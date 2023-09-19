import os
from supabase import create_client, Client

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
files = os.environ.get('SUPABASE_BUCKET_FILES')
weights = os.environ.get('SUPABASE_BUCKET_WEIGHTS')
profile_images = os.environ.get('SUPABASE_BUCKET_PROFILE_IMAGES')

supabase: Client = create_client(url, key)

def get_bucket_type(bucket):
    if bucket == 'files':
        return files
    elif bucket == 'weights':
        return weights
    elif bucket == 'profile_images':
        return profile_images
    else:
        return None

def upload_file_to_bucket(bucket, filepath):
    with open(filepath, 'rb+') as f:
        response = supabase.storage.from_(get_bucket_type(bucket)).upload(filepath, f)
        
    return response

def download_file_from_bucket(bucket, filename):
    data = supabase.storage.from_(get_bucket_type(bucket)).download(filename)
    
    return data

def get_file_url_by_name(bucket, filename):
    return supabase.storage.from_(get_bucket_type(bucket)).get_public_url(filename)

def get_all_files_from_bucket(bucket):
    return supabase.storage.from_(get_bucket_type(bucket)).list()

def delete_file_by_name(bucket, filename):
    return supabase.storage.from_(get_bucket_type(bucket)).remove(filename)