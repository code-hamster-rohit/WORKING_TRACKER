import os
import io, json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from db.rules import get_all, add, update

# If modifying these scopes, delete the token from MongoDB.
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_gdrive_service():
    """Shows basic usage of the Drive v3 API."""
    creds = None
    
    # Try to load token from MongoDB
    tokens = get_all("WORKING_TRACKER", "GDRIVE_TOKENS", {})
    if tokens:
        token_data = tokens[0]
        # Remove mongo _id for credentials initialization
        token_data.pop('_id', None)
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Update token in MongoDB
            if tokens:
                token_data = json.loads(creds.to_json())
                update("WORKING_TRACKER", "GDRIVE_TOKENS", {}, token_data)
        else:
            # We must have credentials.json to do the initial flow
            creds_json_str = os.environ.get("GCP_OAUTH_CREDENTIALS_JSON")
            if creds_json_str:
                creds_dict = json.loads(creds_json_str)
                flow = InstalledAppFlow.from_client_config(creds_dict, SCOPES)
            elif os.path.exists('credentials.json'):
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            else:
                raise Exception("Missing OAuth credentials. Provide GCP_OAUTH_CREDENTIALS_JSON or credentials.json")
            
            creds = flow.run_local_server(port=0)
            
            # Save token to MongoDB
            token_data = json.loads(creds.to_json())
            if tokens:
                update("WORKING_TRACKER", "GDRIVE_TOKENS", {}, token_data)
            else:
                add("WORKING_TRACKER", "GDRIVE_TOKENS", token_data)

    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(service, folder_name="WorkingTrackerBackups"):
    # Search for the folder
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='nextPageToken, files(id, name, shared)').execute()
    items = results.get('files', [])
    
    if items:
        # Prefer the folder shared by the user over one created by the bot
        for item in items:
            if item.get('shared', False):
                return item['id']
        return items[0]['id']
    else:
        # Create the folder
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')

def upload_file(filepath, filename):
    service = get_gdrive_service()
    folder_id = get_or_create_folder(service)
    
    file_metadata = {'name': filename, 'parents': [folder_id]}
    media = MediaFileUpload(filepath, mimetype='application/zip')
    
    # Check if a file with this name already exists and delete/update it
    results = service.files().list(q=f"name='{filename}' and '{folder_id}' in parents and trashed=false",
                                   spaces='drive',
                                   fields='nextPageToken, files(id, name)').execute()
    items = results.get('files', [])
    
    if items:
        # Update existing file
        file_id = items[0]['id']
        file = service.files().update(fileId=file_id, media_body=media).execute()
        return file.get('id')
    else:
        # Create new file
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

def download_file(filename, destination_path):
    service = get_gdrive_service()
    folder_id = get_or_create_folder(service)
    
    results = service.files().list(q=f"name='{filename}' and '{folder_id}' in parents and trashed=false",
                                   spaces='drive',
                                   fields='nextPageToken, files(id, name)').execute()
    items = results.get('files', [])
    if not items:
        return False
        
    file_id = items[0]['id']
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    return True

def get_available_backup_months():
    try:
        service = get_gdrive_service()
        folder_id = get_or_create_folder(service)
        results = service.files().list(q=f"name contains 'backup_' and name contains '.zip' and '{folder_id}' in parents and trashed=false",
                                       spaces='drive',
                                       fields='files(id, name)').execute()
        files = results.get('files', [])
        months = []
        for f in files:
            name = f['name']
            if name.startswith('backup_') and name.endswith('.zip'):
                months.append(name.replace('backup_', '').replace('.zip', ''))
        return sorted(months)
    except Exception as e:
        print("Error fetching backup months:", e)
        return []
