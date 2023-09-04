from __future__ import print_function

import base64
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import mimetypes
import os

from google_services.authorization.get_oauth_creds import get_creds
from config_main import settings, logger
from datetime import datetime

def gmail_send_message(
        send_to: str,
        sent_from: str,
        subject: str,
        text_content: str,
):
    """Create and send an email message
    Print the returned  message id
    Returns: Message object, including message id
    """
    
    creds = get_creds()

    try:
        service = build('gmail', 'v1', credentials=creds)
        message = EmailMessage()

        message.set_content(text_content)

        message['To'] = send_to
        message['From'] = sent_from
        message['Subject'] = subject

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        logger.info(f'Message Id: {send_message["id"]}')
    
    except HttpError as error:
        logger.info(f'An error occurred: {error}')
        send_message = None
    
    return send_message

def gmail_send_attachment_message(
    send_to: str,
    subject: str,
    text_content: str,
    attachment_path: list[str] = None
):
    """Create and send an email message with optional attachment
    Print the returned message id
    Returns: Message object, including message id
    """
    
    creds = get_creds()

    try:
        service = build('gmail', 'v1', credentials=creds)

        message = MIMEMultipart()
        message['to'] = send_to
        message['subject'] = subject

        if not attachment_path:
            for path in attachment_path:
                content_type, _ = mimetypes.guess_type(path)
                if content_type is None:
                    content_type = 'application/octet-stream'
                main_type, sub_type = content_type.split('/', 1)
                with open(path, 'rb') as attachment:
                    message_attachment = MIMEBase(main_type, sub_type)
                    message_attachment.set_payload(attachment.read())
                    encoders.encode_base64(message_attachment)
                    message_attachment.add_header('Content-Disposition', f'attachment; filename={os.path.basename(path)}')
                    message.attach(message_attachment)
        
        text_part = MIMEText(text_content, 'plain')
        message.attach(text_part)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        send_message = service.users().messages().send(
            userId="me",
            body={'raw': raw_message}
        ).execute()
        
        logger.info(f'Message Id: {send_message["id"]}')
    
    except HttpError as error:
        logger.info(f'An error occurred: {error}')
        send_message = None
    
    return send_message

if __name__ == '__main__':
    image_urls = [
    'https://drive.google.com/uc?export=view&id=1MyzkCXQY0-1ecP2qh_UtG0lBbXsFwyEQ',
    'https://drive.google.com/uc?export=view&id=1F0TtgV7eCA28Vvzr1LIfukNAhfVHERxV',
    'https://drive.google.com/uc?export=view&id=12Gs82D0m8vjw6M8x6na4qqNoljLaP97U',
    ]

    gmail_send_attachment_message(
        send_to='thelonius19@gmail.com',
        subject=f"{datetime.now().strftime('%d-%m-%Y %H:%M')}. Now we kinda got used to the oauth flow, wow!",
        text_content='Here a funny thing. You understand something for this day. Hero!',
        attachment_path=image_urls
    )