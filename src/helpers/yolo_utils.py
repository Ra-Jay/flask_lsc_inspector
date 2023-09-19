# For demo purposes only
import os

from ultralytics import YOLO

# For demo purposes only
DEMO_WEIGHTS_FOLDER = os.path.join('src', 'static', 'pre-trained_weights', 'yolov8s', 'lsc_v1.pt')

# When an image has been uploaded, it will preview in the frontend and will be saved in the uploads folder
UPLOADS_FOLDER = os.path.join('src', 'static', 'uploads')

def demo_analyze_image(filename):
    model = YOLO(DEMO_WEIGHTS_FOLDER)
    
    file_path = os.path.join(UPLOADS_FOLDER, filename)
    
    result = model.predict(
        source=file_path, 
        show=False, 
        conf=0.20,
        save=False
    )
    
    return result
  
# Using the custom weights of the user that was retreived from the database through their user_id.
def custom_analyze_image(filename, custom_weights):
    
    # TODO: Download custom weights from the url attribute of the custom_weights object to use as parameter for the YOLO object. [RESEARCHING]
    model = YOLO(DEMO_WEIGHTS_FOLDER)
    
    file_path = os.path.join(UPLOADS_FOLDER, filename)
    
    result = model.predict(
        source=file_path, 
        show=False, 
        conf=0.20,
        save=False
    )
    
    return result