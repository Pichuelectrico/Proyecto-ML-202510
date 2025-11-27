from agents import function_tool
from tools.browser.controller import init_browser
from tools.shared import log

@function_tool
async def browser_open(url: str):
    log(f"🌐 Abriendo página → {url}")
    page = await init_browser()
    await page.goto(url, timeout=60000)
    log("✅ Página cargada")
    return f"OK: opened {url}"

@function_tool
async def browser_click(selector: str):
    log(f"🖱️ Click → {selector}")
    page = await init_browser()
    await page.click(selector)
    return f"OK: clicked {selector}"

@function_tool
async def browser_type(selector: str, text: str):
    log(f"⌨️ Escribiendo en {selector}: {text}")
    page = await init_browser()
    await page.fill(selector, text)
    return "OK"

@function_tool
async def browser_wait(selector: str):
    log(f"⏳ Esperando elemento → {selector}")
    page = await init_browser()
    await page.wait_for_selector(selector, timeout=60000)
    log(f"👀 Visible → {selector}")
    return "OK"

@function_tool
async def browser_scroll(pixels: int = 2000):
    log(f"🌀 Scroll → {pixels}px")
    page = await init_browser()
    await page.mouse.wheel(0, pixels)
    return f"Scroll {pixels}px"

@function_tool
async def browser_eval(script: str):
    log("🧮 Ejecutando JavaScript en la página")
    page = await init_browser()
    result = await page.evaluate(script)
    log("📤 Resultado de JavaScript obtenido")
    return result