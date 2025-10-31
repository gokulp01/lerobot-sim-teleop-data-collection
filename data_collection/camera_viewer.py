import cv2
import numpy as np


class CameraViewer:
    def __init__(self, show_front=True, show_top=True):
        self.show_front = show_front
        self.show_top = show_top
        self.window_created = False
    
    def update(self, observation):
        if "image_front" not in observation and "image_top" not in observation:
            return
        
        images = []
        
        if self.show_front and "image_front" in observation:
            front_img = observation["image_front"]
            front_bgr = cv2.cvtColor(front_img, cv2.COLOR_RGB2BGR)
            front_bgr = cv2.resize(front_bgr, (480, 360))
            
            cv2.putText(front_bgr, "Front Camera", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            images.append(front_bgr)
        
        if self.show_top and "image_top" in observation:
            top_img = observation["image_top"]
            top_bgr = cv2.cvtColor(top_img, cv2.COLOR_RGB2BGR)
            top_bgr = cv2.resize(top_bgr, (480, 360))
            
            cv2.putText(top_bgr, "Top Camera", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            images.append(top_bgr)
        
        if len(images) == 0:
            return
        
        if len(images) == 1:
            combined = images[0]
        else:
            combined = np.hstack(images)
        
        cv2.imshow("Robot Camera Views", combined)
        cv2.waitKey(1)
        
        self.window_created = True
    
    def close(self):
        if self.window_created:
            cv2.destroyAllWindows()

