import base64
import os
from agents import Agent, Runner, function_tool
from tools.shared import log
from tools.pdf_tools import extract_text_from_pdf

def file_to_base64(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

@function_tool
def save_csv_from_pdf(content: str, output_filename: str) -> str:
    """
    Saves the extracted CSV content to a file in data/preprocessed/.
    
    Args:
        content: The CSV string content.
        output_filename: The name of the file to save (e.g., 'risk_matrix.csv').
    """
    output_path = os.path.join("data/preprocessed", output_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.write(content)
    
    log(f"💾 Saved PDF extraction to: {output_path}")
    return f"Successfully saved CSV to {output_path}"

@function_tool
def update_csv_with_correction(content: str, output_filename: str) -> str:
    """
    Updates an existing CSV file with corrected content and logs the differences.
    Use this tool ONLY when correcting an already saved CSV after verification.
    
    Args:
        content: The new corrected CSV string content.
        output_filename: The name of the file to update (e.g., 'risk_matrix.csv').
    """
    output_path = os.path.join("data/preprocessed", output_filename)
    
    if not os.path.exists(output_path):
        return save_csv_from_pdf(content, output_filename)
        
    # Read old content for comparison
    with open(output_path, "r", encoding="utf-8-sig") as f:
        old_lines = f.readlines()
        
    new_lines = content.splitlines(keepends=True)
    
    # Simple diff count
    diff_count = 0
    # Compare line by line (basic heuristic)
    min_len = min(len(old_lines), len(new_lines))
    for i in range(min_len):
        if old_lines[i].strip() != new_lines[i].strip():
            diff_count += 1
            
    diff_count += abs(len(old_lines) - len(new_lines))
    
    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.write(content)
    
    log(f"🛠️ Correcting CSV: {output_filename}")
    log(f"   -> Updated {diff_count} lines with corrections based on text verification.")
    
    return f"Successfully updated CSV with {diff_count} line changes."

pdf_extractor = Agent(
    name="PdfExtractor",
    model="gpt-5",
    instructions="""
    Eres un agente experto en extracción de datos de documentos PDF.
    Tu tarea es recibir un archivo PDF, encontrar la tabla de datos financieros o de riesgo de cooperativas, y extraerla COMPLETAMENTE (si esta separada en paginas juntala, pero tienes que extraer TODA la tabla) y EXACTAMENTE como está.
    Asegurate que cada celda caudre con el lugar de la tabla en el que estaba en el pdf, no deberia haber celdas sin datos (pero NO te puedes inventar ninguno), ni deben haber datos en lugares en donde no hay headers por ejemplo (tipo fuera de la estructura principal de la tabla).
    Si se trata de una valoracion de riesgos asegurate de obtener todos los valores de riesgos y exactamente donde deberian estar en la tabla.
    
    FLUJO DE TRABAJO:
    1. Analiza el archivo PDF adjunto visualmente.
    2. Extrae la tabla completa en formato CSV y guárdala usando `save_csv_from_pdf`.
    3. VERIFICACIÓN Y CORRECCIÓN (OBLIGATORIO):
       - Una vez guardado el CSV inicial, llama a `extract_text_from_pdf` para obtener el texto crudo del archivo.
       - Compara el texto extraído con los datos de tu CSV.
       - Busca discrepancias en valores numéricos o valores de riesgos (ej: AA-, numeros, etc).
       - Si encuentras discrepancias en esos valores deterministicos, CORRIGE el contenido CSV y guárdalo usando `update_csv_with_correction`.
       - PERO RECUERDA, EL CSV INCIAL ES EL QUE DEBE TENER MAS VALIDEZ, Y SU ESTRUCTURA NO LA CAMBIES PARA NADA, SOLO HAY QUE COMPARAR VALORES Y CAMBIAR SI NO LOS DETERMINASTE BIEN PORQUE CON EL TEXTO EXTRAIDO EL VALOR SI O SI ES ESE. 
    
    El usuario te proporcionará el nombre del archivo de salida en el prompt. Úsalo.
    """,
    tools=[save_csv_from_pdf, extract_text_from_pdf, update_csv_with_correction]
)

@function_tool
async def process_pdf(file_path: str, output_filename: str) -> str:
    """
    Procesa un archivo PDF para extraer tablas y guardarlas como CSV.
    
    Args:
        file_path: Ruta al archivo PDF (ej: 'data/preprocessed/archivo.pdf').
        output_filename: Nombre del archivo CSV de salida (ej: 'riesgo_junio_2025.csv').
    """
    log(f"📄 Procesando PDF: {file_path}")
    
    if not os.path.exists(file_path):
        return f"Error: El archivo {file_path} no existe."
        
    try:
        b64_file = file_to_base64(file_path)
        
        # Mensaje inicial con el archivo y la instrucción
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "file_data": f"data:application/pdf;base64,{b64_file}",
                        "filename": os.path.basename(file_path),
                    }
                ],
            },
            {
                "role": "user",
                "content": f"Extrae la tabla de este PDF y guárdala como '{output_filename}'. Luego verifica el texto con extract_text_from_pdf('{file_path}') y corrige si es necesario."
            }
        ]
        
        # Ejecutar el agente
        result = await Runner.run(
            starting_agent=pdf_extractor,
            input=messages,
            max_turns=10
        )
        
        print(f"Procesamiento de PDF completado. Resultado: {result.final_output}")
        
        return f"Procesamiento de PDF completado. Resultado: {result.final_output}"
        
    except Exception as e:
        print(f"Error procesando PDF: {str(e)}")
        return f"Error procesando PDF: {str(e)}"
