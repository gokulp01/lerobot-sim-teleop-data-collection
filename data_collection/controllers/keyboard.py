import numpy as np
from pynput import keyboard

from .base import BaseController
from ..config import JOINT_LIMITS_LOW, JOINT_LIMITS_HIGH


class KeyboardController(BaseController):
    def __init__(self, env):
        super().__init__(env)
        self.keys_pressed = set()
        self.target_qpos = None
        self.joint_delta = 0.05
        self.reset_requested = False
        self.exit_requested = False
        
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
    
    def _on_press(self, key):
        try:
            k = key.char.lower() if hasattr(key, 'char') and key.char else None
            if k:
                self.keys_pressed.add(k)
            elif key == keyboard.Key.space:
                self.reset_requested = True
            elif key == keyboard.Key.esc:
                self.exit_requested = True
        except:
            pass
    
    def _on_release(self, key):
        try:
            k = key.char.lower() if hasattr(key, 'char') and key.char else None
            if k and k in self.keys_pressed:
                self.keys_pressed.remove(k)
        except:
            pass
    
    def get_action(self, observation):
        if self.target_qpos is None:
            self.target_qpos = observation["arm_qpos"].copy()
        
        if 'q' in self.keys_pressed: self.target_qpos[0] += self.joint_delta
        if 'a' in self.keys_pressed: self.target_qpos[0] -= self.joint_delta
        if 'w' in self.keys_pressed: self.target_qpos[1] += self.joint_delta
        if 's' in self.keys_pressed: self.target_qpos[1] -= self.joint_delta
        if 'e' in self.keys_pressed: self.target_qpos[2] += self.joint_delta
        if 'd' in self.keys_pressed: self.target_qpos[2] -= self.joint_delta
        if 'r' in self.keys_pressed: self.target_qpos[3] += self.joint_delta
        if 'f' in self.keys_pressed: self.target_qpos[3] -= self.joint_delta
        if 't' in self.keys_pressed: self.target_qpos[4] += self.joint_delta
        if 'g' in self.keys_pressed: self.target_qpos[4] -= self.joint_delta
        if 'y' in self.keys_pressed: self.target_qpos[5] += self.joint_delta
        if 'h' in self.keys_pressed: self.target_qpos[5] -= self.joint_delta
        
        self.target_qpos = np.clip(self.target_qpos, JOINT_LIMITS_LOW, JOINT_LIMITS_HIGH)
        return self.target_qpos.copy()
    
    def should_reset(self):
        if self.reset_requested:
            self.reset_requested = False
            self.target_qpos = None
            return True
        return False
    
    def should_exit(self):
        return self.exit_requested
    
    def get_status_text(self):
        if self.target_qpos is None:
            joints_str = "[0.00, 0.00, 0.00]"
        else:
            joints_str = f"[{self.target_qpos[0]:.2f}, {self.target_qpos[1]:.2f}, {self.target_qpos[2]:.2f}]"
        
        return (f"[cyan]Episode:[/cyan] {self.episode}  "
                f"[green]Reward:[/green] {self.reward:+.3f}  "
                f"[yellow]Joints:[/yellow] {joints_str}")
    
    def cleanup(self):
        self.listener.stop()

