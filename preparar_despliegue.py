#!/usr/bin/env python3
"""Revisa variables críticas antes de desplegar Aranza; no cambia archivos ni servicios."""
from __future__ import annotations
import os
import sys
from urllib.parse import urlparse


def revisar(env=None):
    env = os.environ if env is None else env
    checks = []

    def add(name, ok, detail, severity="ERROR"):
        checks.append({"name": name, "ok": bool(ok), "detail": detail, "severity": severity})

    password = str(env.get("ARANZA_PASSWORD", ""))
    secret = str(env.get("ARANZA_SESSION_SECRET", ""))
    origins = [x.strip() for x in str(env.get("ARANZA_ALLOWED_ORIGINS", "")).split(",") if x.strip()]
    db_path = str(env.get("ARANZA_DB_PATH", "aranza.sqlite3"))
    add("ARANZA_PASSWORD", len(password) >= 12, "Definida con al menos 12 caracteres." if len(password) >= 12 else "Configura una contraseña de al menos 12 caracteres.")
    secret_ok = len(secret) >= 32 and secret != password and secret.lower() not in {"change-me", "changeme", "secret", "your-secret-key"}
    add("ARANZA_SESSION_SECRET", secret_ok, "Clave persistente de 32+ caracteres y distinta de la contraseña." if secret_ok else "Configura una clave aleatoria persistente de al menos 32 caracteres, distinta de la contraseña y de valores de ejemplo.")
    parsed_origins = [urlparse(x) for x in origins]
    origins_valid = bool(origins) and len(set(origins)) == len(origins) and all(u.scheme == "https" and u.netloc and not u.path and not u.params and not u.query and not u.fragment for u in parsed_origins)
    add("ARANZA_ALLOWED_ORIGINS", origins_valid, "Orígenes HTTPS únicos y sin rutas." if origins_valid else "Indica orígenes HTTPS exactos y únicos, solo esquema + dominio; no uses *, rutas, parámetros ni localhost en producción.")
    db = __import__("pathlib").Path(db_path).expanduser()
    absolute_db = db.is_absolute()
    persistent_mount = absolute_db and (str(db) == "/var/data" or str(db).startswith("/var/data/"))
    add(
        "ARANZA_DB_PATH",
        persistent_mount,
        "La base de datos apunta al disco persistente de Render (/var/data)."
        if persistent_mount else
        "Para el despliegue Render recomendado, configura ARANZA_DB_PATH dentro de /var/data (por ejemplo /var/data/aranza.sqlite3); una ruta relativa o fuera del disco puede perder datos al redeplegar."
    )
    username = str(env.get("ARANZA_USERNAME", "owner")).strip()
    add("ARANZA_USERNAME", bool(username) and username.lower() not in {"admin", "root", "user", "owner"}, "Nombre de cuenta personalizado." if username and username.lower() not in {"admin", "root", "user", "owner"} else "Cambia el nombre predeterminado por uno propio antes de publicar.", "WARNING")
    provider = bool(str(env.get("GROQ_API_KEY", "")).strip())
    add("GROQ_API_KEY", provider, "Clave de proveedor presente." if provider else "No hay proveedor configurado: la app puede arrancar, pero las respuestas con modelo externo no funcionarán.", "ERROR" if not provider else "INFO")
    return checks


def main():
    checks = revisar()
    for item in checks:
        status = "OK" if item["ok"] else item["severity"]
        print(f"[{status}] {item['name']}: {item['detail']}")
    failures = [x for x in checks if not x["ok"] and x["severity"] == "ERROR"]
    print(f"\nResultado: {len(checks) - len(failures)}/{len(checks)} comprobaciones críticas aprobadas.")
    print("Esta revisión no despliega la app ni verifica almacenamiento persistente, DNS o disponibilidad del proveedor.")
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main())
