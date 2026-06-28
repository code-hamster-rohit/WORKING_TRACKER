import os
import io, json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_gdrive_service():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds_json_str = os.environ.get("GCP_SERVICE_ACCOUNT_JSON")
    if creds_json_str:
        creds_dict = json.loads(creds_json_str)
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    elif os.path.exists('service_account.json'):
        creds = service_account.Credentials.from_service_account_file('service_account.json', scopes=SCOPES)
    else:
        raise Exception("Missing Service Account Credentials. Please set GCP_SERVICE_ACCOUNT_JSON env var or provide service_account.json file.")

    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(service, folder_name="WorkingTrackerBackups"):
    # Search for the folder
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='nextPageToken, files(id, name)').execute()
    items = results.get('files', [])
    
    if items:
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
