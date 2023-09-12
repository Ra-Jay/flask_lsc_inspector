import os
from ultralytics import YOLO
from src.controllers.weights import get_weight

def demo_analyze_image(filename):
    model = YOLO('src\\pre-trained_weights\\yolov8s\\lsc_v1.pt')
    
    # TODO: Get the file path of the image from the filename parameter instead of predefining the address of the file.
    # (May need how the NextJS app will send the file to the backend)
    file_path = os.path.join('src\\uploads\\', filename)
    
    result = model.predict(
        source=file_path, 
        show=False, 
        conf=0.20,
        save=False
    )
    
    return result
  
def custom_analyze_image(filename):
  
    # TODO: Get the id of the selected/uploaded custom weights of the user. 
    # (This is the id of the custom weights that was returned from handle_weights function, 
    # so it may need to store the weight_id in the session)
    custom_weights = get_weight(id)
    
    # TODO: Download custom weights from the url attribute of the custom_weights object to use as parameter for the YOLO object.
    model = YOLO('src\\pre-trained_weights\\yolov8s\\lsc_v1.pt')
    
    # TODO: Get the file path of the image from the filename parameter instead of predefining the address of the file.
    # (May need how the NextJS app will send the file to the backend)
    file_path = os.path.join('src\\uploads\\', filename)
    
    result = model.predict(
        source=file_path, 
        show=False, 
        conf=0.20,
        save=False
    )
    
    return result