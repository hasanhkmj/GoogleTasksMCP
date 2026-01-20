import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Scopes required by the API
SCOPES = ['https://www.googleapis.com/auth/tasks']

def get_service():
    """Shows basic usage of the Tasks API.
    Returns the service object.
    """
    creds = None
    
    # 1. Try Environment Variables (Matching JS implementation)
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    refresh_token = os.environ.get('GOOGLE_REFRESH_TOKEN')
    
    if client_id and client_secret and refresh_token:
        creds = Credentials(
            None, # access_token (will be refreshed)
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=SCOPES
        )
    
    # 2. Try File-based Token (Standard Python Flow)
    if not creds and os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # 3. If no valid creds, and we have credentials.json, run the flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None # Force re-auth
        
        if not creds:
            if os.path.exists('credentials.json') and not (client_id and refresh_token): # Only if not using Env Vars
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            elif not client_id:
                 raise ValueError("Missing Authentication Configuration. Please provide GOOGLE_CLIENT_ID/SECRET/REFRESH_TOKEN env vars or credentials.json")

    return build('tasks', 'v1', credentials=creds)
