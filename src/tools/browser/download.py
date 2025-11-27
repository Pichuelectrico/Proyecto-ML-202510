from agents import function_tool
from tools.browser.controller import init_browser
from tools.shared import log
import requests
import os

@function_tool
async def browser_download_from_click(selector: str, filename: str):
    log(f"⬇️ Iniciando descarga desde navegador → {selector}")
    page = await init_browser()
    os.makedirs("data/raw", exist_ok=True)
    path = f"data/raw/{filename}"

    async with page.expect_download(timeout=60000) as info:
        await page.click(selector)

    download = await info.value
    await download.save_as(path)
    log(f"✅ Descarga desde navegador completada → {path}")
    return f"Downloaded: {path}"

@function_tool
async def download_file(url: str, filename: str):
    log(f"⬇️ Iniciando descarga directa → {url}")
    os.makedirs("data/raw", exist_ok=True)
    path = f"data/raw/{filename}"

    r = requests.get(url, stream=True, timeout=60)
    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    log(f"✅ Descarga directa completada → {path}")
    return f"Downloaded: {path}"
