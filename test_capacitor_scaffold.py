import json
from pathlib import Path

BASE = Path(__file__).parent


def test_capacitor_package_has_android_workflow():
    package = json.loads((BASE / 'package.json').read_text(encoding='utf-8'))
    assert package['version'] == '1.80.0'
    assert 'cap:add:android' in package['scripts']
    assert '@capacitor/android' in package['devDependencies']


def test_capacitor_config_is_present_and_uses_local_web_root():
    config = (BASE / 'capacitor.config.ts').read_text(encoding='utf-8')
    assert "appId: 'com.aranza.ai'" in config
    assert "appName: 'Aranza AI'" in config
    assert "webDir: '.'" in config
    assert 'allowMixedContent: false' in config


def test_android_guide_does_not_claim_apk_exists():
    guide = (BASE / 'ANDROID_CAPACITOR_V1_80.md').read_text(encoding='utf-8')
    assert 'no contiene un APK' in guide
    assert 'ARANZA_API_BASE' in guide
    assert 'ARANZA_ALLOWED_ORIGINS' in guide
