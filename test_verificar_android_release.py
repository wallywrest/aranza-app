import shutil
from pathlib import Path
from verificar_android_release import auditar


def test_current_android_scaffold_passes_static_audit():
    results = auditar()
    assert len(results) == 7
    assert all(item['ok'] for item in results), results


def test_audit_detects_cleartext_and_backup_regression(tmp_path):
    root = Path(__file__).resolve().parent
    shutil.copytree(root / 'android-template', tmp_path / 'android-template')
    shutil.copy(root / 'package.json', tmp_path / 'package.json')
    shutil.copy(root / 'capacitor.config.ts', tmp_path / 'capacitor.config.ts')
    manifest = tmp_path / 'android-template/app/src/main/AndroidManifest.xml'
    content = manifest.read_text(encoding='utf-8').replace('android:allowBackup="false"', 'android:allowBackup="true"').replace('android:usesCleartextTraffic="false"', 'android:usesCleartextTraffic="true"')
    manifest.write_text(content, encoding='utf-8')
    results = {item['name']: item for item in auditar(tmp_path)}
    assert not results['BACKUP_DISABLED']['ok']
    assert not results['CLEARTEXT_DISABLED']['ok']


def test_audit_detects_unexpected_permission(tmp_path):
    root = Path(__file__).resolve().parent
    shutil.copytree(root / 'android-template', tmp_path / 'android-template')
    shutil.copy(root / 'package.json', tmp_path / 'package.json')
    shutil.copy(root / 'capacitor.config.ts', tmp_path / 'capacitor.config.ts')
    manifest = tmp_path / 'android-template/app/src/main/AndroidManifest.xml'
    content = manifest.read_text(encoding='utf-8').replace('<application', '<uses-permission android:name="android.permission.READ_CONTACTS" />\n    <application')
    manifest.write_text(content, encoding='utf-8')
    results = {item['name']: item for item in auditar(tmp_path)}
    assert not results['PERMISSIONS_MINIMAL']['ok']
