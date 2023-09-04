from __future__ import print_function

import base64
import mimetypes
import os
from os.path import isfile, join

from email.message import EmailMessage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google_services.authorization.get_oauth_creds import get_creds

from config import GOOGLE_API_KEY

def gmail_send_with_attachment(
    email_text: str,
    attachments: list[str],
    email_to: list[str],
    email_from: str,
    email_subject: str,
    creds=None,
    api_key=None
    ):
    """
    Send an email with attachment.
    Print the returned draft's message and id.
    Returns: Draft object, including draft id and message meta data.
    """
    
    # create gmail api client
    if creds:
        service = build('gmail', 'v1', credentials=creds)
    elif not creds and api_key:
        service = build('gmail', 'v1', developerKey=api_key)
    else:
        raise Exception("You must provide some credentials: oatuh2 token or api_key")

    mime_message = MIMEMultipart()

    # headers
    mime_message['To'] = (lambda x: x if type(x)==str else ', '.join(x))(email_to)
    mime_message['From'] = email_from
    mime_message['Subject'] = email_subject

    # text
    mime_message.attach(MIMEText(email_text, 'plain'))
    

    for attachment in attachments:
        content_type, encoding = mimetypes.guess_type(attachment)
        main_type, sub_type = content_type.split('/', 1)
        file_name = os.path.basename(attachment)
    
        with open(attachment, 'rb') as f:
    
            myFile = MIMEBase(main_type, sub_type)
            myFile.set_payload(f.read())
            myFile.add_header('Content-Disposition', 'attachment', filename=file_name)
            encoders.encode_base64(myFile)
        
        mime_message.attach(myFile)

    encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
    
    # pylint: disable=E1101

    try:
        send_message = service.users().messages().\
            send(userId="me", body={'raw': encoded_message}).execute()
        print(f'Message Id: {send_message["id"]}')
        
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None

    return send_message



if __name__ == '__main__':
    creds = get_creds()
    email_text = '''
    Ежегодную пресс-конференцию Владимира Путина, вероятно, отменили из опасений «несанкционированного обсуждения» войны в Украине.
    Об этом говорится в сводке военной разведки министерства обороны Великобритании.
    12 декабря пресс-секретарь президента РФ Дмитрий Песков объявил, что в 2022 году итоговая пресс-конференция Путина с журналистами не состоится.
    Подобное произошло впервые за десять лет. Причин отмены мероприятия представитель Кремля не привел.
    Как отмечает Минобороны Великобритании, итоговая пресс-конференция всегда была важной частью календаря общественных мероприятий президента РФ и ее использовали «как возможность продемонстрировать предполагаемую честность Путина».
    '''
    email_to = ['thelonius19@gmail.com', 'kertanov19071989@yahoo.com']
    email_from = 'thelonius19@gmail.com'
    email_subject = 'Тестирование автоматического имэйла, отправленного Питоном.'

    attachments_dir = 'google_services/google_mail/test_attachments'
    attachments = [f"{attachments_dir}/{f}" for f in os.listdir(attachments_dir) if isfile(join(attachments_dir, f))]

    gmail_send_with_attachment(email_text, attachments, email_to, email_from, email_subject, creds=creds, api_key=GOOGLE_API_KEY)
    

    print('Helo world!')