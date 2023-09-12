import os
from ultralytics import YOLO
from datetime import datetime
from src.controllers.weights import get_weight

def demo_analyze_image(filename):
    model = YOLO('src\\pre-trained_weights\\yolov8s\\lsc_v1.pt')
    
    #TODO: Get the file path of the image from the filename parameter instead of predefining the address of the file.
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
  
def custom_analyze_image(filename):
  
    # TODO: Get the id of the selected custom weights of the user.
    custom_weights = get_weight(id)
    # TODO: Download custom weights from the url attribute of the custom_weights object to use as parameter for the YOLO object.
    model = YOLO('src\\pre-trained_weights\\yolov8s\\lsc_v1.pt')
    
    #TODO: Get the file path of the image from the filename parameter instead of predefining the address of the file.
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