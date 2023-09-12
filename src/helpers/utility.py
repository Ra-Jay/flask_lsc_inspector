import os
from ultralytics import YOLO
from datetime import datetime

def analyze_image(filename):
    model = YOLO('src\\pre-trained_weights\\yolov8s\\lsc_v1.pt')
    
    file_path = os.path.join('src\\uploads\\', filename)
    
    now = datetime.now()
    date_time_str = now.strftime('%Y-%m-%d_%H-%M')
    
    result = model.predict(
        source=file_path, 
        show=False, 
        conf=0.20, 
        project="src/predictions", 
        name=date_time_str, save=True
    )
    
    result[0].path = "src/predictions/" + date_time_str + "/" + filename
    
    return result