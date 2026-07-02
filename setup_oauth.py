import os
import json
from dotenv import load_dotenv

# Load environment variables (like MONGO_URI) BEFORE importing db modules
load_dotenv()

from google_auth_oauthlib.flow import InstalledAppFlow
from db.rules import get_all, add, update

SCOPES = ['https://www.googleapis.com/auth/drive']

def setup_oauth():
    print("Starting Google Drive OAuth2 Setup...")
    
    if not os.path.exists('credentials.json'):
        print("ERROR: credentials.json not found in the current directory.")
        print("Please download it from Google Cloud Console and place it here.")
        return

    print("Opening browser for authentication...")
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    print("Authentication successful! Saving token to MongoDB...")
    token_data = json.loads(creds.to_json())
    
    tokens = get_all("WORKING_TRACKER", "GDRIVE_TOKENS", {})
    if tokens:
        print("Updating existing token in MongoDB...")
        update("WORKING_TRACKER", "GDRIVE_TOKENS", {}, token_data)
    else:
        print("Adding new token to MongoDB...")
        add("WORKING_TRACKER", "GDRIVE_TOKENS", token_data)
        
    print("Done! The token is now saved in MongoDB.")
    print("Vercel will now automatically use this token to authenticate.")

if __name__ == "__main__":
    setup_oauth()
