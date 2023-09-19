import os
from supabase import create_client, Client

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')

supabase: Client = create_client(url, key, options={'timeout': 10})

def supabase_upload(filepath):
    with open(filepath, 'rb+') as f:
        response = supabase.storage.from_('lsc_bucket').upload(filepath, f)
        
    return response

def supabase_download(filename):
    data = supabase.storage.from_('lsc_bucket').download(filename)
    
    return data

def supabase_get_url(filename):
    return supabase.storage.from_('lsc_bucket').get_public_url(filename)