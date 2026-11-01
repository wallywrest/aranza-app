"""Copias verificadas y restauración segura de la base SQLite de Aranza.

Uso:
  python backup_db.py backup
  python backup_db.py backup --output-dir ./respaldos
  python backup_db.py restore --source ./respaldos/aranza_....sqlite3 --confirm

La restauración debe hacerse con el servicio detenido para evitar escrituras
simultáneas. Nunca se elimina la base actual: se crea un respaldo previo.
"""
import argparse
import hashlib
import json
import os
import sqlite3
import tempfile
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
_raw_db_path = Path(os.getenv("ARANZA_DB_PATH", str(BASE_DIR / "aranza.sqlite3")))
DB_PATH = _raw_db_path if _raw_db_path.is_absolute() else (BASE_DIR / _raw_db_path).resolve()


def integrity_check(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"No existe la base de datos: {path}")
    with sqlite3.connect(str(path), timeout=10) as conn:
        result = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise sqlite3.DatabaseError(f"La comprobación de integridad falló: {result}")


def inspect_database(source: Path = DB_PATH) -> dict:
    """Valida una base sin modificarla y devuelve metadatos operativos seguros."""
    source = Path(source).resolve()
    integrity_check(source)
    with sqlite3.connect(str(source), timeout=10) as conn:
        journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        tables = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchone()[0]
        page_count = conn.execute("PRAGMA page_count").fetchone()[0]
        page_size = conn.execute("PRAGMA page_size").fetchone()[0]
    return {
        "path": str(source),
        "integrity": "ok",
        "journal_mode": str(journal_mode),
        "table_count": int(tables),
        "size_bytes": int(source.stat().st_size),
        "logical_size_bytes": int(page_count * page_size),
    }


def diagnose_database(source: Path = DB_PATH) -> dict:
    """Diagnóstico no destructivo para distinguir ausencia, corrupción y permisos."""
    source = Path(source).resolve()
    parent = source.parent
    report = {
        "path": str(source),
        "exists": source.is_file(),
        "parent_exists": parent.is_dir(),
        "parent_writable": bool(parent.is_dir() and os.access(parent, os.W_OK)),
        "wal_present": Path(str(source) + "-wal").exists(),
        "shm_present": Path(str(source) + "-shm").exists(),
        "integrity": "not_checked",
        "error": None,
    }
    if not report["exists"]:
        report["integrity"] = "missing"
        report["error"] = "No existe el archivo de base de datos. No se creó ni modificó nada."
        return report
    try:
        integrity_check(source)
        report["integrity"] = "ok"
    except (OSError, sqlite3.Error) as exc:
        report["integrity"] = "error"
        report["error"] = str(exc)
    return report


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_backup_manifest(backup: Path, source: Path) -> Path:
    """Escribe metadatos de trazabilidad mediante reemplazo atómico."""
    info = inspect_database(backup)
    manifest = {
        "format_version": 1,
        "backup_file": backup.name,
        "source_path": str(source),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "size_bytes": int(backup.stat().st_size),
        "sha256": _sha256_file(backup),
        "integrity": info["integrity"],
        "table_count": info["table_count"],
    }
    target = Path(str(backup) + ".json")
    fd, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent))
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(manifest, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    return target


def verify_backup_manifest(source: Path) -> dict:
    """Verifica el manifiesto y checksum si existe; permite respaldos heredados sin manifiesto."""
    source = Path(source).resolve()
    integrity_check(source)
    manifest_path = Path(str(source) + ".json")
    if not manifest_path.exists():
        return {"status": "missing", "manifest_path": str(manifest_path), "checksum_verified": None}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"No se pudo leer el manifiesto del respaldo: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValueError("El manifiesto del respaldo debe contener un objeto JSON.")
    if manifest.get("format_version") != 1 or manifest.get("backup_file") != source.name:
        raise ValueError("El manifiesto no corresponde a este respaldo o usa una versión desconocida.")
    actual_size = int(source.stat().st_size)
    actual_hash = _sha256_file(source)
    if manifest.get("size_bytes") != actual_size or manifest.get("sha256") != actual_hash:
        raise ValueError("El tamaño o SHA-256 del respaldo no coincide con su manifiesto.")
    if manifest.get("integrity") != "ok":
        raise ValueError("El manifiesto no registra integridad correcta.")
    return {"status": "ok", "manifest_path": str(manifest_path), "checksum_verified": True}


def backup_database(source: Path = DB_PATH, output_dir: Path | None = None) -> Path:
    source = Path(source).resolve()
    integrity_check(source)
    destination_dir = Path(output_dir or (source.parent / "backups")).resolve()
    destination_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destination = destination_dir / f"aranza_{stamp}.sqlite3"
    # SQLite backup API incluye correctamente las páginas confirmadas incluso
    # cuando la base usa WAL; copiar el archivo a mano no ofrece esa garantía.
    with sqlite3.connect(str(source), timeout=10) as src, sqlite3.connect(str(destination), timeout=10) as dst:
        src.backup(dst)
    integrity_check(destination)
    _write_backup_manifest(destination, source)
    return destination


def verify_restore(source: Path) -> dict:
    """Ensaya una restauración en un SQLite temporal sin tocar la base activa."""
    source = Path(source).resolve()
    manifest_report = verify_backup_manifest(source)
    source_info = inspect_database(source)
    with tempfile.TemporaryDirectory(prefix="aranza-verify-restore-") as temp_dir:
        isolated = Path(temp_dir) / "restore_test.sqlite3"
        with sqlite3.connect(str(source), timeout=10) as src, sqlite3.connect(str(isolated), timeout=10) as dst:
            src.backup(dst)
        restored_info = inspect_database(isolated)
        with sqlite3.connect(str(source), timeout=10) as src, sqlite3.connect(str(isolated), timeout=10) as restored:
            source_tables = src.execute(
                "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            ).fetchall()
            restored_tables = restored.execute(
                "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            ).fetchall()
        if source_tables != restored_tables:
            raise sqlite3.DatabaseError("La restauración aislada no coincide con el esquema de origen.")
        if source_info["table_count"] != restored_info["table_count"]:
            raise sqlite3.DatabaseError("La cantidad de tablas cambió durante la restauración aislada.")
        return {
            "status": "ok",
            "source": str(source),
            "source_integrity": source_info["integrity"],
            "manifest_status": manifest_report["status"],
            "checksum_verified": manifest_report["checksum_verified"],
            "restored_integrity": restored_info["integrity"],
            "table_count": restored_info["table_count"],
            "source_size_bytes": source_info["size_bytes"],
            "isolated_restore_size_bytes": restored_info["size_bytes"],
            "active_database_touched": False,
            "backup_modified": False,
            "temporary_restore_removed": True,
        }


def restore_database(source: Path, destination: Path = DB_PATH) -> Path:
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    verify_backup_manifest(source)
    integrity_check(source)
    if source == destination:
        raise ValueError("El respaldo de origen no puede ser la base de destino.")
    destination.parent.mkdir(parents=True, exist_ok=True)

    # Salvaguarda antes de tocar el archivo actual.
    if destination.exists():
        safety_copy = backup_database(destination, destination.parent / "backups_pre_restore")
    else:
        safety_copy = None

    # Preparar la restauración en un archivo temporal del mismo directorio:
    # solo reemplazar el destino después de validar la copia restaurada.
    # Esto evita dejar una base parcialmente escrita si la operación falla.
    temp_path: Path | None = None
    try:
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{destination.name}.", suffix=".restore.tmp", dir=str(destination.parent)
        )
        os.close(fd)
        temp_path = Path(temp_name)
        with sqlite3.connect(str(source), timeout=10) as src, sqlite3.connect(str(temp_path), timeout=10) as dst:
            src.backup(dst)
        integrity_check(temp_path)
        # Aparta los sidecars de la base anterior antes de sustituirla. Si el
        # reemplazo falla, se restauran para no dejar la base antigua sin sus
        # archivos auxiliares. El servicio debe estar detenido durante restore.
        staged_sidecars: list[tuple[Path, Path]] = []
        try:
            for suffix in ("-wal", "-shm"):
                sidecar = Path(str(destination) + suffix)
                if sidecar.exists():
                    staged = sidecar.with_name(sidecar.name + ".pre-restore")
                    if staged.exists():
                        raise FileExistsError(f"Existe un sidecar temporal de restauración: {staged}")
                    os.replace(sidecar, staged)
                    staged_sidecars.append((sidecar, staged))
            os.replace(temp_path, destination)
            temp_path = None
        except Exception:
            for original, staged in reversed(staged_sidecars):
                if staged.exists() and not original.exists():
                    try:
                        os.replace(staged, original)
                    except OSError:
                        # Mantiene el sidecar staged para recuperación manual.
                        pass
            raise
        else:
            for _, staged in staged_sidecars:
                staged.unlink(missing_ok=True)
        integrity_check(destination)
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
    return safety_copy



def audit_backups(directory: Path, max_age_days: float = 7.0, now: datetime | None = None) -> dict:
    """Audita respaldos SQLite sin modificarlos ni eliminar archivos.

    Informa validez, antigüedad y si existe al menos un respaldo reciente válido.
    Los archivos no SQLite se ignoran; los archivos SQLite corruptos se reportan.
    """
    directory = Path(directory).resolve()
    if max_age_days < 0:
        raise ValueError("max_age_days no puede ser negativo.")
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    if not directory.is_dir():
        return {
            "directory": str(directory),
            "directory_exists": False,
            "max_age_days": float(max_age_days),
            "backup_count": 0,
            "valid_count": 0,
            "invalid_count": 0,
            "latest_valid": None,
            "latest_valid_age_days": None,
            "has_recent_valid_backup": False,
            "backups": [],
            "error": "El directorio de respaldos no existe.",
        }

    entries = []
    candidates = sorted(
        (item for item in directory.iterdir() if item.is_file() and item.suffix.lower() in {".sqlite3", ".sqlite", ".db"}),
        key=lambda item: item.name.lower(),
    )
    for item in candidates:
        try:
            modified = datetime.fromtimestamp(item.stat().st_mtime, tz=timezone.utc)
            age_days = max(0.0, (current.astimezone(timezone.utc) - modified).total_seconds() / 86400)
            integrity_check(item)
            entry = {"path": str(item), "valid": True, "age_days": round(age_days, 3), "error": None, "modified_at": modified.isoformat(), "manifest_status": "missing", "manifest_path": str(Path(str(item) + ".json")), "checksum_verified": None}
            manifest_path = Path(str(item) + ".json")
            if manifest_path.exists():
                try:
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    if manifest.get("format_version") != 1 or manifest.get("backup_file") != item.name:
                        raise ValueError("El manifiesto no corresponde a este respaldo o usa una versión desconocida.")
                    actual_size = int(item.stat().st_size)
                    actual_hash = _sha256_file(item)
                    if manifest.get("size_bytes") != actual_size or manifest.get("sha256") != actual_hash:
                        raise ValueError("El tamaño o SHA-256 no coincide con el manifiesto.")
                    if manifest.get("integrity") != "ok":
                        raise ValueError("El manifiesto no registra integridad correcta.")
                    entry["manifest_status"] = "ok"
                    entry["checksum_verified"] = True
                    entry["manifest_created_at"] = manifest.get("created_at")
                except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                    entry["manifest_status"] = "invalid"
                    entry["checksum_verified"] = False
                    entry["manifest_error"] = str(exc)
            entries.append(entry)
        except (OSError, sqlite3.Error) as exc:
            try:
                modified = datetime.fromtimestamp(item.stat().st_mtime, tz=timezone.utc)
                age_days = max(0.0, (current.astimezone(timezone.utc) - modified).total_seconds() / 86400)
            except OSError:
                age_days = None
                modified = None
            entries.append({"path": str(item), "valid": False, "age_days": round(age_days, 3) if age_days is not None else None, "error": str(exc), "modified_at": modified.isoformat() if modified else None, "manifest_status": "unchecked", "manifest_path": str(Path(str(item) + ".json")), "checksum_verified": None})

    valid = [entry for entry in entries if entry["valid"] and entry["manifest_status"] != "invalid"]
    manifest_invalid_count = sum(entry["manifest_status"] == "invalid" for entry in entries)
    latest = min(valid, key=lambda entry: entry["age_days"]) if valid else None
    recent = any(entry["age_days"] <= max_age_days for entry in valid)
    return {
        "directory": str(directory),
        "directory_exists": True,
        "max_age_days": float(max_age_days),
        "backup_count": len(entries),
        "valid_count": len(valid),
        "invalid_count": len(entries) - sum(entry["valid"] for entry in entries),
        "manifest_invalid_count": manifest_invalid_count,
        "manifest_verified_count": sum(entry["manifest_status"] == "ok" for entry in entries),
        "legacy_without_manifest_count": sum(entry["manifest_status"] == "missing" for entry in entries),
        "latest_valid": latest["path"] if latest else None,
        "latest_valid_age_days": latest["age_days"] if latest else None,
        "has_recent_valid_backup": recent,
        "backups": entries,
        "error": None if recent else "No existe un respaldo válido dentro de la antigüedad permitida.",
    }


def append_audit_history(history_file: Path, report: dict, now: datetime | None = None) -> Path:
    """Registra una línea JSON por auditoría; no guarda contenido de la base."""
    history_file = Path(history_file).resolve()
    history_file.parent.mkdir(parents=True, exist_ok=True)
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    record = {
        "recorded_at": current.astimezone(timezone.utc).isoformat(),
        "directory": report.get("directory"),
        "directory_exists": bool(report.get("directory_exists")),
        "max_age_days": report.get("max_age_days"),
        "backup_count": int(report.get("backup_count", 0)),
        "valid_count": int(report.get("valid_count", 0)),
        "invalid_count": int(report.get("invalid_count", 0)),
        "manifest_invalid_count": int(report.get("manifest_invalid_count", 0)),
        "manifest_verified_count": int(report.get("manifest_verified_count", 0)),
        "legacy_without_manifest_count": int(report.get("legacy_without_manifest_count", 0)),
        "has_recent_valid_backup": bool(report.get("has_recent_valid_backup")),
        "status": "ok" if report.get("directory_exists") and report.get("has_recent_valid_backup") and not report.get("invalid_count") and not report.get("manifest_invalid_count") else "error",
        "error": report.get("error"),
    }
    # Una línea por ejecución facilita leer el historial de forma incremental.
    with history_file.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    return history_file



def evaluate_backup_policy(
    history_file: Path,
    max_consecutive_failures: int = 2,
    max_record_age_hours: float = 24.0,
    now: datetime | None = None,
) -> dict:
    """Evalúa el historial de auditorías y devuelve alertas sin modificarlo."""
    history_file = Path(history_file)
    if max_consecutive_failures < 1:
        raise ValueError("max_consecutive_failures debe ser al menos 1.")
    if max_record_age_hours < 0:
        raise ValueError("max_record_age_hours no puede ser negativo.")
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    alerts: list[dict] = []
    records: list[dict] = []
    if not history_file.is_file():
        alerts.append({"level": "critical", "code": "history_missing", "message": "No existe el archivo de historial de auditorías."})
    else:
        try:
            for line_number, line in enumerate(history_file.read_text(encoding="utf-8").splitlines(), start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    if not isinstance(record, dict) or record.get("status") not in {"ok", "error"}:
                        raise ValueError("registro sin estado válido")
                    stamp = datetime.fromisoformat(str(record["recorded_at"]).replace("Z", "+00:00"))
                    if stamp.tzinfo is None:
                        raise ValueError("fecha sin zona horaria")
                    record["_parsed_at"] = stamp.astimezone(timezone.utc)
                    records.append(record)
                except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                    alerts.append({"level": "warning", "code": "history_record_invalid", "message": f"Registro inválido en línea {line_number}: {exc}"})
        except OSError as exc:
            alerts.append({"level": "critical", "code": "history_unreadable", "message": f"No se pudo leer el historial: {exc}"})

    if records:
        latest = max(records, key=lambda item: item["_parsed_at"])
        age_hours = max(0.0, (current.astimezone(timezone.utc) - latest["_parsed_at"]).total_seconds() / 3600)
        if age_hours > max_record_age_hours:
            alerts.append({"level": "warning", "code": "history_stale", "message": f"La última auditoría tiene {age_hours:.1f} horas; el límite es {max_record_age_hours:.1f}.", "age_hours": round(age_hours, 3)})
        ordered = sorted(records, key=lambda item: item["_parsed_at"], reverse=True)
        consecutive_failures = 0
        for record in ordered:
            if record.get("status") != "error":
                break
            consecutive_failures += 1
        if consecutive_failures >= max_consecutive_failures:
            alerts.append({"level": "critical", "code": "consecutive_failures", "message": f"Hay {consecutive_failures} auditorías fallidas consecutivas.", "count": consecutive_failures})
        if not latest.get("has_recent_valid_backup", False):
            alerts.append({"level": "critical", "code": "no_recent_valid_backup", "message": "La última auditoría no encontró un respaldo válido reciente."})
        if latest.get("invalid_count", 0) or latest.get("manifest_invalid_count", 0):
            alerts.append({"level": "critical", "code": "invalid_backups", "message": "La última auditoría detectó respaldos o manifiestos inválidos."})
    else:
        if history_file.is_file():
            alerts.append({"level": "critical", "code": "history_empty", "message": "El historial no contiene auditorías válidas."})

    for record in records:
        record.pop("_parsed_at", None)
    return {
        "history_file": str(history_file.resolve()),
        "record_count": len(records),
        "latest_record_at": max((r["recorded_at"] for r in records), default=None),
        "consecutive_failures": consecutive_failures if records else 0,
        "max_consecutive_failures": max_consecutive_failures,
        "max_record_age_hours": float(max_record_age_hours),
        "alert_count": len(alerts),
        "status": "ok" if not alerts else "alert", 
        "alerts": alerts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Respaldo y restauración de SQLite para Aranza")
    subparsers = parser.add_subparsers(dest="command", required=True)
    backup_parser = subparsers.add_parser("backup", help="Crear y verificar un respaldo")
    backup_parser.add_argument("--output-dir", type=Path, default=None)
    inspect_parser = subparsers.add_parser("inspect", help="Comprobar integridad y metadatos de una base sin modificarla")
    inspect_parser.add_argument("--source", type=Path, default=DB_PATH)
    doctor_parser = subparsers.add_parser("doctor", help="Diagnosticar ausencia, integridad y permisos sin modificar archivos")
    doctor_parser.add_argument("--source", type=Path, default=DB_PATH)
    audit_parser = subparsers.add_parser("audit-backups", help="Auditar integridad y antigüedad de los respaldos sin borrarlos")
    audit_parser.add_argument("--directory", type=Path, default=DB_PATH.parent / "backups")
    audit_parser.add_argument("--max-age-days", type=float, default=7.0)
    audit_parser.add_argument("--history-file", type=Path, default=None, help="Guardar el resultado de cada auditoría en un historial JSONL")
    status_parser = subparsers.add_parser("backup-status", help="Evaluar alertas y antigüedad del historial de auditorías")
    status_parser.add_argument("--history-file", type=Path, required=True)
    status_parser.add_argument("--max-consecutive-failures", type=int, default=2)
    status_parser.add_argument("--max-record-age-hours", type=float, default=24.0)
    verify_parser = subparsers.add_parser("verify-restore", help="Ensayar la restauración en una base temporal aislada")
    verify_parser.add_argument("--source", type=Path, required=True)
    restore_parser = subparsers.add_parser("restore", help="Restaurar desde un respaldo verificado")
    restore_parser.add_argument("--source", type=Path, required=True)
    restore_parser.add_argument("--confirm", action="store_true", help="Confirma que el servicio está detenido")
    args = parser.parse_args()

    try:
        if args.command == "backup":
            result = backup_database(DB_PATH, args.output_dir)
            print(f"Respaldo creado y verificado: {result}")
        elif args.command == "inspect":
            report = inspect_database(args.source)
            for key, value in report.items():
                print(f"{key}: {value}")
        elif args.command == "audit-backups":
            report = audit_backups(args.directory, args.max_age_days)
            for key, value in report.items():
                print(f"{key}: {value}")
            if args.history_file is not None:
                history_path = append_audit_history(args.history_file, report)
                print(f"Historial de auditorías actualizado: {history_path}")
            if not report["directory_exists"] or not report["has_recent_valid_backup"] or report["invalid_count"] or report.get("manifest_invalid_count", 0):
                return 1
        elif args.command == "verify-restore":
            report = verify_restore(args.source)
            print(json.dumps(report, ensure_ascii=False, indent=2))
        elif args.command == "backup-status":
            report = evaluate_backup_policy(args.history_file, args.max_consecutive_failures, args.max_record_age_hours)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            if report["status"] != "ok":
                return 1
        elif args.command == "doctor":
            report = diagnose_database(args.source)
            for key, value in report.items():
                print(f"{key}: {value}")
            if report["integrity"] != "ok" or not report["parent_writable"]:
                return 1
        else:
            if not args.confirm:
                parser.error("Para restaurar, añade --confirm y detén primero el servicio Aranza.")
            safety_copy = restore_database(args.source, DB_PATH)
            print(f"Base restaurada y verificada: {DB_PATH}")
            if safety_copy:
                print(f"Copia de seguridad de la base anterior: {safety_copy}")
        return 0
    except (OSError, sqlite3.Error, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
