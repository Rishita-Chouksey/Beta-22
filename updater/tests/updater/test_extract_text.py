import pytest
import io
import pypdf
from updater.extract_text import (
    normalize_text,
    calculate_sha256,
    extract_from_html,
    process_document
)

def test_html_strips_boilerplate_and_scripts():
    html = """
    <html>
      <head>
        <script>function bad(){ return 1; }</script>
        <style>body { background: red; }</style>
      </head>
      <body>
        <nav><a href="/">Home</a><a href="/login">Login</a></nav>
        <header><h1>Ministry Header</h1></header>
        <main>
          <h2>PM-KISAN Samman Nidhi</h2>
          <p>Under PM-KISAN, eligible farmers receive ₹6,000 annually in three installments of ₹2,000 each.</p>
        </main>
        <footer><p>Copyright 2026 NIC</p></footer>
      </body>
    </html>
    """
    clean = extract_from_html(html.encode("utf-8"))
    assert "bad()" not in clean
    assert "background: red" not in clean
    assert "Home" not in clean
    assert "Login" not in clean
    assert "Copyright" not in clean
    assert "PM-KISAN Samman Nidhi" in clean
    assert "₹6,000" in clean

def test_text_normalization():
    raw = "Under   PM-KISAN,\t Rs. 6000\n\n\n\nis  given  to farmers."
    norm = normalize_text(raw)
    assert norm == "Under PM-KISAN, ₹ 6000\n\nis given to farmers."

def test_sha256_deterministic():
    t1 = "Landholding farmer entitlement: ₹6000 per year."
    t2 = "Landholding farmer entitlement: ₹6000 per year."
    assert calculate_sha256(t1) == calculate_sha256(t2)
    assert calculate_sha256(t1) != calculate_sha256(t1 + " ")

def test_process_document_html():
    html = b"<html><body><main><p>Eligible income limit is Rs. 2,00,000.</p></main></body></html>"
    doc = process_document(html, content_type="text/html")
    assert doc.is_pdf is False
    assert "₹ 2,00,000" in doc.clean_text or "₹2,00,000" in doc.clean_text
    assert len(doc.sha256) == 64
    assert doc.word_count > 0

def test_process_document_scanned_pdf_detection():
    # Create an empty or tiny synthetic PDF without text layer (simulating scanned document)
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=100, height=100)
    buf = io.BytesIO()
    writer.write(buf)
    pdf_bytes = buf.getvalue()

    doc = process_document(pdf_bytes, content_type="application/pdf", url="https://sample.nic.in/doc.pdf")
    assert doc.is_pdf is True
    assert doc.is_scanned_pdf is True
