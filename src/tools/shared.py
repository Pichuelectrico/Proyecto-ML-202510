from rich.console import Console
from rich.rule import Rule

_console = Console()

def log(msg: str):
    """Unified logging with Rich styling."""
    _console.print(f"[bold blue]🧠[/bold blue] [dim]tool[/dim] › {msg}")

def print_header(title: str, description: str):
    # Use Rich Rule for full-width horizontal lines
    _console.print(Rule(style="bold cyan", characters="="))
    _console.print(f"[bold white]{title}")
    _console.print(f"[grey70]{description}")
    _console.print(Rule(style="bold cyan", characters="="))

from agents import function_tool

@function_tool
def report_agent_start(title: str, description: str):
    """Imprime encabezado destacado al inicio de un agente."""
    print_header(title, description)
    return f"Inicio reportado para agente {title}"