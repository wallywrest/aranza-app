from pathlib import Path
import xml.etree.ElementTree as ET

MANIFEST = Path(__file__).parent / 'android-template/app/src/main/AndroidManifest.xml'
ANDROID = '{http://schemas.android.com/apk/res/android}'


def test_android_manifest_declares_only_minimum_permissions():
    root = ET.parse(MANIFEST).getroot()
    permissions = {node.attrib[ANDROID + 'name'] for node in root.findall('uses-permission')}
    assert permissions == {
        'android.permission.INTERNET',
        'android.permission.CAMERA',
        'android.permission.RECORD_AUDIO',
    }


def test_camera_and_microphone_are_optional_and_cleartext_is_disabled():
    root = ET.parse(MANIFEST).getroot()
    features = {node.attrib[ANDROID + 'name']: node.attrib[ANDROID + 'required']
                for node in root.findall('uses-feature')}
    assert features == {
        'android.hardware.camera': 'false',
        'android.hardware.microphone': 'false',
    }
    app = root.find('application')
    assert app.attrib[ANDROID + 'usesCleartextTraffic'] == 'false'
    assert app.attrib[ANDROID + 'allowBackup'] == 'false'
