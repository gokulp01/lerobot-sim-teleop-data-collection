import numpy as np
import pygame

from .base import BaseController
from ..config import JOINT_LIMITS_LOW, JOINT_LIMITS_HIGH, DEAD_ZONE_THRESHOLD


class GamepadController(BaseController):
    def __init__(self, env):
        super().__init__(env)
        
        pygame.init()
        pygame.joystick.init()
        
        if pygame.joystick.get_count() == 0:
            raise RuntimeError("No game controller detected")
        
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()
        
        self.target_qpos = None
        self.joint_delta = 0.06
        self.clock = pygame.time.Clock()
    
    def _apply_dead_zone(self, value):
        if abs(value) < DEAD_ZONE_THRESHOLD:
            return 0.0
        sign = 1 if value > 0 else -1
        return sign * (abs(value) - DEAD_ZONE_THRESHOLD) / (1.0 - DEAD_ZONE_THRESHOLD)
    
    def get_action(self, observation):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        
        pygame.event.pump()
        
        if self.target_qpos is None:
            self.target_qpos = observation["arm_qpos"].copy()
        
        current_qpos = observation["arm_qpos"].copy()
        self.target_qpos = current_qpos.copy()
        
        if self.controller.get_numaxes() >= 4:
            left_x = self._apply_dead_zone(self.controller.get_axis(0))
            left_y = self._apply_dead_zone(self.controller.get_axis(1))
            right_y = self._apply_dead_zone(self.controller.get_axis(3) if self.controller.get_numaxes() > 3 else 0)
            right_x = self._apply_dead_zone(self.controller.get_axis(2) if self.controller.get_numaxes() > 2 else 0)
            
            self.target_qpos[0] += left_x * self.joint_delta
            self.target_qpos[1] += -left_y * self.joint_delta
            self.target_qpos[2] += -right_y * self.joint_delta
            self.target_qpos[3] += right_x * self.joint_delta
        
        gripper_close = False
        gripper_open = False
        
        if self.controller.get_numbuttons() > 6:
            gripper_close = self.controller.get_button(6)
        if self.controller.get_numbuttons() > 7:
            gripper_open = self.controller.get_button(7)
        
        if not gripper_close and self.controller.get_numbuttons() > 4:
            gripper_close = self.controller.get_button(4)
        if not gripper_open and self.controller.get_numbuttons() > 5:
            gripper_open = self.controller.get_button(5)
        
        if not gripper_close and not gripper_open and self.controller.get_numaxes() > 4:
            trigger_left = self.controller.get_axis(4)
            trigger_right = self.controller.get_axis(5) if self.controller.get_numaxes() > 5 else 0.0
            
            if trigger_left > 0.5:
                gripper_close = True
            elif trigger_right > 0.5:
                gripper_open = True
        
        if gripper_close:
            self.target_qpos[5] -= 0.1
        elif gripper_open:
            self.target_qpos[5] += 0.1
        
        self.target_qpos = np.clip(self.target_qpos, JOINT_LIMITS_LOW, JOINT_LIMITS_HIGH)
        return self.target_qpos.copy()
    
    def should_reset(self):
        if self.controller.get_numbuttons() > 9 and self.controller.get_button(9):
            self.target_qpos = None
            return True
        return False
    
    def should_exit(self):
        if self.controller.get_numbuttons() > 8 and self.controller.get_button(8):
            return True
        return False
    
    def get_status_text(self):
        if self.target_qpos is None:
            gripper_str = "0.00"
        else:
            gripper_str = f"{self.target_qpos[5]:.2f}"
        
        return (f"[cyan]Episode:[/cyan] {self.episode}  "
                f"[green]Reward:[/green] {self.reward:+.3f}  "
                f"[yellow]Gripper:[/yellow] {gripper_str}")
    
    def tick(self):
        self.clock.tick(50)
    
    def cleanup(self):
        pygame.quit()

