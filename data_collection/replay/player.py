import time
from ..controllers.base import BaseController


class ReplayController(BaseController):
    def __init__(self, env, recording_data):
        super().__init__(env)
        self.episodes = recording_data["episodes"]
        self.current_episode_idx = 0
        self.current_step_idx = 0
        self.paused = False
        self.playback_speed = 1.0
        
        self.start_episode()
    
    def start_episode(self):
        if self.current_episode_idx >= len(self.episodes):
            self.current_episode_idx = 0
        
        self.current_step_idx = 0
        self.episode = 1
    
    def get_action(self, observation):
        if self.current_episode_idx >= len(self.episodes):
            self.current_episode_idx = 0
            self.current_step_idx = 0
        
        episode = self.episodes[self.current_episode_idx]
        
        if self.current_step_idx >= len(episode["actions"]):
            return episode["actions"][-1]
        
        action = episode["actions"][self.current_step_idx]
        self.reward = float(episode["rewards"][self.current_step_idx])
        
        self.current_step_idx += 1
        
        return action
    
    def should_reset(self):
        if self.current_episode_idx >= len(self.episodes):
            return False
        
        episode = self.episodes[self.current_episode_idx]
        
        if self.current_step_idx >= len(episode["actions"]):
            self.current_episode_idx += 1
            self.current_step_idx = 0
            self.episode += 1
            return True
        
        return False
    
    def should_exit(self):
        return self.current_episode_idx >= len(self.episodes)
    
    def get_status_text(self):
        total_episodes = len(self.episodes)
        progress = f"{self.current_episode_idx + 1}/{total_episodes}"
        
        return (f"[cyan]Episode:[/cyan] {progress}  "
                f"[green]Reward:[/green] {self.reward:+.3f}  "
                f"[yellow]Step:[/yellow] {self.current_step_idx}")
    
    def tick(self):
        if self.current_episode_idx < len(self.episodes):
            episode = self.episodes[self.current_episode_idx]
            
            if self.current_step_idx > 0 and self.current_step_idx < len(episode["timestamps"]):
                prev_time = episode["timestamps"][self.current_step_idx - 1]
                curr_time = episode["timestamps"][self.current_step_idx]
                dt = (curr_time - prev_time) / self.playback_speed
                time.sleep(max(0, dt))
            else:
                time.sleep(0.02)
    
    def cleanup(self):
        pass

