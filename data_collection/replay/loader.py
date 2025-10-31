import numpy as np
from pathlib import Path
from datetime import datetime


def list_recordings(data_dir="collected_data"):
    data_path = Path(data_dir)
    
    if not data_path.exists():
        return []
    
    recordings = []
    for file in sorted(data_path.glob("*.npz"), reverse=True):
        try:
            data = np.load(file, allow_pickle=True)
            
            env_name = str(data["env_name"])
            control_method = str(data["control_method"])
            num_episodes = int(data["num_episodes"])
            timestamp = str(data["timestamp"])
            
            total_steps = 0
            for i in range(num_episodes):
                obs = data[f"episode_{i}_observations"]
                total_steps += len(obs)
            
            recordings.append({
                "filename": file.name,
                "filepath": str(file),
                "env_name": env_name,
                "control_method": control_method,
                "num_episodes": num_episodes,
                "total_steps": total_steps,
                "timestamp": timestamp,
                "date": datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            })
        except Exception:
            continue
    
    return recordings


def load_recording(filepath):
    data = np.load(filepath, allow_pickle=True)
    
    num_episodes = int(data["num_episodes"])
    episodes = []
    
    for i in range(num_episodes):
        episode = {
            "observations": data[f"episode_{i}_observations"],
            "actions": data[f"episode_{i}_actions"],
            "rewards": data[f"episode_{i}_rewards"],
            "timestamps": data[f"episode_{i}_timestamps"]
        }
        episodes.append(episode)
    
    return {
        "env_name": str(data["env_name"]),
        "control_method": str(data["control_method"]),
        "num_episodes": num_episodes,
        "episodes": episodes
    }

