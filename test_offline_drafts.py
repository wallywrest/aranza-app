from pathlib import Path

BASE = Path(__file__).parent


def test_drafts_are_scoped_by_account_and_conversation():
    html = (BASE / 'index.html').read_text(encoding="utf-8")
    assert "const DRAFT_PREFIX = 'aranza_draft_v1:'" in html
    assert 'encodeURIComponent(account)' in html
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
