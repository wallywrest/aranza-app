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

def test_inline_code_is_protected_before_markdown_emphasis():
    html = (Path(__file__).parent / "index.html").read_text(encoding="utf-8")
    protection = "Protect inline code before parsing other syntax"
    restore = "CODESPAN"
    assert protection in html
    assert restore in html
    assert html.index(protection) < html.index("out = out.replace(/\\*\\*(.+?)\\*\\*/g")
    assert "return out.replace(/@@CODESPAN" in html


def test_code_fence_parser_keeps_code_content_escaped():
    html = (Path(__file__).parent / "index.html").read_text(encoding="utf-8")
    assert "const codeBlocks = []" in html
    assert "escapeHTML(source)" in html
    assert '<pre class="md-code"' in html
