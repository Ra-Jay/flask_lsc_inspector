import os
from ultralytics import YOLO

# For demo purposes only
DEMO_WEIGHTS_FOLDER = os.path.join('src', 'static', 'pre-trained_weights', 'yolov8s', 'lsc_v1.pt')

# Assuming if the group will only showcase the LSC model.
def demo_analyze_image(file_url):
    """
    Analyzes the image using the pre-trained weights of the LSC model.
    
    Parameters:
        `file_url`: The url of the image that you want to analyze.
        
    Returns:
        `result`: List of result object from YOLO.
    """
    model = YOLO(DEMO_WEIGHTS_FOLDER)
    result = model.predict(
        source=file_url, 
        show=False, 
        conf=0.20,
        save=False
    )
    return result
  
# Using the custom weights of the user that was retreived from the database through their user_id.
# Assuming if YOLO allows url as a parameter for the weights. Otherwise, just download the weights locally.
def custom_analyze_image(file_url, custom_weights_url):
    """
    Analyzes the image using the custom weights of the user.
    
    Parameters:
        `file_url`: The url of the image that you want to analyze.
        
        `custom_weights_url`: The url of the custom weights of the user.
        
    Returns:
        `result`: List of result object from YOLO.
    """
    model = YOLO(custom_weights_url)
    result = model.predict(
        source=file_url, 
        show=False, 
        conf=0.20,
        save=False
    )
    return result