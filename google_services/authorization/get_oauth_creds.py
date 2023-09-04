import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from config import settings
from logs.log_config import logger

# If modifying these scopes, delete the file credentials/token.json
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/devstorage.full_control',
    'https://mail.google.com/']

def get_creds():
    '''Our goal is to get the creds needed for Google API calls.
    1) If we don't have token.json, we use credentials.json, taken from Google console and via the consent screen we obtain token.json;
    2) token.json has the info about access token needed for API calls and refresh token, needed to refresh access token when it shortly expires;
    3) So if our access token needed for API calls has expired, the script uses refresh token and obtaines new acces token;
    4) Anyway we must end up with a valid credentials;
    5) Refresh token in Google API must never expire;
    '''
    creds = None
    if os.path.exists(f'{settings.google_creds_folder}token.json'):
        creds = Credentials.from_authorized_user_file(f'{settings.google_creds_folder}token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as e:
                print(f"Error refreshing credentials: {e}")
                flow = InstalledAppFlow.from_client_secrets_file(
                f'{settings.google_creds_folder}credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
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