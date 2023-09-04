import base64
from googleapiclient.discovery import build
from google_services.authorization.get_oauth_creds import get_creds
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from datetime import datetime
from poem_app.config_main import settings


def create_message(to, subject, message_text):
    message = MIMEText(message_text, 'html')
    message['to'] = to
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message
    except HttpError as error:
        print('An error occurred: %s' % error)


def send_poem_message(
        success: bool,
        poem_text: str,
        image_urls: list[str] = None,
    ):
    creds = get_creds()
    service = build('gmail', 'v1', credentials=creds)
    sender = settings.email

    # Create an email body with inline images
    status_time = datetime.now().strftime('%d-%m-%Y %H:%M')
    if success:
        subject = f"OK: {status_time}"
    else:
        subject = f"ERROR: {status_time}"
    email_body = f"""
    <html>
    <head><b>{subject}</b></head>
    <body>
    """
    
    poem_text = poem_text.split('\n')
    for line in poem_text:
        email_body+= f"<p>{line}</p>"
        if "\r" in line:
            email_body += "</br>"
    
    if image_urls:
        email_body += '<ul>'

        for idx, image_url in enumerate(image_urls, start=1):
            email_body += f'<li><a href="{image_url}">#{idx} Image </a></li>'

    if image_urls:
        email_body += '</ul>'

    email_body += """
    </body>
    </html>
    """

    message = create_message(sender, subject, email_body)
    send_message(service, 'me', message)


if __name__ == '__main__':
   caption = '[ 555 дней войны, «Стихи и нет войне» №1817 ]\r\n «НИЧТОЖЕСТВО» \r\nАфанасий Фет, 1880\r\n*** ***** *** ***** *** ***** *** *****\r\nТебя не знаю я. Болезненные крики\nНа рубеже твоем рождала грудь моя,\nИ были для меня мучительны и дики\nУсловья первые земного бытия.\nСквозь слез младенческих обманчивой улыбкой\nНадежда озарить сумела мне чело,\nИ вот всю жизнь с тех пор ошибка за ошибкой,\nЯ всё ищу добра — и нахожу лишь зло.\nИ дни сменяются утратой и заботой\n(Не всё ль равно: один иль много этих дней!),\nХочу тебя забыть над тяжкою работой,\nНо миг — и ты в глазах с бездонностью своей.\nЧто ж ты? Зачем? — Молчат и чувства и познанье.\nЧей глаз хоть заглянул на роковое дно?\nТы — это ведь я сам. Ты только отрицанье\nВсего, что чувствовать, что мне узнать дано.\nЧто ж я узнал? Пора узнать, что в мирозданьи,\nКуда ни обратись, — вопрос, а не ответ;\nА я дышу, живу и понял, что в незнаньи\nОдно прискорбное, но страшного в нем нет ВОЙНЕ.\nА между тем, когда б в смятении великом\nСрываясь, силой я хоть детской обладал,\nЯ встретил бы твой край тем самым резким криком,\nС каким я некогда твой берег покидал.\r\n*** ***** *** ***** *** ***** *** *****\r\n#украина #stopputin #odesa #russia #kyiv #russiaisaterroriststate #standupforukraine'
   image_urls = [
       'https://drive.google.com/uc?export=view&id=1mWWqiHANgMWaF_XgexAQEf6SYfPynd3Z',
       'https://drive.google.com/uc?export=view&id=1kAWiE8pKusFykTipA0demvLkehhX0zqC',
   ]
   send_poem_message(True, caption, image_urls)
   
   print('Hello world!')