from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich import box

from ..config import ENVIRONMENTS

console = Console()


def show_welcome():
    console.clear()
    
    welcome = Text()
    welcome.append("🤖 ", style="bold yellow")
    welcome.append("Robot Data Collection System", style="bold cyan")
    welcome.append(" 🎮", style="bold yellow")
    
    panel = Panel(welcome, box=box.DOUBLE, border_style="bright_cyan", padding=(1, 2))
    console.print(panel)
    console.print()


def select_environment():
    console.print("[bold cyan]📦 Available Environments:[/bold cyan]\n")
    
    table = Table(box=box.SIMPLE_HEAVY, border_style="cyan")
    table.add_column("#", style="bold yellow", width=4)
    table.add_column("Environment", style="bold green", width=20)
    table.add_column("Task Description", style="white")
    
    for num, (env_name, desc) in ENVIRONMENTS.items():
        table.add_row(num, env_name, desc)
    
    console.print(table)
    console.print()
    
    choice = Prompt.ask(
        "[bold cyan]Select environment[/bold cyan]",
        choices=list(ENVIRONMENTS.keys()),
        default="1"
    )
    
    return ENVIRONMENTS[choice][0]


def select_control_method(keyboard_available, controller_available, has_recordings):
    console.print("\n[bold cyan]🎮 Control Methods:[/bold cyan]\n")
    
    methods = []
    method_map = {}
    
    if keyboard_available:
        methods.append(("1", "⌨️  Keyboard", "Use QWEASD keys for joint control"))
        method_map["1"] = "keyboard"
    
    if controller_available:
        methods.append(("2", "🎮 Game Controller", "Use Switch/Xbox/PS controller"))
        method_map["2"] = "controller"
    
    if has_recordings:
        methods.append(("3", "📼 Replay Recording", "Play back collected demonstrations"))
        method_map["3"] = "replay"
    
    methods.append(("4", "👁️  Watch Only", "No control - just observe simulation"))
    method_map["4"] = "watch"
    
    table = Table(box=box.SIMPLE_HEAVY, border_style="cyan")
    table.add_column("#", style="bold yellow", width=4)
    table.add_column("Method", style="bold green", width=20)
    table.add_column("Description", style="white")
    
    for num, method, desc in methods:
        table.add_row(num, method, desc)
    
    console.print(table)
    console.print()
    
    choice = Prompt.ask(
        "[bold cyan]Select control method[/bold cyan]",
        choices=list(method_map.keys()),
        default="1" if keyboard_available else "4"
    )
    
    return method_map[choice]


def select_recording(recordings):
    console.print("\n[bold cyan]📼 Available Recordings:[/bold cyan]\n")
    
    table = Table(box=box.SIMPLE_HEAVY, border_style="cyan")
    table.add_column("#", style="bold yellow", width=4)
    table.add_column("Date/Time", style="bold green", width=18)
    table.add_column("Environment", style="cyan", width=18)
    table.add_column("Episodes", style="white", width=10)
    table.add_column("Steps", style="white", width=10)
    
    for i, rec in enumerate(recordings, 1):
        date_str = rec["date"].strftime("%Y-%m-%d %H:%M")
        table.add_row(
            str(i),
            date_str,
            rec["env_name"],
            str(rec["num_episodes"]),
            str(rec["total_steps"])
        )
    
    console.print(table)
    console.print()
    
    choices = [str(i) for i in range(1, len(recordings) + 1)]
    choice = Prompt.ask(
        "[bold cyan]Select recording[/bold cyan]",
        choices=choices,
        default="1"
    )
    
    return recordings[int(choice) - 1]

