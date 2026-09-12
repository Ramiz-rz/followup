"""
Turns an uploaded file into normalized plain text that the analyzer
can work with. We never send raw binary content anywhere, and we never
hand a file straight to OpenAI, everything goes through here first.
"""
import json
import re

SUPPORTED_EXTENSIONS = {"txt", "md", "markdown", "json", "pdf"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


class DocumentParseError(Exception):
    pass


def get_extension(filename: str) -> str:
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # collapse 3+ blank lines into a single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)
    # collapse runs of spaces/tabs
    text = re.sub(r"[ \t]{2,}", " ", text)
    # strip trailing whitespace on each line
    lines = [line.rstrip() for line in text.split("\n")]
    return "\n".join(lines).strip()


def parse_markdown(raw: str) -> str:
    text = raw
    # strip markdown headers, bold/italic markers, code fences, links
    text = re.sub(r"^```[\s\S]*?```$", "", text, flags=re.MULTILINE)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^[-*]\s+", "", text, flags=re.MULTILINE)
    return clean_text(text)


def parse_json_bytes(raw_bytes: bytes) -> str:
    try:
        data = json.loads(raw_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise DocumentParseError("This JSON file could not be read.") from e

    fragments = []

    def walk(node):
        if isinstance(node, str):
            stripped = node.strip()
            if len(stripped) > 1:
                fragments.append(stripped)
        elif isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    if not fragments:
        raise DocumentParseError("No readable text was found in this JSON file.")
    return clean_text("\n".join(fragments))


def parse_pdf_bytes(raw_bytes: bytes) -> str:
    try:
        import fitz  # PyMuPDF
    except ImportError as e:
        raise DocumentParseError("PDF support is not available on this server.") from e

    try:
        doc = fitz.open(stream=raw_bytes, filetype="pdf")
    except Exception as e:
        raise DocumentParseError("We could not read this PDF.") from e

    pages = []
    try:
        for page in doc:
            pages.append(page.get_text())
    except Exception as e:
        raise DocumentParseError("We could not read this PDF.") from e
    finally:
        doc.close()

    text = clean_text("\n".join(pages))
    if not text:
        raise DocumentParseError("This PDF does not seem to contain extractable text.")
    return text


def parse_txt_bytes(raw_bytes: bytes) -> str:
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = raw_bytes.decode("latin-1", errors="ignore")
    return clean_text(text)


def parse_document(filename: str, raw_bytes: bytes) -> str:
    if len(raw_bytes) > MAX_FILE_SIZE_BYTES:
        raise DocumentParseError("This file is too large. Keep it under 5 MB.")

    ext = get_extension(filename)
    if ext not in SUPPORTED_EXTENSIONS:
        raise DocumentParseError("This file type is not supported.")

    if ext == "pdf":
        return parse_pdf_bytes(raw_bytes)
    if ext == "json":
        return parse_json_bytes(raw_bytes)
    if ext in ("md", "markdown"):
        return parse_markdown(parse_txt_bytes(raw_bytes))
    return parse_txt_bytes(raw_bytes)
