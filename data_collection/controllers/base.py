from abc import ABC, abstractmethod


class BaseController(ABC):
    def __init__(self, env):
        self.env = env
        self.running = True
        self.episode = 1
        self.reward = 0.0
    
    @abstractmethod
    def get_action(self, observation):
        pass
    
    @abstractmethod
    def should_reset(self):
        pass
    
    @abstractmethod
    def should_exit(self):
        pass
    
    @abstractmethod
    def get_status_text(self):
        pass
    
    @abstractmethod
    def cleanup(self):
        pass

