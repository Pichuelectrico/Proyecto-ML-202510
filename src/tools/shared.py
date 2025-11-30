from rich.console import Console
from rich.rule import Rule
import os
import re

_console = Console()
LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "execution_log.txt")

def log(msg: str):
    _console.print(f"[bold blue]🧠[/bold blue] [dim]tool[/dim] › {msg}")

def print_header(title: str, description: str):
    _console.print(Rule(style="bold cyan", characters="="))
    _console.print(f"[bold white]{title}")
    _console.print(f"[grey70]{description}")
    _console.print(Rule(style="bold cyan", characters="="))

def clear_execution_log():
    try:
        with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("=== Execution Log ===\n\n")
    except Exception as e:
        print(f"Error clearing execution log: {e}")

from agents import function_tool

@function_tool
def report_agent_start(title: str, description: str):
    print_header(title, description)
    return f"Inicio reportado para agente {title}"

@function_tool
def report_agent_completion(title: str, output: str):
    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*40}\n")
            f.write(f"AGENT: {title}\n")
            f.write(f"{'='*40}\n")
            f.write(f"{output}\n\n")
        return f"Output registrado correctamente para {title}"
    except Exception as e:
        return f"Error registrando output: {str(e)}"

def reorder_execution_log():
    if not os.path.exists(LOG_FILE_PATH):
        return

    try:
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        header_marker = "=== Execution Log ===\n\n"
        if content.startswith(header_marker):
            header = header_marker
            body = content[len(header_marker):]
        else:
            header = ""
            body = content
        pattern = re.compile(r"(\n?={40}\nAGENT: \[(\d+)/\d+\].*?)(?=\n={40}\nAGENT: |\Z)", re.DOTALL)
        
        matches = pattern.findall(body)
        
        if not matches:
            return
        sorted_matches = sorted(matches, key=lambda x: int(x[1]))
        new_body = "".join([m[0] for m in sorted_matches])
        
        with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(header + new_body)

    except Exception as e:
        print(f"Error reordering execution log: {e}")
