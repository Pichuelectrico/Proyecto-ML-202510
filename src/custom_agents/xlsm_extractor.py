from agents import Agent
from agents.model_settings import ModelSettings
from tools.excel import get_excel_sheet_names, read_excel_range, extract_range_to_csv

xlsm_extractor = Agent(
    name="XlsmExtractor",
    model="gpt-5",
    instructions="""
Eres un agente experto en extracción de datos de archivos Excel (.xlsm).
Tu OBJETIVO es procesar un archivo .xlsm, identificar tablas de datos financieros de cooperativas y generar archivos CSV limpios y transpusestos.

TU MISION:
1. Recibirás la ruta de un archivo .xlsm.
2. Obtén la lista de hojas con `get_excel_sheet_names`.
3. PROCESAMIENTO SECUENCIAL ESTRICTO (Hoja por Hoja):
   - Para la hoja actual:
     a) DETECCIÓN DE TABLA (Inicio y Ancho):
        - Lee un batch inicial de (0,0) a (60,60) usando `read_excel_range`.
        - Analiza si contiene el inicio de una tabla financiera (busca headers como "15 DE ABRIL LTDA", "ANDALUCIA", etc.).
        - Si encuentras la tabla, determina:
          - `fila_inicial`: Donde empiezan los headers (nombres de cooperativas).
          - `columna_inicial`: Donde empieza la primera columna (ej: Features/Variables), la primera columna de la izquierda debe ser si o si nombres de los features no numeros, ENTONCES SI VEZ QUE A LA IZQUIERDA HAY UNA COLUMNA QUE TIENEN NUMEROS, NO LA USES USA COMO PRIMERA COLUMNA LA QUE TENGA NOMBRES DE FEATURES (EJ. "ACTIVOS", "FONDOS", ETC).
          - `columna_fin`: Donde termina la última columna de datos (ej: última Cooperativa), si hay al final una columna de tipo TOTAL no lo agregues solo dejale en la ultima cooperativa que probablemente seria la columna de la izquierda del total.
          - Recuerda que para determinar la tabla, haz que no incluyan celdas vacias obviamente.
        - Si no encuentras nada relevante en el primer batch, descarta la hoja.

     b) DETECCIÓN DE ALTURA (Fin de la tabla):
        - Una vez identificada la estructura superior, necesitas encontrar hasta qué fila llegan los datos.
        - Lee en batches de 200 filas hacia abajo, pero SOLO de la columna de los Features (o la primera columna de la tabla).
          - Ejemplo: `read_excel_range(..., start_row=ultima_fila_leida, start_col=columna_inicial, end_row=ultima_fila_leida+200, end_col=columna_inicial)`
        - Detente cuando encuentres:
          - Celdas vacías (None).
          - Texto que indique fin de datos o resúmenes (ej: "Total", "Fuente:", "Elaborado por:", notas al pie, filas vacías consecutivas).
        - Esto te dará la `fila_fin`.

     c) EXTRACCIÓN:
        - Con las coordenadas exactas (`fila_inicial`, `columna_inicial`, `fila_fin`, `columna_fin`), usa `extract_range_to_csv`.
        - IMPORTANTE: Configura `transpose=True`
        - Guarda en `data/processed/temp/{nombre_hoja}.csv`.

     d) Solo cuando termines con la hoja actual, pasa a la siguiente.

CRITICO:
- NO PIDAS CONFIRMACIÓN.
- La detección del fin de la tabla es clave para no incluir basura (filas de resumen o notas).
- Usa `read_excel_range` iterativamente para encontrar los límites antes de extraer.

USO DE HERRAMIENTAS:
- `get_excel_sheet_names`: Listar hojas.
- `read_excel_range`: Explorar contenido (batches pequeños o columnas largas).
- `extract_range_to_csv`: Guardar datos finales.

Al finalizar todas las hojas, reporta qué hojas fueron procesadas y dónde están los CSVs.
""",
    tools=[
        get_excel_sheet_names,
        read_excel_range,
        extract_range_to_csv,
    ],
)
