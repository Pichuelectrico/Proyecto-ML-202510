import json
import os
from agents import function_tool
from tools.shared import log
from pydantic import BaseModel

class FileInfo(BaseModel):
    filename: str
    description: str

@function_tool
def save_download_summary(files: list[FileInfo]):
    """
    Guarda un archivo JSON en data/raw con la descripción de los archivos descargados.
    
    Args:
        files: Lista de objetos con filename y description.
    """
    log("📝 Guardando resumen de descargas...")
    os.makedirs("data/raw", exist_ok=True)
    
    summary_path = "data/raw/download_summary.json"
    
    # Convert Pydantic models to dicts
    files_data = [f.model_dump() for f in files]

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(files_data, f, indent=4, ensure_ascii=False)
        
    log(f"✅ Resumen guardado en {summary_path}")
    return f"Summary saved to {summary_path}"
