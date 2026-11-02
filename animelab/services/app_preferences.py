"""Installation/account preferences, independent of WebView origins and ports."""
import json
from animelab.database import sqlite_connection

DEFAULTS = {'onboardingCompleted': False, 'theme': None, 'palette': None,
            'checkUpdates': True, 'updateChannel': 'beta', 'downloadDirectory': None, 'lastSeenVersion': None}


def load():
    with sqlite_connection() as conn:
        row = conn.execute("SELECT value FROM app_preferences WHERE key='startup'").fetchone()
    return {**DEFAULTS, **(json.loads(row['value']) if row else {})}


def save(changes):
    # Read/merge/write under the same write lock: completing setup must not
    # overwrite a concurrent update-channel or appearance change.
    with sqlite_connection() as conn:
        conn.execute('BEGIN IMMEDIATE')
        row = conn.execute("SELECT value FROM app_preferences WHERE key='startup'").fetchone()
        values = {**DEFAULTS, **(json.loads(row['value']) if row else {}), **changes}
        conn.execute("INSERT INTO app_preferences(key,value) VALUES('startup',?) "
                     'ON CONFLICT(key) DO UPDATE SET value=excluded.value', (json.dumps(values),))
    return values


def restore_download_directory():
    from animelab.config import settings, IS_ANDROID
    from animelab.environment import getenv
    if IS_ANDROID or getenv('ANIMELAB_SHARED_WORKER') == '1':
        return
    # An explicit operator/launcher override always wins over a saved choice.
    directory = load()['downloadDirectory']
    current_override = getenv('ANIMELAB_DOWNLOAD_DIR')
    if directory and (not current_override or current_override == load().get('downloadDirectoryOrigin')):
        from animelab.services.download_manager import download_manager
        settings.DOWNLOAD_DIR = download_manager.download_dir = directory
