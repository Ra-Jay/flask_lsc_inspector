from flask import current_app, jsonify
from supabase import create_client

def get_bucket_type(bucket : str):
    """
    Gets the bucket type from the bucket name.
    
    Parameters:
        `bucket`: The bucket name that the user want to get the type.
        
    Returns:
        `str`: The bucket type.
    """
    return current_app.config.get(f"SUPABASE_BUCKET_{bucket}")

def upload_file_to_bucket(bucket : str, name : str, data : bytes):
    """
    Uploads a file to a specified bucket.
    
    Parameters:
        `bucket`: The bucket name that the user want to upload the file.
        
        `name`: The name of the file.
        
        `data`: The data of the file as bytes.
        
    Returns:
        `str`: The public url of the file.
        
        `JSON Supabase Response`: If there is an error while uploading the file to Supabase.
    """
    try:
        supabase = create_client(current_app.config['SUPABASE_URL'], current_app.config['SUPABASE_KEY'])
        content_type = {"content-type": f"image/{name.split('.')[-1]}"}
        supabase.storage.from_(get_bucket_type(bucket)).upload(name, data, content_type)
        return get_file_url_by_name(bucket, name)
    except Exception as e:
        return jsonify({
            'error': e.args[0]['error'] + '.',
            'message': 'Failed to upload the file to the bucket. File URL retrieval failed.'
        }), e.args[0]['statusCode']

def get_file_url_by_name(bucket : str, name : str):
    """
    Gets the public url of a file from a specified bucket.
    
    Parameters:
        `bucket`: The bucket name that the user want to get the file.
        
        `name`: The name of the file.
        
    Returns:
        `str`: The public url of the file.
        
        `JSON Supabase Response`: If there is an error while getting the file url from Supabase.
    """
    try:
        supabase = create_client(current_app.config['SUPABASE_URL'], current_app.config['SUPABASE_KEY'])
        return supabase.storage.from_(get_bucket_type(bucket)).get_public_url(name)
    except Exception as e:
        return jsonify({
            'error': e.args[0]['error'] + '.',
            'message': 'File URL retrieval failed.'
        }), e.args[0]['statusCode']

def delete_file_by_name(bucket : str, name : str):
    """
    Deletes a file from a specified bucket.
    
    Parameters:
        `bucket`: The bucket name that the user want to delete the file.
        
        `name`: The name of the file.
        
    Returns:
        `JSON Response (200)`: The response from the server with the file details.
    
        `JSON Supabase Response`: If there is an error while deleting the file from Supabase.
    """
    try:
        supabase = create_client(current_app.config['SUPABASE_URL'], current_app.config['SUPABASE_KEY'])
        return supabase.storage.from_(get_bucket_type(bucket)).remove(name)
    except Exception as e:
        return jsonify({
            'error': e.args[0]['error'] + '.',
            'message': 'File deletion failed.'
        }), e.args[0]['statusCode']