"""Pruebas de títulos, fijado y aislamiento de conversaciones."""
import main


def test_first_message_creates_persistent_title_and_conversation():
    cid = "meta-title-test"
    main.guardar_intercambio(cid, "Preparar exposición de gestión industrial", "Vamos a organizarla.", "meta-user-a")
    rows = main.listar_conversaciones("meta-user-a")
    row = next(item for item in rows if item["conversation_id"] == cid)
    assert row["title"] == "Preparar exposición de gestión industrial"
    assert row["pinned"] == 0
    assert row["message_count"] == 2


def test_pin_and_title_update_are_persistent_and_sort_first():
    main.guardar_intercambio("meta-normal", "Chat normal", "Respuesta", "meta-user-b")
    main.guardar_intercambio("meta-pinned", "Chat importante", "Respuesta", "meta-user-b")
    assert main.actualizar_metadatos_conversacion("meta-pinned", "meta-user-b", title="Proyecto Aranza", pinned=True)
    rows = main.listar_conversaciones("meta-user-b")
    assert rows[0]["conversation_id"] == "meta-pinned"
    assert rows[0]["title"] == "Proyecto Aranza"
    assert rows[0]["pinned"] == 1
    assert main.actualizar_metadatos_conversacion("meta-pinned", "meta-user-b", pinned=False)
    assert next(r for r in main.listar_conversaciones("meta-user-b") if r["conversation_id"] == "meta-pinned")["pinned"] == 0


def test_conversation_metadata_is_account_scoped():
    main.guardar_intercambio("same-id", "Cuenta A", "Respuesta A", "meta-account-a")
    main.guardar_intercambio("same-id", "Cuenta B", "Respuesta B", "meta-account-b")
    assert main.actualizar_metadatos_conversacion("same-id", "meta-account-a", title="Privado A", pinned=True)
    row_a = next(r for r in main.listar_conversaciones("meta-account-a") if r["conversation_id"] == "same-id")
    row_b = next(r for r in main.listar_conversaciones("meta-account-b") if r["conversation_id"] == "same-id")
    assert row_a["title"] == "Privado A" and row_a["pinned"] == 1
    assert row_b["title"] == "Cuenta B" and row_b["pinned"] == 0
    assert not main.actualizar_metadatos_conversacion("same-id", "meta-account-c", title="Intruso")


def test_deleting_conversation_also_deletes_metadata():
    main.guardar_intercambio("meta-delete", "Borrar esto", "Respuesta", "meta-delete-user")
    assert main.borrar_conversacion("meta-delete", "meta-delete-user")
    with main.conectar_db() as conn:
        assert conn.execute("SELECT 1 FROM conversaciones WHERE account_id=? AND conversation_id=?", ("meta-delete-user", "meta-delete")).fetchone() is None
