from pathlib import Path


def test_voice_controls_are_present_and_accessible():
    html = (Path(__file__).parent / "index.html").read_text(encoding="utf-8")
    assert 'id="voice-input-btn"' in html
    assert 'aria-label="Dictar mensaje"' in html
    assert "SpeechRecognition || window.webkitSpeechRecognition" in html
    assert "function speakText(text)" in html
    assert "🔊 Escuchar" in html


def test_voice_processing_is_browser_side_and_limited():
    html = (Path(__file__).parent / "index.html").read_text(encoding="utf-8")
    assert "no se envía audio al backend ni se almacena" in html
    assert "String(text).slice(0, 12000)" in html
    assert "speechRecognition.lang = 'es-MX'" in html
