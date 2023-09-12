import os
from ultralytics import YOLO
from datetime import datetime

def analyze_image(filename):
    # If available na ang custom weights upload [FEATURE], 
    # use the filepath/filename to load the custom weights instead.
    model = YOLO('src\\pre-trained_weights\\yolov8s\\lsc_v1.pt')
    
    file_path = os.path.join('src\\uploads\\', filename)
    
    now = datetime.now()
    date_time_str = now.strftime('%Y-%m-%d_%H-%M')
    
    result = model.predict(
        source=file_path, 
        show=False, 
        conf=0.20,
        name=date_time_str,
        save=False
    )
    
    return result