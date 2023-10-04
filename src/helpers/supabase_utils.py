from flask import current_app, jsonify
from supabase import create_client, Client

def get_bucket_type(bucket : str):
    """
    Gets the bucket type from the bucket name.
    
    Parameters:
        `bucket`: The name of the bucket.
        
    Returns:
        `str`: The bucket type.
    """
    if bucket == 'lsc_files':
        return current_app.config['SUPABASE_BUCKET_FILES']
    elif bucket == 'lsc_profile_images':
        return current_app.config['SUPABASE_BUCKET_PROFILE_IMAGES']
    else:
        return None

def upload_file_to_bucket(bucket : str, name : str, data : str):
    """
    Uploads a file to a specified bucket.
    
    Parameters:
        `bucket`: The name of the bucket where you want to upload the file.
        
        `name`: The name of the file that you want to upload to the bucket.
        
        `data`: The data of the file that you want to upload to the bucket.
        
    Returns:
        `str`: The public url of the file if the file is uploaded successfully.
        
        `JSON Response`: If an error occurs from the supabase server.
    """
    try:
        supabase: Client = create_client(current_app.config['SUPABASE_URL'], current_app.config['SUPABASE_KEY'])
        global response
        
        if name.endswith('.png'):
            response = supabase.storage.from_(bucket).upload(name, data, {"content-type": "image/png"})
        elif name.endswith('.jpg') or name.endswith('.jpeg'):
            response = supabase.storage.from_(bucket).upload(name, data, {"content-type": "image/jpeg"})
            
        return get_file_url_by_name(bucket, name)
    except Exception as e:
        return jsonify({
            'error': e.args[0]['error'] + '.',
            'message': 'Failed to upload the file to the bucket. File URL retrieval failed.'
        }), e.args[0]['statusCode']
    

def download_file_from_bucket(bucket : str, name : str):
    """
    Downloads a file from a specified bucket.
    
    Parameters:
        `bucket`: The name of the bucket where you want to download the file.
        
        `name`: The name of the file that you want to download from the bucket.
        
    Returns:
        `bytes`: The file data to be saved.
        
        `JSON Response`: If an error occurs from the supabase server.
    """
    try:
        supabase: Client = create_client(current_app.config['SUPABASE_URL'], current_app.config['SUPABASE_KEY'])
        return supabase.storage.from_(get_bucket_type(bucket)).download(name)
    except Exception as e:
        return jsonify({
            'error': e.args[0]['error'] + '.',
            'message': 'File download failed.'
        }), e.args[0]['statusCode']

def get_file_url_by_name(bucket : str, name : str):
    """
    Gets the public url of a file from a specified bucket.
    
    Parameters:
        `bucket`: The name of the bucket where you want to get the file url.
        
        `name`: The name of the file that you want to get the url from the bucket.
        
    Returns:
        `str`: The public url of the file.
        
        `JSON Response`: If an error occurs from the supabase server.
    """
    try:
        supabase: Client = create_client(current_app.config['SUPABASE_URL'], current_app.config['SUPABASE_KEY'])
        return supabase.storage.from_(get_bucket_type(bucket)).get_public_url(name)
    except Exception as e:
        return jsonify({
            'error': e.args[0]['error'] + '.',
            'message': 'File URL retrieval failed.'
        }), e.args[0]['statusCode']
    
def get_all_files_from_bucket(bucket : str):
    """
    Gets all the files from a specified bucket.
    
    Parameters:
        `bucket`: The name of the bucket where you want to get all the files.
        
    Returns:
        `list[dict[str, str]]`: A list of dictionaries containing the file name and url.
        
        `JSON Response`: If an error occurs from the supabase server.
    """
    try:
        supabase: Client = create_client(current_app.config['SUPABASE_URL'], current_app.config['SUPABASE_KEY'])
        return supabase.storage.from_(get_bucket_type(bucket)).list()
    except Exception as e:
        return jsonify({
            'error': e.args[0]['error'] + '.',
            'message': 'Files retrieval failed.'
        }), e.args[0]['statusCode']

def delete_file_by_name(bucket : str, name : str):
    """
    Deletes a file from a specified bucket.
    
    Parameters:
        `bucket`: The name of the bucket where you want to delete the file.
        
        `name`: The name of the file that you want to delete from the bucket.
        
    Returns:
        `dict[str, str]`: A dictionary containing the file name and url.
        
        `JSON Response`: If an error occurs from the supabase server.
    """
    try:
        supabase: Client = create_client(current_app.config['SUPABASE_URL'], current_app.config['SUPABASE_KEY'])
        return supabase.storage.from_(get_bucket_type(bucket)).remove(name)
    except Exception as e:
        return jsonify({
            'error': e.args[0]['error'] + '.',
            'message': 'File deletion failed.'
        }), e.args[0]['statusCode']