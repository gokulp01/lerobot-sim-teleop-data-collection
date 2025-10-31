import numpy as np
from datetime import datetime
from pathlib import Path


class DataRecorder:
    def __init__(self, env_name, control_method, output_dir="collected_data"):
        self.env_name = env_name
        self.control_method = control_method
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.episodes = []
        self.current_episode = {
            "observations": [],
            "actions": [],
            "rewards": [],
            "timestamps": []
        }
        self.episode_start_time = None
    
    def start_episode(self):
        self.current_episode = {
            "observations": [],
            "actions": [],
            "rewards": [],
            "timestamps": [],
            "images_front": [],
            "images_top": []
        }
        self.episode_start_time = datetime.now()
    
    def record_step(self, observation, action, reward):
        if self.episode_start_time is None:
            self.start_episode()
        
        timestamp = (datetime.now() - self.episode_start_time).total_seconds()
        
        self.current_episode["observations"].append(observation["arm_qpos"])
        self.current_episode["actions"].append(action)
        self.current_episode["rewards"].append(reward)
        self.current_episode["timestamps"].append(timestamp)
        
        if "image_front" in observation:
            self.current_episode["images_front"].append(observation["image_front"])
        if "image_top" in observation:
            self.current_episode["images_top"].append(observation["image_top"])
    
    def end_episode(self):
        if len(self.current_episode["observations"]) > 0:
            episode_data = {
                "observations": np.array(self.current_episode["observations"]),
                "actions": np.array(self.current_episode["actions"]),
                "rewards": np.array(self.current_episode["rewards"]),
                "timestamps": np.array(self.current_episode["timestamps"])
            }
            
            if len(self.current_episode["images_front"]) > 0:
                episode_data["images_front"] = np.array(self.current_episode["images_front"], dtype=np.uint8)
            if len(self.current_episode["images_top"]) > 0:
                episode_data["images_top"] = np.array(self.current_episode["images_top"], dtype=np.uint8)
            
            self.episodes.append(episode_data)
    
    def save(self):
        if len(self.episodes) == 0:
            print(f"Warning: No episodes to save")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.env_name}_{self.control_method}_{timestamp}.npz"
        filepath = self.output_dir / filename
        
        print(f"Saving {len(self.episodes)} episodes to {filepath}...")
        
        save_dict = {
            "env_name": self.env_name,
            "control_method": self.control_method,
            "num_episodes": len(self.episodes),
            "timestamp": timestamp,
        }
        
        for i, episode in enumerate(self.episodes):
            save_dict[f"episode_{i}_observations"] = episode["observations"]
            save_dict[f"episode_{i}_actions"] = episode["actions"]
            save_dict[f"episode_{i}_rewards"] = episode["rewards"]
            save_dict[f"episode_{i}_timestamps"] = episode["timestamps"]
            
            if "images_front" in episode:
                save_dict[f"episode_{i}_images_front"] = episode["images_front"]
            if "images_top" in episode:
                save_dict[f"episode_{i}_images_top"] = episode["images_top"]
        
        try:
            np.savez_compressed(filepath, **save_dict)
            print(f"Successfully saved to {filepath}")
            return filepath
        except Exception as e:
            print(f"Error saving file: {e}")
            return None
    
    def get_total_steps(self):
        return sum(len(ep["observations"]) for ep in self.episodes)

