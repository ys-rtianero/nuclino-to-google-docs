import os
import json
import requests
from typing import Dict, Any, List

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


class NuclinoClient:
    """Client for interacting with the Nuclino API."""

    BASE_URL = "https://api.nuclino.com/v0.5"

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def get_workspace_items(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Return items in a Nuclino workspace."""
        url = f"{self.BASE_URL}/workspaces/{workspace_id}/items"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("data", [])

    def get_item_content(self, item_id: str) -> str:
        """Return content of a Nuclino item."""
        url = f"{self.BASE_URL}/items/{item_id}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        return data.get("body", "")


class GoogleDriveClient:
    """Client for Google Drive and Google Docs APIs."""

    def __init__(self, credentials_path: str):
        scopes = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/documents",
        ]
        creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
        self.drive_service = build("drive", "v3", credentials=creds)
        self.docs_service = build("docs", "v1", credentials=creds)

    def create_folder(self, name: str, parent_id: str = None) -> str:
        """Create a folder on Google Drive and return its ID."""
        file_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            file_metadata["parents"] = [parent_id]
        folder = self.drive_service.files().create(body=file_metadata, fields="id").execute()
        return folder.get("id")

    def create_document(self, name: str, content: str, parent_id: str) -> str:
        """Create a Google Doc in the specified Drive folder."""
        file_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.document",
            "parents": [parent_id],
        }
        gfile = self.drive_service.files().create(body=file_metadata, fields="id").execute()
        document_id = gfile.get("id")
        if content:
            requests = [{"insertText": {"location": {"index": 1}, "text": content}}]
            self.docs_service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()
        return document_id


def sync_workspace(nuclino: NuclinoClient, gdrive: GoogleDriveClient, workspace_id: str, drive_root_id: str):
    """Sync the entire Nuclino workspace into Google Drive."""
    items = nuclino.get_workspace_items(workspace_id)
    for item in items:
        name = item.get("title")
        item_id = item.get("id")
        if not name or not item_id:
            continue
        content = nuclino.get_item_content(item_id)
        gdrive.create_document(name, content, drive_root_id)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sync a Nuclino workspace to Google Drive")
    parser.add_argument("workspace_id", help="Nuclino workspace ID")
    parser.add_argument("drive_folder_id", help="Google Drive folder ID where docs will be created")
    parser.add_argument("--token", help="Nuclino API token", default=os.getenv("NUCLINO_TOKEN"))
    parser.add_argument("--credentials", help="Path to Google service account credentials", default=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

    args = parser.parse_args()
    if not args.token:
        raise SystemExit("Nuclino token is required")
    if not args.credentials:
        raise SystemExit("Google credentials path is required")

    nuclino_client = NuclinoClient(args.token)
    gdrive_client = GoogleDriveClient(args.credentials)
    sync_workspace(nuclino_client, gdrive_client, args.workspace_id, args.drive_folder_id)
