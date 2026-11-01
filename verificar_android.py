#!/usr/bin/env python3
"""Preflight local para preparar el cliente Capacitor sin exponer secretos."""
from __future__ import annotations
import os
from urllib.parse import urlparse


def revisar_android(env=None):
    env = os.environ if env is None else env
    api = str(env.get('ARANZA_API_BASE', '')).strip().rstrip('/')
    origins = [x.strip() for x in str(env.get('ARANZA_ALLOWED_ORIGINS', '')).split(',') if x.strip()]
    parsed_api = urlparse(api)
    api_ok = parsed_api.scheme == 'https' and bool(parsed_api.netloc) and not parsed_api.username and not parsed_api.password and not parsed_api.query and not parsed_api.fragment
    parsed_origins = [urlparse(x) for x in origins]
    origins_ok = bool(origins) and len(origins) == len(set(origins)) and all(p.scheme == 'https' and p.netloc and not p.path and not p.query and not p.fragment and not p.username and not p.password for p in parsed_origins)
    return [
        {'name': 'ARANZA_API_BASE', 'ok': api_ok, 'detail': 'URL HTTPS válida para el backend.' if api_ok else 'Define ARANZA_API_BASE con la URL HTTPS del backend, sin credenciales, query ni fragmento.'},
        {'name': 'ARANZA_ALLOWED_ORIGINS', 'ok': origins_ok, 'detail': 'Orígenes HTTPS explícitos y únicos.' if origins_ok else 'Incluye el origen exacto de la app y del sitio web; no uses * ni rutas.'},
        {'name': 'CLIENT_SECRETS', 'ok': True, 'detail': 'No se inspeccionan ni se incrustan claves de proveedor en el cliente. Manténlas solo en el servidor.'},
    ]


def main():
    results = revisar_android()
    for item in results:
        print(f"[{'OK' if item['ok'] else 'ERROR'}] {item['name']}: {item['detail']}")
    failed = sum(not x['ok'] for x in results)
    print(f'\nResultado: {len(results)-failed}/{len(results)} comprobaciones aprobadas.')
    print('Este preflight no compila APK, no prueba el dispositivo y no verifica conectividad real.')
    return 1 if failed else 0

if __name__ == '__main__':
    raise SystemExit(main())
