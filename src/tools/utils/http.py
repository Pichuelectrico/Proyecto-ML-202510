import requests
import mimetypes
from urllib.parse import urlparse, unquote
from tools.shared import log
from tools.utils.parsing import parse_content_disposition
from agents import function_tool

@function_tool
def inspect_download_url(url: str) -> dict:
    log(f"🔍 Inspeccionando URL de descarga → {url}")

    try:
        head = requests.head(url, allow_redirects=True, timeout=20)
        final_url = head.url
        content_type = head.headers.get("content-type", "").lower()
        content_disp = head.headers.get("content-disposition", "")

        filename = ""
        if content_disp:
            _, params = parse_content_disposition(content_disp)
            filename = params.get("filename") or params.get("filename*") or ""

        if not filename:
            parsed = urlparse(final_url)
            filename = unquote(parsed.path.split("/")[-1])

        ext = ""
        if "." in filename:
            ext = filename.split(".")[-1].lower()
        elif content_type:
            ext = (mimetypes.guess_extension(content_type) or "").lstrip(".")

        return {
            "url_final": final_url,
            "content_type": content_type,
            "filename": filename,
            "extension": ext,
        }

    except Exception as e:
        return {
            "url_final": url,
            "content_type": "",
            "filename": "",
            "extension": "",
            "error": str(e)
        }