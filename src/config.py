import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Google Auth (Env var method)
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
    
    # Server Auth
    MCP_SERVER_TOKEN = os.getenv("MCP_SERVER_TOKEN", "google-tasks-token")
    PORT = int(os.getenv("PORT", "3333"))
    HOST = os.getenv("HOST", "0.0.0.0") # Bind to all interfaces for Docker
