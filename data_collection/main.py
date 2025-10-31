import time
import gymnasium as gym
from rich.console import Console
from rich.panel import Panel
from rich.live import Live

import gym_lowcostrobot
from .config import MAX_EPISODE_STEPS
from .ui import show_welcome, select_environment, select_control_method, select_recording, create_status_display
from .controllers import KeyboardController, GamepadController, WatchController
from .recording import DataRecorder
from .replay import list_recordings, load_recording, ReplayController

console = Console()

try:
    from pynput import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

try:
    import pygame
    CONTROLLER_AVAILABLE = True
except ImportError:
    CONTROLLER_AVAILABLE = False


def run_collection_system():
    show_welcome()
    
    if not KEYBOARD_AVAILABLE:
        console.print("[yellow]⚠️  pynput not installed - keyboard control unavailable[/yellow]")
    if not CONTROLLER_AVAILABLE:
        console.print("[yellow]⚠️  pygame not installed - controller support unavailable[/yellow]")
    
    if not KEYBOARD_AVAILABLE and not CONTROLLER_AVAILABLE:
        console.print("[bold red]Please install: pip install pynput pygame[/bold red]\n")
    
    recordings = list_recordings()
    has_recordings = len(recordings) > 0
    
    env_name = select_environment()
    control_method = select_control_method(KEYBOARD_AVAILABLE, CONTROLLER_AVAILABLE, has_recordings)
    
    recording_data = None
    if control_method == "replay":
        if not has_recordings:
            console.print("[bold red]No recordings found![/bold red]")
            return
        
        selected_recording = select_recording(recordings)
        recording_data = load_recording(selected_recording["filepath"])
        env_name = recording_data["env_name"]
        console.print(f"\n[bold green]✓[/bold green] Loading recording: [cyan]{selected_recording['filename']}[/cyan]\n")
    else:
        console.print(f"\n[bold green]✓[/bold green] Starting [cyan]{env_name}[/cyan] with [yellow]{control_method}[/yellow] control...\n")
    
    console.print("[dim]Viser viewer: http://localhost:8080[/dim]\n")
    time.sleep(1)
    
    try:
        _run_collection(env_name, control_method, recording_data)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
    
    console.print("\n[bold green]✓ Data collection session ended[/bold green]\n")


def _run_collection(env_name, control_method, recording_data=None):
    env = gym.make(env_name, render_mode="human", action_mode="joint")
    
    if hasattr(env, '_max_episode_steps'):
        env._max_episode_steps = MAX_EPISODE_STEPS
    
    observation, info = env.reset()
    
    if control_method == "replay":
        controller = ReplayController(env, recording_data)
        recorder = None
    elif control_method == "keyboard":
        controller = KeyboardController(env)
        recorder = DataRecorder(env_name, control_method)
        recorder.start_episode()
    elif control_method == "controller":
        controller = GamepadController(env)
        recorder = DataRecorder(env_name, control_method)
        recorder.start_episode()
    else:
        controller = WatchController(env)
        recorder = None
    
    layout = create_status_display(control_method)
    
    with Live(layout, console=console, screen=True, refresh_per_second=4):
        while not controller.should_exit():
            if controller.should_reset():
                if recorder:
                    recorder.end_episode()
                    recorder.start_episode()
                
                observation, info = env.reset()
                controller.episode += 1
            
            action = controller.get_action(observation)
            observation, reward, terminated, truncated, info = env.step(action)
            
            controller.reward = reward
            
            if recorder:
                recorder.record_step(observation, action, reward)
            
            status_text = controller.get_status_text()
            layout["status"].update(Panel(status_text, border_style="green"))
            
            if terminated or truncated:
                if recorder:
                    recorder.end_episode()
                    recorder.start_episode()
                
                observation, info = env.reset()
                controller.episode += 1
            
            if hasattr(controller, 'tick'):
                controller.tick()
            else:
                time.sleep(0.01)
    
    controller.cleanup()
    env.close()
    
    if recorder:
        console.print("\n[dim]Finalizing data collection...[/dim]")
        recorder.end_episode()
        
        total_steps = recorder.get_total_steps()
        num_episodes = len(recorder.episodes)
        
        console.print(f"[dim]Debug: Episodes={num_episodes}, Steps={total_steps}[/dim]")
        
        if num_episodes > 0 and total_steps > 0:
            filepath = recorder.save()
            if filepath:
                console.print(f"\n[bold green]✓ Data saved:[/bold green] [cyan]{filepath.name}[/cyan]")
                console.print(f"[dim]Location: {filepath}[/dim]")
                console.print(f"[dim]Episodes: {num_episodes} | Total Steps: {total_steps}[/dim]")
            else:
                console.print("\n[bold red]❌ Failed to save data![/bold red]")
        else:
            console.print(f"\n[yellow]⚠️  No data collected (Episodes: {num_episodes}, Steps: {total_steps})[/yellow]")

