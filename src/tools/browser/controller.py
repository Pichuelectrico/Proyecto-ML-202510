from playwright.async_api import async_playwright

_playwright = None
_browser = None
_context = None
_page = None


async def init_browser(headless=True):
    global _playwright, _browser, _context, _page

    if _browser is None:
        print("🌐 [BROWSER] Iniciando Playwright...", flush=True)
        _playwright = await async_playwright().start()

        print("🌐 [BROWSER] Lanzando Chromium...", flush=True)
        _browser = await _playwright.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"]
        )

        print("🌐 [BROWSER] Creando contexto y página...", flush=True)
        _context = await _browser.new_context()
        _page = await _context.new_page()

        print("✅ [BROWSER] Navegador listo", flush=True)

    return _page



async def close_browser():
    global _playwright, _browser
    if _browser:
        await _browser.close()
        await _playwright.stop()
