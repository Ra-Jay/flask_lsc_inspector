from flask import current_app
from supabase import create_client, Client

def get_bucket_type(bucket):
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

def upload_file_to_bucket(bucket, file_name, file):
    """
    Uploads a file to a specified bucket.
    
    Parameters:
        `bucket`: The name of the bucket where you want to upload the file.
        
        `filepath`: The path to the file that you want to upload to the bucket.
        
    Returns:
        `JSON Response`: The response from the supabase server.
    """
    # Check if image extension if png or jpeg
    supabase: Client = create_client(current_app.config['SUPABASE_URL'], current_app.config['SUPABASE_KEY'])
    
    if file_name.endswith('.png'):
        return supabase.storage.from_(bucket).upload(file_name, file, {"content-type": "image/png"})
    elif file_name.endswith('.jpg') or file_name.endswith('.jpeg'):
        return supabase.storage.from_(bucket).upload(file_name, file, {"content-type": "image/jpeg"})

def download_file_from_bucket(bucket, file_name):
    """
    Downloads a file from a specified bucket.
    
    Parameters:
        `bucket`: The name of the bucket where you want to download the file.
        
        `filename`: The name of the file that you want to download from the bucket.
        
    Returns:
        `bytes`: The file data in bytes.
    """
    supabase: Client = create_client(current_app.config['SUPABASE_URL'], current_app.config['SUPABASE_KEY'])
    return supabase.storage.from_(get_bucket_type(bucket)).download(file_name)

def get_file_url_by_name(bucket, file_name):
    """
    Gets the public url of a file from a specified bucket.
    
    Parameters:
        `bucket`: The name of the bucket where you want to get the file url.
        
        `filename`: The name of the file that you want to get the url from the bucket.
        
    Returns:
        `str`: The public url of the file.
    """
    supabase: Client = create_client(current_app.config['SUPABASE_URL'], current_app.config['SUPABASE_KEY'])
    return supabase.storage.from_(get_bucket_type(bucket)).get_public_url(file_name)

def get_all_files_from_bucket(bucket):
    """
    Gets all the files from a specified bucket.
    
    Parameters:
        `bucket`: The name of the bucket where you want to get all the files.
        
    Returns:
        `list[dict[str, str]]`: A list of dictionaries containing the file name and url.
    """
    supabase: Client = create_client(current_app.config['SUPABASE_URL'], current_app.config['SUPABASE_KEY'])
    return supabase.storage.from_(get_bucket_type(bucket)).list()

def delete_file_by_name(bucket, file_name):
    """
    Deletes a file from a specified bucket.
    
    Parameters:
        `bucket`: The name of the bucket where you want to delete the file.
        
        `filename`: The name of the file that you want to delete from the bucket.
        
    Returns:
        `JSON Response`: The response from the supabase server.
    """
    supabase: Client = create_client(current_app.config['SUPABASE_URL'], current_app.config['SUPABASE_KEY'])
    return supabase.storage.from_(get_bucket_type(bucket)).remove(file_name)