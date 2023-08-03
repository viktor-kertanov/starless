import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from config import settings

# If modifying these scopes, delete the file credentials/token.json
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/youtube']

def get_creds():
    creds = None
    if os.path.exists(f'{settings.google_creds_folder}token.json'):
        creds = Credentials.from_authorized_user_file(f'{settings.google_creds_folder}token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as e:
                print(f"Error refreshing credentials: {e}")
                raise
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                f'{settings.google_creds_folder}credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(f'{settings.google_creds_folder}token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds


if __name__ == '__main__':
    get_creds()