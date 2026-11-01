"""La revisión previa solo contextualiza propuestas muy parecidas y de la misma cuenta."""
import base64
import hashlib
import hmac
import json
import time

from fastapi.testclient import TestClient
import main


def token(account_id="owner"):
    expires_at = int(time.time()) + main.SESSION_TTL_SECONDS
    nonce = f"review-context-{account_id}-{time.time_ns()}"
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO sesiones(nonce, expires_at, account_id) VALUES (?, ?, ?)", (nonce, expires_at, account_id))
    payload = json.dumps({"exp": expires_at, "nonce": nonce, "account_id": account_id}, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(hmac.new(main._session_secret(), body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return f"{body}.{signature}"


def create_review(account, memory_content, candidate, decision="no_contradiccion"):
    memory_id = main.guardar_memoria(memory_content + str(time.time_ns()), "general", account_id=account)
    with main.conectar_db() as conn:
        conn.execute(
            "INSERT INTO decisiones_revision_memoria(account_id, memory_id, decision, candidate_content) VALUES (?, ?, ?, ?)",
            (account, memory_id, decision, candidate),
        )
    return memory_id


def test_similar_candidate_includes_previous_review_for_same_account():
    main.inicializar_db()
    memory_id = main.guardar_memoria("Me gusta el café de Veracruz", "general", account_id="owner")
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO decisiones_revision_memoria(account_id, memory_id, decision, candidate_content) VALUES (?, ?, ?, ?)",
                     ("owner", memory_id, "no_contradiccion", "Me gusta el café de Veracruz"))
    headers = {"Authorization": f"Bearer {token('owner')}"}
    with TestClient(main.app) as client:
        response = client.post("/memory/check", json={"content": "Me gusta el café de Veracruz", "category": "general"}, headers=headers)
    assert response.status_code == 200
    candidate = next(c for c in response.json()["candidates"] if c["id"] == memory_id)
    assert candidate["previous_review"]["decision"] == "no_contradiccion"
    assert "no un veredicto automático" in candidate["previous_review"]["note"]


def test_review_context_is_not_shared_between_accounts():
    main.inicializar_db()
    memory_id = main.guardar_memoria("Me gusta el café de Veracruz", "general", account_id="owner")
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO decisiones_revision_memoria(account_id, memory_id, decision, candidate_content) VALUES (?, ?, ?, ?)",
                     ("another-account", memory_id, "temporal", "Me gusta el café de Veracruz"))
    headers = {"Authorization": f"Bearer {token('owner')}"}
    with TestClient(main.app) as client:
        response = client.post("/memory/check", json={"content": "Me gusta el café de Veracruz", "category": "general"}, headers=headers)
    assert response.status_code == 200
    candidate = next(c for c in response.json()["candidates"] if c["id"] == memory_id)
    assert "previous_review" not in candidate


def test_weakly_similar_candidate_does_not_get_old_review_annotation():
    main.inicializar_db()
    memory_id = main.guardar_memoria("Me gusta el café de Veracruz", "general", account_id="owner")
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO decisiones_revision_memoria(account_id, memory_id, decision, candidate_content) VALUES (?, ?, ?, ?)",
                     ("owner", memory_id, "temporal", "Ahora prefiero las bicicletas rojas para viajar"))
    headers = {"Authorization": f"Bearer {token('owner')}"}
    with TestClient(main.app) as client:
        response = client.post("/memory/check", json={"content": "Me gusta el café de Veracruz", "category": "general"}, headers=headers)
    assert response.status_code == 200
    candidate = next(c for c in response.json()["candidates"] if c["id"] == memory_id)
    assert "previous_review" not in candidate


def test_matching_older_review_is_not_lost_after_unrelated_newer_review():
    main.inicializar_db()
    memory_id = main.guardar_memoria("Me gusta el café de Veracruz", "general", account_id="owner")
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO decisiones_revision_memoria(account_id, memory_id, decision, candidate_content) VALUES (?, ?, ?, ?)",
                     ("owner", memory_id, "no_contradiccion", "Me gusta el café de Veracruz"))
        conn.execute("INSERT INTO decisiones_revision_memoria(account_id, memory_id, decision, candidate_content) VALUES (?, ?, ?, ?)",
                     ("owner", memory_id, "temporal", "Ahora prefiero las bicicletas rojas para viajar"))
    headers = {"Authorization": f"Bearer {token('owner')}"}
    with TestClient(main.app) as client:
        response = client.post("/memory/check", json={"content": "Me gusta el café de Veracruz", "category": "general"}, headers=headers)
    assert response.status_code == 200
    candidate = next(c for c in response.json()["candidates"] if c["id"] == memory_id)
    assert candidate["previous_review"]["decision"] == "no_contradiccion"
    assert candidate["previous_review"]["similarity"] >= 0.65


def test_best_matching_review_is_selected_instead_of_newest_unrelated_review():
    main.inicializar_db()
    memory_id = main.guardar_memoria("Quiero estudiar ingeniería industrial", "general", account_id="owner")
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO decisiones_revision_memoria(account_id, memory_id, decision, candidate_content) VALUES (?, ?, ?, ?)",
                     ("owner", memory_id, "temporal", "Quiero estudiar ingeniería industrial y finanzas"))
        conn.execute("INSERT INTO decisiones_revision_memoria(account_id, memory_id, decision, candidate_content) VALUES (?, ?, ?, ?)",
                     ("owner", memory_id, "archivado", "Prefiero aprender cocina italiana los domingos"))
    headers = {"Authorization": f"Bearer {token('owner')}"}
    with TestClient(main.app) as client:
        response = client.post("/memory/check", json={"content": "Quiero estudiar ingeniería industrial y finanzas", "category": "general"}, headers=headers)
    assert response.status_code == 200
    candidate = next(c for c in response.json()["candidates"] if c["id"] == memory_id)
    assert candidate["previous_review"]["decision"] == "temporal"


def test_temporal_marker_detector_normalizes_accents_and_common_phrases():
    markers = main.detectar_senales_temporales("Antes me gustaba correr, pero ahora prefiero caminar y ya no hago ejercicio")
    assert "antes" in markers
    assert "ahora" in markers
    assert "ya no" in markers
    assert "antes me gustaba" in markers
    assert "ahora prefiero" in markers


def test_temporal_marker_detector_ignores_generic_preference_without_time_cues():
    assert main.detectar_senales_temporales("Me gusta el café de Veracruz") == []


def test_memory_check_marks_temporal_cues_without_changing_memory():
    main.inicializar_db()
    memory_id = main.guardar_memoria("Me gusta el café de Veracruz", "general", account_id="owner")
    headers = {"Authorization": f"Bearer {token('owner')}"}
    with TestClient(main.app) as client:
        response = client.post("/memory/check", json={"content": "Antes me gustaba el café de Veracruz, ahora ya no me gusta el café de Veracruz", "category": "general"}, headers=headers)
    assert response.status_code == 200
    candidate = next(c for c in response.json()["candidates"] if c["id"] == memory_id)
    assert candidate["temporal_context"]["proposal_markers"]
    assert candidate["temporal_context"]["existing_memory_markers"] == []
    assert response.json()["automatic_changes"] is False
    with main.conectar_db() as conn:
        row = conn.execute("SELECT content FROM memorias WHERE id = ?", (memory_id,)).fetchone()
    assert row["content"] == "Me gusta el café de Veracruz"
