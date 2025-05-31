from supabase import Client, create_client, StorageException
import os


SUPABASE_PUBLIC_URL=os.getenv('SUPABASE_URL')
SUPABASE_PUBLIC_KEY=os.getenv('SUPABASE_KEY')
SUPABASE_BUCKET = "meal_images"  
supabase: Client = create_client(SUPABASE_PUBLIC_URL, SUPABASE_PUBLIC_KEY)