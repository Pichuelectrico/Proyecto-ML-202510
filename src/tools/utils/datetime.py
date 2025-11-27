from agents import function_tool
from datetime import datetime
from tools.shared import log

@function_tool
def get_current_date():
    log("📅 Obteniendo fecha actual del sistema")
    now = datetime.now()
    return {
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "iso": now.strftime("%Y-%m-%d")
    }
