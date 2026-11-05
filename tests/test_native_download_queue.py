"""Exercise the real queue resolver, HTTP transfer and media verification together."""
import json
import shutil
import subprocess
from pathlib import Path
from unittest.mock import AsyncMock
from types import SimpleNamespace

import httpx
import pytest

from animelab import platform_events
from animelab.models.download_task import DownloadTask, DownloadStatus
from animelab.services.android_extensions import AndroidAPKSource
from animelab.services.download_manager import DownloadManagerService
from animelab.services.extension_service import extension_service
from animelab.services.library_service import library_service


@pytest.mark.asyncio
@pytest.mark.parametrize("episode_number", [0, 7])
async def test_native_queue_preserves_episode_fragment_and_uses_apk_resolution_and_headers(tmp_path, monkeypatch, episode_number):
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        pytest.skip('Real FFmpeg/FFprobe required')
    source_file = tmp_path/'reference.mp4'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-f','lavfi','-i','testsrc2=s=64x64:r=10',
                    '-t','1','-c:v','libx264','-threads','1','-pix_fmt','yuv420p',str(source_file)],check=True,timeout=20)
    payload = source_file.read_bytes()
    episode_url = f'https://source.fixture.invalid/season/#episode={episode_number}'
    video_url = 'https://video.fixture.invalid/episode.mp4'
    headers = {'Referer':'https://source.fixture.invalid/', 'User-Agent':'Actual source UA', 'X-Source-Proof':'fixture'}
    apk = AndroidAPKSource({'pkg':'fixture.native'}, {'id':'1152921504606846977','name':'Native','baseUrl':'https://source.fixture.invalid','lang':'fr'})
    apk._episodes[episode_url] = {'url':f'/season/#episode={episode_number}','name':f'Episode {episode_number}','memo':{'selection':'native-state'}}
    native_calls = []
    async def invoke(operation, value):
        native_calls.append(operation)
        if operation == 'hosters':
            assert value['url'] == f'/season/#episode={episode_number}'
            assert value['memo']['selection'] == 'native-state'
            return [{'hosterName':'Native host', 'videoList':[{'videoUrl':'native://opaque', 'videoTitle':'480p', 'memo':{'video':state}} for state in ('unavailable', 'native-state')]}]
        assert operation == 'resolve_video'
        if value['memo']['video'] == 'unavailable': raise ValueError('Synthetic unavailable rendition')
        assert value['memo']['video'] == 'native-state'
        return {'videoUrl':video_url, 'videoTitle':'480p', 'headers':list(headers.items()), 'subtitleTracks':[], 'audioTracks':[]}
    apk.call = invoke
    monkeypatch.setattr(extension_service,'get_container_source_by_id',lambda sid: apk if sid == apk.source_id else None)
    monkeypatch.setattr('animelab.security.is_safe_url',lambda url,**kwargs: url == video_url)
    monkeypatch.setattr('animelab.media_policy.is_safe_url',lambda url,**kwargs: url == video_url)
    manager = DownloadManagerService()
    monkeypatch.setattr(manager,'broadcast_update',lambda task:None)
    monkeypatch.setattr(manager,'_trigger_process_queue',lambda:None)
    monkeypatch.setattr(library_service,'save_task',lambda task:None)
    monkeypatch.setattr(library_service,'mark_as_downloaded',lambda *args,**kwargs:None)
    monkeypatch.setattr(platform_events,'completed_handler',None)
    generic = AsyncMock(side_effect=AssertionError('A native video must be resolved by its original APK'))
    monkeypatch.setattr(manager,'resolve_imported_video_stream',generic)
    requests=[]
    def respond(request):
        assert str(request.url) == video_url
        for key,value in headers.items(): assert request.headers[key] == value
        requests.append(request)
        return httpx.Response(200,content=payload,headers={'Content-Type':'video/mp4','Content-Length':str(len(payload)),'ETag':'"fixture"'})
    monkeypatch.setattr(manager,'_create_async_client',lambda **kwargs:httpx.AsyncClient(transport=httpx.MockTransport(respond),headers=kwargs.get('headers')))
    destination=tmp_path/'downloads'/'episode.mp4';destination.parent.mkdir()
    task=DownloadTask(animeName='Native series',episodeNumber=episode_number,fileUrl=episode_url,source=apk.source_id,
                      savePath=str(destination),fileName=destination.name,selectedQuality='480p')
    manager.tasks[task.id]=task
    try:
        await manager._execute_download(task)
        assert task.status == DownloadStatus.COMPLETED, task.error
        assert task.verificationStatus == 'VALID'
        assert destination.read_bytes() == payload
        assert task.downloadedBytes == len(payload)
        assert len(requests) == 1 and native_calls == ['hosters','resolve_video','resolve_video']
        generic.assert_not_awaited()
        assert task.requestHeaders == headers
        assert json.loads(task.mediaJson)['transferAttempt']['status'] == 'completed'
        assert list(destination.parent.glob('*.mp4')) == [destination]
    finally:
        await manager.shutdown()


@pytest.mark.asyncio
async def test_desktop_recipe_receives_its_complete_episode_fragment(monkeypatch):
    from animelab.services.source_resolvers import SourceResolverRegistry
    url = 'https://source.fixture.invalid/season/#animelab-episode=2'
    video = 'https://video.fixture.invalid/episode.mp4'
    service = SimpleNamespace(runtime='recipe', get_episode_sources=AsyncMock(return_value=[{'url':video,'quality':'HD'}]))
    monkeypatch.setattr(extension_service,'get_container_source_by_id',lambda source:service)
    monkeypatch.setattr('animelab.media_policy.is_safe_url',lambda target,**kwargs: target == video)
    ctx = SimpleNamespace(_needs_scraping_resolution=lambda target:False,
        resolve_imported_video_stream=AsyncMock(return_value={'videoUrl':video}),
        _update_resolved_subtitles=lambda *args:None)
    task = DownloadTask(fileUrl=url,source='fixture.recipe')
    media = await SourceResolverRegistry().resolve(ctx,task,need_resolve=True,skip_local=False)
    service.get_episode_sources.assert_awaited_once_with(url)
    assert media.url == video
