import os
from ultralytics import YOLO
from src.controllers.weights import get_weight

# For demo purposes only
DEMO_WEIGHTS_FOLDER = os.path.join('src', 'static', 'pre-trained_weights', 'yolov8s', 'lsc_v1.pt')

# When an image has been uploaded, it will preview in the frontend and will be saved in the uploads folder
UPLOADS_FOLDER = os.path.join('src', 'static', 'uploads')

def demo_analyze_image(filename):
    model = YOLO(DEMO_WEIGHTS_FOLDER)
    
    # TODO: Get the file path of the image from the filename parameter instead of predefining the address of the file. [DISCONTINUED]
    # (May need how the NextJS app will send the file to the backend) [DISCONTINUED]
    file_path = os.path.join(UPLOADS_FOLDER, filename)
    
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
    model = YOLO(DEMO_WEIGHTS_FOLDER)
    
    # TODO: Get the file path of the image from the filename parameter instead of predefining the address of the file. [DISCONTINUED]
    # (May need how the NextJS app will send the file to the backend) [DISCONTINUED]
    file_path = os.path.join(UPLOADS_FOLDER, filename)
    
    result = model.predict(
        source=file_path, 
        show=False, 
        conf=0.20,
        save=False
    )
    
    return result