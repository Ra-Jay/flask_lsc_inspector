import os
from supabase import create_client, Client

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
files = os.environ.get('SUPABASE_BUCKET_FILES')
weights = os.environ.get('SUPABASE_BUCKET_WEIGHTS')
profile_images = os.environ.get('SUPABASE_BUCKET_PROFILE_IMAGES')

supabase: Client = create_client(url, key)

def get_bucket_type(bucket):
    """
    Gets the bucket type from the bucket name.
    
    Parameters:
        `bucket`: The name of the bucket.
        
    Returns:
        `str`: The bucket type.
    """
    if bucket == 'files':
        return files
    elif bucket == 'weights':
        return weights
    elif bucket == 'profile_images':
        return profile_images
    else:
        return None

def upload_file_to_bucket(bucket, filepath):
    """
    Uploads a file to a specified bucket.
    
    Parameters:
        `bucket`: The name of the bucket where you want to upload the file.
        
        `filepath`: The path to the file that you want to upload to the bucket.
        
    Returns:
        `JSON Response`: The response from the supabase server.
    """
    with open(filepath, 'rb+') as f:
        response = supabase.storage.from_(get_bucket_type(bucket)).upload(filepath, f)
    return response

def download_file_from_bucket(bucket, filename):
    """
    Downloads a file from a specified bucket.
    
    Parameters:
        `bucket`: The name of the bucket where you want to download the file.
        
        `filename`: The name of the file that you want to download from the bucket.
        
    Returns:
        `bytes`: The file data in bytes.
    """
    data = supabase.storage.from_(get_bucket_type(bucket)).download(filename)
    return data

def get_file_url_by_name(bucket, filename):
    """
    Gets the public url of a file from a specified bucket.
    
    Parameters:
        `bucket`: The name of the bucket where you want to get the file url.
        
        `filename`: The name of the file that you want to get the url from the bucket.
        
    Returns:
        `str`: The public url of the file.
    """
    return supabase.storage.from_(get_bucket_type(bucket)).get_public_url(filename)

def get_all_files_from_bucket(bucket):
    """
    Gets all the files from a specified bucket.
    
    Parameters:
        `bucket`: The name of the bucket where you want to get all the files.
        
    Returns:
        `list[dict[str, str]]`: A list of dictionaries containing the file name and url.
    """
    return supabase.storage.from_(get_bucket_type(bucket)).list()

def delete_file_by_name(bucket, filename):
    """
    Deletes a file from a specified bucket.
    
    Parameters:
        `bucket`: The name of the bucket where you want to delete the file.
        
        `filename`: The name of the file that you want to delete from the bucket.
        
    Returns:
        `JSON Response`: The response from the supabase server.
    """
    return supabase.storage.from_(get_bucket_type(bucket)).remove(filename)