import time

from .base import BaseController


class WatchController(BaseController):
    def __init__(self, env):
        super().__init__(env)
        self.interrupted = False
    
    def get_action(self, observation):
        return self.env.action_space.sample()
    
    def should_reset(self):
        return False
    
    def should_exit(self):
        return self.interrupted
    
    def get_status_text(self):
        return (f"[cyan]Episode:[/cyan] {self.episode}  "
                f"[green]Reward:[/green] {self.reward:+.3f}  "
                f"[yellow]Mode:[/yellow] Random Actions")
    
    def tick(self):
        time.sleep(0.02)
    
    def cleanup(self):
        pass

