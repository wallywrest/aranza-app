from pathlib import Path


def test_chat_markdown_renderer_supports_rich_safe_formatting():
    html = (Path(__file__).parent / "index.html").read_text(encoding="utf-8")
    for feature in (
        "function renderMarkdown(source)", "md-table-wrap", "md-heading",
        "md-image", "md-code-label", "<blockquote>", "<del>", "<u>",
        "rel=\"noopener noreferrer\"",
    ):
        assert feature in html


def test_chat_markdown_renderer_does_not_enable_raw_html():
    html = (Path(__file__).parent / "index.html").read_text(encoding="utf-8")
    assert "Raw HTML is never trusted" in html
    assert "escapeHTML(source)" in html
    assert "target=\"_blank\" rel=\"noopener noreferrer\"" in html
