from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import sys
import webbrowser

SCOPES = ["https://www.googleapis.com/auth/drive"]

def authenticate_drive():
    creds = None
    # Load previously saved credentials
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("~/Downloads/credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for future use
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)


import re

def extract_file_id(shared_link):
    match = re.search(r"/drive/([a-zA-Z0-9_-]+)", shared_link)
    return match.group(1) if match else None


def copy_public_file(drive_service, file_id, new_file_name="Copied Document"):
    try:
        copied_file = {
            "name": new_file_name
        }
        copied = drive_service.files().copy(
            fileId=file_id,
            body=copied_file
        ).execute()

        print(f"File copied successfully! New File ID: {copied['id']}")
        return copied["id"]

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def copy_and_move_file(drive_service, file_id, new_file_name, folder_id):
    try:
        # Step 1: Copy the file
        copied_file_metadata = {"name": new_file_name}
        copied_file = drive_service.files().copy(
            fileId=file_id,
            body=copied_file_metadata
        ).execute()

        copied_file_id = copied_file["id"]
        print(f"File copied successfully! New File ID: {copied_file_id}")

        # Step 2: Move the copied file to the target folder
        # Get the existing parents of the file
        file_details = drive_service.files().get(
            fileId=copied_file_id,
            fields="parents"
        ).execute()

        previous_parents = ",".join(file_details.get("parents", []))

        # Move the file to the new folder
        drive_service.files().update(
            fileId=copied_file_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields="id, parents"
        ).execute()

        print(f"File moved to folder ID: {folder_id}")

        return copied_file_id

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def print_help():
    print("Usage: python baixar.py <target_folder_id> <public_file_link> <new_file_name>")
    print("Arguments:")
    print("  <public_file_link>   The public link of the Google Drive file to be copied.")
    print("  <new_file_name>      The name for the copied file.")
    print("  <target_folder_id>   The ID of the Google Drive folder where the file will be moved.")
    print("\nExample:")
    print("  python baixar.py https://drive.google.com/file/d/12345/view CopiedFileName 1a2b3c4d5e6f7g8h9i0j")

def run():
    # Use environment variable for folder ID if available
    target_folder_id = os.environ.get('GDRIVE_FOLDER_ID')

    # Validate inputs
    if len(sys.argv) < 3 or (len(sys.argv) < 4 and not target_folder_id):
        print_help()
        sys.exit(1)
    
    public_link = sys.argv[1]
    file_name = sys.argv[2]
    target_folder_id = sys.argv[3]

    drive_service = authenticate_drive()
    
    file_id = extract_file_id(public_link)

    if file_id:
        newfile_id = copy_and_move_file(drive_service, file_id, file_name, target_folder_id)
        webbrowser.open(f"https://colab.research.google.com/drive/{newfile_id}")
    else:
        print("Invalid Google Drive link!")


if __name__ == "__main__":
    run()