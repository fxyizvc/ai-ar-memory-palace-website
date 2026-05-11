import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
# ... (keep existing imports and code)
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from io import BytesIO  # <--- Add this import at the top if missing

def get_drive_service():
    """Helper to get the authenticated service."""
    creds = get_oauth_credentials()
    return build('drive', 'v3', credentials=creds)

def stream_file(file_id):
    """
    Downloads a file into memory to stream it to the user.
    """
    try:
        service = get_drive_service()
        request = service.files().get_media(fileId=file_id)
        
        file_stream = BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        print(f"Error streaming file: {e}")
        return None






# --- GOOGLE DRIVE CONFIGURATION ---
CLIENT_SECRET_FILE = 'credentials.json'        # OAuth client secret file
TOKEN_FILE = 'token.json'                      # Saved login session
TARGET_FOLDER_ID = '1I8JIzIf1ShwFl1OF_MsG4j37wyz06YwF'
SCOPES = ['https://www.googleapis.com/auth/drive.file']
# ----------------------------------


def get_oauth_credentials():
    """Gets OAuth credentials, refreshes or logs in once."""
    creds = None

    # Load existing token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid token → authenticate user
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Auto-refresh
            creds.refresh(Request())
        else:
            # First-time login
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token for next runs
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


def upload_to_drive(filepath, filename, mime_type, folder_id=TARGET_FOLDER_ID):
    """
    Uploads a file to Google Drive folder using OAuth.
    Returns: (webViewLink, fileId)
    """
    try:
        # Authenticate user OAuth
        creds = get_oauth_credentials()
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }

        media = MediaFileUpload(filepath, resumable=True, mimetype=mime_type)

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        file_id = file.get('id')
        web_link = file.get('webViewLink')

        print(f"✅ Drive Upload SUCCESS - {filename}. ID: {file_id}")
        return web_link, file_id

    except HttpError as e:
        print(f"❌ Google Drive API Error (HTTP {e.resp.status}): {e.content}")
        return None, None
    except Exception as e:
        print(f"❌ Generic Error uploading {filename}: {e}")
        return None, None
