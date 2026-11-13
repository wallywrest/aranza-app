from pathlib import Path

BASE = Path(__file__).parent


def test_drafts_are_scoped_by_account_and_conversation():
    html = (BASE / 'index.html').read_text(encoding="utf-8")
    assert "const DRAFT_PREFIX = 'aranza_draft_v1:'" in html
    assert 'const account = state.accountId || \'anonymous\'' in html
    assert 'function scopedStorageKey(key)' in html
    assert 'encodeURIComponent(String(id || \'nuevo\'))' in html


def test_drafts_are_local_and_never_auto_sent():
    html = (BASE / 'index.html').read_text(encoding="utf-8")
    assert 'localStorage.setItem(key, value)' in html
    assert 'function restoreDraft' in html
    assert 'function clearDraft' in html
    assert 'clearDraft();' in html
    # Restoring a draft only populates the composer; it does not invoke sendMessage.
    restore = html.split('function restoreDraft', 1)[1].split('function clearDraft', 1)[0]
    assert "$('user-input').value = value" in restore
    assert 'sendMessage(' not in restore


def test_network_status_is_visible_and_reacts_to_connection_changes():
    html = (BASE / 'index.html').read_text(encoding="utf-8")
    assert 'id="network-status"' in html
    assert "window.addEventListener('online', updateNetworkStatus)" in html
    assert "window.addEventListener('offline', updateNetworkStatus)" in html


def test_logout_purges_aranza_local_data_and_conversation_delete_calls_server():
    html = (BASE / 'index.html').read_text(encoding="utf-8")
    assert "function purgeAranzaLocalData()" in html
    assert "clearBrowserSession(); showLogin('Sesión cerrada.')" in html
    assert "method: 'DELETE'" in html
    assert "Eliminar permanentemente esta conversación" in html


def test_conversation_search_archive_and_attachment_history_are_connected_to_api():
    html = (BASE / 'index.html').read_text(encoding="utf-8")
    assert 'id="history-search"' in html
    assert 'id="history-archive-toggle"' in html
    assert "params.set('q', query)" in html
    assert "params.set('archived', 'true')" in html
    assert "form.append('conversation_id', state.conversationId)" in html
    assert "async function syncCurrentConversationFromServer()" in html
