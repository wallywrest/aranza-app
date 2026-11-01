#!/usr/bin/env python3
"""Auditoría estática de preparación Android; no sustituye pruebas en dispositivo."""
from __future__ import annotations
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ANDROID_NS = '{http://schemas.android.com/apk/res/android}'
ALLOWED_PERMISSIONS = {
    'android.permission.INTERNET',
    'android.permission.CAMERA',
    'android.permission.RECORD_AUDIO',
}


def auditar(root: Path = ROOT):
    checks = []
    def add(name, ok, detail):
        checks.append({'name': name, 'ok': bool(ok), 'detail': detail})

    package_file = root / 'package.json'
    config_file = root / 'capacitor.config.ts'
    manifest_file = root / 'android-template/app/src/main/AndroidManifest.xml'
    try:
        package = json.loads(package_file.read_text(encoding='utf-8'))
        add('PACKAGE_JSON', isinstance(package, dict) and package.get('private') is True,
            'package.json válido y privado.' if package.get('private') is True else 'Falta private=true o package.json válido.')
    except Exception:
        package = {}
        add('PACKAGE_JSON', False, 'No se pudo leer package.json.')

    try:
        config = config_file.read_text(encoding='utf-8')
        app_id = re.search(r"appId:\s*'([^']+)'", config)
        app_name = re.search(r"appName:\s*'([^']+)'", config)
        add('CAPACITOR_ID', bool(app_id and re.fullmatch(r'[a-zA-Z][\w]*(?:\.[a-zA-Z][\w]*)+', app_id.group(1))),
            'Identificador de aplicación válido.' if app_id else 'No se encontró appId.')
        add('CAPACITOR_NAME', bool(app_name and app_name.group(1).strip()), 'Nombre de aplicación configurado.' if app_name else 'No se encontró appName.')
        add('WEBVIEW_SECURITY', 'allowMixedContent: false' in config and 'webContentsDebuggingEnabled: false' in config,
            'Contenido mixto y depuración WebView deshabilitados.' if 'allowMixedContent: false' in config and 'webContentsDebuggingEnabled: false' in config else 'Revisa mixed content y depuración WebView.')
    except Exception:
        add('CAPACITOR_CONFIG', False, 'No se pudo leer capacitor.config.ts.')

    try:
        tree = ET.parse(manifest_file)
        app = tree.getroot().find('application')
        permissions = {node.attrib.get(ANDROID_NS + 'name') for node in tree.getroot().findall('uses-permission')}
        unexpected = sorted(x for x in permissions if x not in ALLOWED_PERMISSIONS)
        add('PERMISSIONS_MINIMAL', not unexpected, 'Permisos dentro de la lista mínima.' if not unexpected else 'Permisos inesperados: ' + ', '.join(unexpected))
        add('BACKUP_DISABLED', app is not None and app.attrib.get(ANDROID_NS + 'allowBackup') == 'false', 'Copia automática deshabilitada.' if app is not None and app.attrib.get(ANDROID_NS + 'allowBackup') == 'false' else 'allowBackup debe ser false.')
        add('CLEARTEXT_DISABLED', app is not None and app.attrib.get(ANDROID_NS + 'usesCleartextTraffic') == 'false', 'Tráfico HTTP sin cifrar deshabilitado.' if app is not None and app.attrib.get(ANDROID_NS + 'usesCleartextTraffic') == 'false' else 'usesCleartextTraffic debe ser false.')
    except Exception:
        add('ANDROID_MANIFEST', False, 'No se pudo analizar la plantilla AndroidManifest.xml.')
    return checks


def main():
    results = auditar()
    for item in results:
        print(f"[{'OK' if item['ok'] else 'REVISAR'}] {item['name']}: {item['detail']}")
    failed = sum(not item['ok'] for item in results)
    print(f'\nResultado: {len(results)-failed}/{len(results)} comprobaciones aprobadas.')
    print('Auditoría estática únicamente: no compila APK ni valida plugins, Merged Manifest, firma o dispositivo real.')
    return 1 if failed else 0

if __name__ == '__main__':
    raise SystemExit(main())
