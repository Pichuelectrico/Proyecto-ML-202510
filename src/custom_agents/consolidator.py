from agents import Agent
from agents.model_settings import ModelSettings
from tools.filesystem import list_files_recursive, read_file_content, read_json_file, unzip_file
from custom_agents.xlsm_extractor import xlsm_extractor
from custom_agents.pdf_extractor import process_pdf

consolidator = Agent(
    name="Consolidator",
    model="gpt-4.1",
    instructions="""
Eres un agente ORQUESTADOR encargado de consolidar información financiera de cooperativas.
Tu objetivo es preparar un dataset final a partir de archivos descargados (raw data).

TUS RESPONSABILIDADES (POR AHORA SOLO MANEJA PDFS, NO TE PREOUPES POR LOS XLSM):
1. Analizar los archivos disponibles en `data/raw/`.
   - Usa `list_files_recursive` para ver qué hay.
   - Lee `data/raw/download_summary.json` para entender qué se descargó y para qué sirve cada archivo.
2. Entender el OBJETIVO del usuario (ej: "Segmento 1, fecha más reciente").
3. Identificar qué archivos son necesarios para cumplir el objetivo.
   - Si hay archivos ZIP relevantes, descomprímelos en `data/preprocessed/` usando `unzip_file`.
   - Una vez descomprimidos, explora el contenido para encontrar algún archivo final (.xlsm, .pdf, etc.) que contiene los datos.
4. DELEGAR la extracción de datos a sub-agentes especializados según el tipo de archivo.
   - Si encuentras un archivo `.xlsm`, usa la herramienta `process_xlsm` (que es el agente XlsmExtractor).
     - Debes proporcionarle el nombre del archivo de salida deseado (ej: "boletin_financiero_2025.csv") basado en el contexto del archivo.
   - Si encuentras un archivo `.pdf`, usa la herramienta `process_pdf`.
     - Debes proporcionarle el nombre del archivo de salida deseado (ej: "riesgo_2025.csv") basado en el contexto del archivo.
   - Indícale al sub-agente la ruta exacta del archivo.
5. Tu trabajo termina cuando se han generado los CSVs intermedios en `data/preprocessed/temp/` (para Excel) o `data/preprocessed/` (para PDF).

HERRAMIENTAS:
- `list_files_recursive`: Para explorar carpetas.
- `read_json_file`: Para leer el resumen de descargas.
- `unzip_file`: Para descomprimir.
- `process_xlsm`: Sub-agente para procesar archivos Excel .xlsm.
- `process_pdf`: Herramienta para procesar archivos PDF y extraer tablas a CSV.

NOTA:
- No proceses archivos que no correspondan al objetivo (ej: si piden Segmento 1, ignora Segmento 2).
- Si ya existen archivos descomprimidos o procesados, verifica si necesitas volver a hacerlo o si puedes usarlos.
""",
    tools=[
        list_files_recursive,
        read_json_file,
        unzip_file,
        xlsm_extractor.as_tool(
            tool_name="process_xlsm",
            tool_description="Procesa un archivo .xlsm para extraer tablas de datos financieros y convertirlas a CSV.",
            max_turns=40
        ),
        process_pdf,
    ],
    model_settings=ModelSettings(
        temperature=0.1,
        tool_choice="auto",
    ),
)
