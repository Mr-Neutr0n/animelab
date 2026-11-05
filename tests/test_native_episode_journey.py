"""The selected native APK must survive details, batch enqueue and stream resolution."""
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from animelab.services.android_extensions import AndroidAPKSource
from animelab.services.extension_service import extension_service
from animelab.services.download_manager import download_manager
from run import app


def source():
    return AndroidAPKSource({'pkg': 'fixture.voiranime'}, {
        'id': '1152921504606846977', 'name': 'Voiranime', 'baseUrl': 'https://example.com', 'lang': 'fr'})


@pytest.mark.asyncio
@pytest.mark.parametrize('suffix,expected', [(' (VF)', 'VF'), (' VOSTFR', 'VOSTFR'), ('', '')])
async def test_native_detail_keeps_voice_version_and_studio(suffix, expected):
    apk = source()
    apk.call = AsyncMock(return_value={'anime': {'url': '/anime', 'title': 'Series'+suffix, 'author': 'Studio'},
        'episodes': [{'url': '/episode/1', 'name': 'Episode 1', 'episode_number': 1}]})
    detail = await apk.get_anime_detail('https://example.com/anime')
    assert detail.version == expected and detail.episodes[0].version == expected
    assert detail.studio == 'Studio'
    assert detail.episodes[0].playerUrl == 'https://example.com/episode/1'


def test_batch_native_apk_does_not_require_a_desktop_recipe(monkeypatch):
    apk = source()
    monkeypatch.setattr(extension_service, 'get_container_source_by_id', lambda sid: apk)
    calls = []
    monkeypatch.setattr(download_manager, 'start_batch_download', lambda *args, **kwargs: calls.append((args, kwargs)) or [SimpleNamespace(id=1)])
    with TestClient(app) as client:
        result = client.post('/api/download/batch', json={'animeName': 'Series', 'source': apk.source_id,
            'episodes': [{'number': 1, 'url': 'https://example.com/episode/1', 'version': 'VF'}]})
    assert result.status_code == 200, result.text
    assert result.json()['count'] == 1
    assert calls[0][1]['source'] == apk.source_id
    assert calls[0][0][1][0]['source'] == apk.source_id


@pytest.mark.asyncio
async def test_native_video_fallback_keeps_candidates_sharing_a_url(monkeypatch):
    apk = source()
    candidates = [{'url': 'https://example.com/shared', 'server': 'Host', 'quality': q, '_native_video': {'quality': q}} for q in ('1080p', '480p')]
    apk.get_episode_sources = AsyncMock(return_value=candidates)
    async def resolve(candidate):
        if candidate['quality'] == '1080p':
            raise ValueError('Unavailable quality')
        return {'videoUrl': 'https://example.com/final.mp4', 'serverType': 'Host', 'selectedQuality': '480p', 'headers': {'Referer': 'https://example.com/'}, 'size': 123}
    apk.resolve_candidate = AsyncMock(side_effect=resolve)
    monkeypatch.setattr(extension_service, 'get_container_source_by_id', lambda sid: apk)
    monkeypatch.setattr(download_manager, 'get_remote_file_size', AsyncMock(return_value=123))
    url = 'https://example.com/episode/native-shared-candidates'
    result = await download_manager.get_or_resolve_episode_info(url, source=apk.source_id)
    assert result and result.direct_url == 'https://example.com/final.mp4'
    assert apk.resolve_candidate.call_count == 2
    assert result.selected_quality == '480p'


@pytest.mark.asyncio
async def test_native_stream_and_download_honor_requested_quality_and_headers(monkeypatch):
    apk = source()
    candidates = [{'url': 'https://example.com/shared', 'server': 'Host', 'quality': q, '_native_video': {'quality': q}} for q in ('1080p', '480p')]
    apk.get_episode_sources = AsyncMock(return_value=candidates)
    headers = {'Referer': 'https://example.com/episode', 'User-Agent': 'Actual source UA'}
    apk.resolve_candidate = AsyncMock(side_effect=lambda candidate: {
        'videoUrl': 'https://example.com/480.mp4', 'headers': headers, 'serverType': 'Host',
        'selectedQuality': candidate['quality'], 'subtitles': [], 'audioTracks': []})
    monkeypatch.setattr(extension_service, 'get_container_source_by_id', lambda sid: apk)
    monkeypatch.setattr(download_manager, 'get_remote_file_size', AsyncMock(return_value=123))
    url = 'https://example.com/episode/quality-request'
    result = await download_manager.get_or_resolve_episode_info(url, source=apk.source_id, preferred_server='Host', preferred_quality='480p')
    assert result.selected_quality == '480p'
    assert apk.resolve_candidate.call_args.args[0] is candidates[1]
    assert download_manager.get_remote_file_size.call_args.kwargs['headers'] == headers
    apk.resolve_candidate.reset_mock()
    with TestClient(app) as client:
        response = client.get('/api/media/stream/resolve', params={'animeName': 'Series', 'episodeNumber': 1,
            'episodeUrl': url, 'source': apk.source_id, 'server': 'Host', 'quality': '480p'})
    assert response.status_code == 200, response.text
    assert response.json()['selectedQuality'] == '480p'
    assert apk.resolve_candidate.call_args.args[0] is candidates[1]


@pytest.mark.asyncio
async def test_embed_can_be_resolved_without_a_container_or_uninitialized_target(monkeypatch):
    monkeypatch.setattr(extension_service, 'get_container_source_by_id', lambda sid: None)
    monkeypatch.setattr(extension_service, 'get_enabled_container_sources', lambda: [])
    resolved = AsyncMock(return_value={'videoUrl': 'https://example.com/final.mp4', 'serverType': 'Host', 'size': 123})
    monkeypatch.setattr(download_manager, 'resolve_imported_video_stream', resolved)
    result = await download_manager.get_or_resolve_episode_info('https://example.com/standalone-embed', source='fixture.embed')
    assert result and result.direct_url.endswith('/final.mp4')
    resolved.assert_awaited_once()


@pytest.mark.asyncio
async def test_episode_info_expands_recipe_players_on_a_known_embed(monkeypatch):
    url = 'https://video.sibnet.ru/shell.php?videoid=123#players=fixture-alternatives'
    alternative = 'https://video.fixture.invalid/working.mp4'
    recipe = SimpleNamespace(runtime='recipe', name='Recipe',
        get_episode_sources=AsyncMock(return_value=[{'url': alternative, 'server': 'Alternative'}]))
    monkeypatch.setattr(extension_service, 'get_container_source_by_id', lambda sid: recipe)
    resolved = AsyncMock(return_value={'videoUrl': alternative, 'serverType': 'Alternative', 'size': 123})
    monkeypatch.setattr(download_manager, 'resolve_imported_video_stream', resolved)
    monkeypatch.setattr(download_manager, 'get_remote_file_size', AsyncMock(return_value=123))
    result = await download_manager.get_or_resolve_episode_info(url, source='fixture.recipe.players')
    assert result and result.direct_url == alternative
    recipe.get_episode_sources.assert_awaited_once_with(url)
    resolved.assert_awaited_once_with(alternative, referer=url, preferred_quality=None)
