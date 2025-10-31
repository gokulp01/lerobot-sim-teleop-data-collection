from rich.panel import Panel
from rich.layout import Layout
from rich import box


def create_control_panel(control_method):
    if control_method == "keyboard":
        controls_text = """[bold cyan]⌨️  KEYBOARD CONTROLS[/bold cyan]  [dim](Camera: Front+Top)[/dim]

[yellow]Joint Control:[/yellow]
  Q/A → Joint 1 (Shoulder pan)    W/S → Joint 2 (Shoulder lift)
  E/D → Joint 3 (Elbow flex)      R/F → Joint 4 (Wrist flex)
  T/G → Joint 5 (Wrist roll)      Y/H → Joint 6 (Gripper)

[yellow]Special:[/yellow]  SPACE = Reset  |  ESC = Exit"""
    
    elif control_method == "controller":
        controls_text = """[bold cyan]🎮 CONTROLLER CONTROLS[/bold cyan]  [dim](Camera: Front+Top)[/dim]

[yellow]Sticks:[/yellow]
  Left Stick → Joints 1 & 2 (Pan/Lift)
  Right Stick → Joints 3 & 4 (Elbow/Wrist)

[yellow]Triggers:[/yellow]  ZL = Close Gripper  |  ZR = Open Gripper
[yellow]Buttons:[/yellow]  X/Y = Speed  |  Plus = Reset  |  Minus = Exit"""
    
    elif control_method == "replay":
        controls_text = """[bold cyan]📼 REPLAY MODE[/bold cyan]

[yellow]Playing back recorded demonstration[/yellow]

Replaying collected episodes automatically
Press Ctrl+C to exit"""
    
    else:
        controls_text = """[bold cyan]👁️  WATCH MODE[/bold cyan]

[yellow]No controls active - observing random actions[/yellow]

Press Ctrl+C to exit"""
    
    return Panel(controls_text, border_style="bright_blue", box=box.ROUNDED, padding=(0, 2))


def create_status_display(control_method):
    layout = Layout()
    layout.split_column(
        Layout(name="controls", size=9),
        Layout(name="status", size=4),
    )
    layout["controls"].update(create_control_panel(control_method))
    return layout

