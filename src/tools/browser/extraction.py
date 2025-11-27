from agents import function_tool
from tools.browser.controller import init_browser
from tools.shared import log

@function_tool
async def browser_get_text(selector: str):
    page = await init_browser()
    txt = await page.inner_text(selector)
    log(f"📄 Texto extraído → {selector}")
    return txt.strip()

@function_tool
async def browser_get_links():
    page = await init_browser()
    links = await page.eval_on_selector_all(
        "a",
        "els => els.map(e => ({ text: e.innerText, href: e.href }))"
    )
    log(f"🔗 {len(links)} enlaces encontrados")
    return links
