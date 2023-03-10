"""
Copyright 2019 Google LLC
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# modified by nick42

from __future__ import print_function

import base64
import os.path
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]


def send_mail(receiver_email: str, message_content: str, subject: str = "", creds=None) -> None:

    if creds is None:
        creds = Credentials.from_authorized_user_file(f"{os.environ.get('HOME')}/.config/token.json", SCOPES)

    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)

    # try to send a mail
    message = EmailMessage()

    message.set_content(message_content)

    message["To"] = receiver_email
    message["From"] = os.environ.get("TEST_MAIL")
    message["Subject"] = subject

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"raw": encoded_message}
    # pylint: disable=E1101
    send_message = service.users().messages().send(userId="me", body=create_message).execute()
    print(f'Message Id: {send_message["id"]}')


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(f"{os.environ.get('HOME')}/.config/token.json"):
        creds = Credentials.from_authorized_user_file(f"{os.environ.get('HOME')}/.config/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                f"{os.environ.get('HOME')}/.config/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=4242)
        # Save the credentials for the next run
        with open(f"{os.environ.get('HOME')}/.config/token.json", "w") as token:
            token.write(creds.to_json())

    try:
        send_mail(receiver_email=os.environ.get("TEST_MAIL"), message="test", creds=creds)
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
