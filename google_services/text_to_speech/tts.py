from google.cloud import texttospeech
from google_services.authorization.get_oauth_creds import get_creds
from config import AUDIO_MP3_FILE_PATH, logging
from db.queries import poem_by_id, get_ig_published
from poem_image.helpers import process_poem_to_no_war
from random import choice
from pydub import AudioSegment
from audio_handler.audio_sampler import get_audio, msec_to_minutes_by_total
import os

VOICES = [
    "ru-RU-Wavenet-A",
    "ru-RU-Wavenet-B",
    "ru-RU-Wavenet-C",
    "ru-RU-Wavenet-D",
    "ru-RU-Wavenet-E",
    "ru-RU-Standard-A",
    "ru-RU-Standard-B",
    "ru-RU-Standard-C",
    "ru-RU-Standard-D",
    "ru-RU-Standard-E"
]

def get_voice_gender(voice: str):
    '''https://cloud.google.com/text-to-speech/docs/voices'''

    voice_map = {"A": "FEMALE", "B": "MALE", "C": "FEMALE", "D": "MALE", "E": "FEMALE"}

    return voice_map[voice.split('-')[-1]]

def tts(
    text: str,
    voice_name: str, 
    filename: str,
    output_folder: str
    ) -> str:
    
    creds = get_creds()
    
    client = texttospeech.TextToSpeechClient(credentials=creds)
    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="ru-RU", name=voice_name
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
        )

    # The response's audio_content is binary.
    output_path = f"{output_folder}/{filename}.mp3".replace('//','/')
    with open(output_path, "wb") as file:
        file.write(response.audio_content)
    
    return output_path

def no_war_paragraphs():
    published_ids = get_ig_published()

    for poem_id in published_ids:
        poem = poem_by_id(poem_id)
        poem_text = poem["poem_full"]
        author = poem["author"]
        title = poem["title"]
        poem_prepared = process_poem_to_no_war(poem_text).split('\r\n\r\n')
        needed_paragraphs = [par for par in poem_prepared if "нет ВОЙНЕ" in par]

        for p_idx, paragraph in enumerate(needed_paragraphs, start=1):
            tts(
                text=paragraph,
                voice_name=choice(VOICES),
                filename=f"{poem_id}_{author}_{title}_p{p_idx}"
                )
    
    return None

def split_big_text(text_to_split: str, split_char: str=". ", bound_char: int=1000) -> list[str]:
    by_elements = text_to_split.split(split_char)

    cur_part, cur_part_len = [], 0
    splitted_text = [cur_part]

    for element in by_elements:
        element = f"{element}{split_char}"
        if cur_part_len + len(element) < bound_char:
            splitted_text[-1].append(element)
            cur_part_len += len(element)
        else:
            splitted_text.append([element])
            cur_part_len = len(element)
    
    final_parts = [('').join(part).strip() for part in splitted_text]
    
    return final_parts

def big_text_tts(
    big_text: str,
    voice_name: str, 
    filename: str,
    output_folder: str,
    bound_char: int = 2000
    ) -> str:
    splitted_text = split_big_text(big_text, split_char=". ", bound_char=bound_char)
    
    final_audio = AudioSegment.empty()
    for part_idx, part in enumerate(splitted_text, start=1):
        part_filename = f"{filename}_part{part_idx}"
        part_audio_path = tts(part, voice_name, part_filename, output_folder)
        part_audio = get_audio(part_audio_path, explicit_mono=True)
        os.remove(part_audio_path)
        final_audio += part_audio
    
    final_path = f"{output_folder}/{filename}.flac".replace('//', '/')
    final_audio.export(final_path, format="flac")

    return final_path


if __name__ == '__main__':
    output_folder = f"speech_to_text_glitch/output/"
    filename = "final_merge_audio"

    long_string = '''
    Уважаемые граждане России дорогие друзья заканчивается 2021 год совсем скоро время перенесёт нас из прошлого в будущее. Да так происходит каждый день минуту и секунду, но этот непрерывный ход времени. Мы отчётливо слышим, Когда встречаем Новый год, ждём его, как жизненный рубеж. Всех нас объединяет сейчас надежда на предстоящие добрые перемены, но мы понимаем, что их невозможно оторвать отделить от событий уходящего года. Мы столкнулись с колоссальными вызовами, но научились жить в таких жёстких условиях решать сложные задачи и смогли это сделать благодаря нашей Солидарности вместе продолжали бороться с опасной эпидемии, которая охватила все континенты и пока не отступают. Коварная болезнь унесла десятки тысяч жизней хочу выразить слова искренней поддержки всем кто потерял родных близких людей. Дорогие друзья, самое главное, что все трудности уходящего года мы преодолевали вместе защитили тех, кто оказался в сложной ситуации. В первую очередь поддержали людей старших поколений и семьи, Где растут дети будущее России Мы твёрдо и последовательно отстаивали наши национальные интересы безопасность страны и граждан в Короткие сроки восстановили экономику. И по многим позициям выходим сейчас на реализацию стратегических задач развития, конечно, нерешённых проблем ещё очень много, но этот год мы прошли, да? Главная заслуга здесь принадлежит именно вам гражданам России это результат вашего дорогие друзья напряжённого труда. Каждый на своём месте и стремился исполнить свой долг сделать не только то, что в его силах, но немного больше помочь, тем, кому особенно трудно. Спасибо всем вам. Такое непростое время, так сейчас очень важен Настрой на соседями стремление обязательно реализовать свои личные планы и принести пользу обществу и родной стране. И встречаю Новый год Мы надеемся, что он откроет новые возможности, рассчитываем, конечно, неудачу, но всё же понимаем, что достижения задуманного прежде всего зависит от нас самих от того, что ставим в приоритет, чем наполняем повседневную жизнь. Я столько крепко активный берёмся за дело и добиться конкретных видимых результатов из них будет складываться реализации наших общенациональных планов их главная цель, повышение благосостояния и качества жизни людей. Решение именно этих задач сделает Россию ещё более сильным и Только вместе. Мы сможем обеспечить дальнейшее развитие И процветание нашей родины. Дорогие друзья Новогодняя ночь буквально наполнено добрыми чувствами и светлыми помыслами желанием каждого проявить свои лучшие качества. И такой открытости щедрости суть и энергетика этого чудесного праздника, Когда становится так важно согреть родители вниманием и заботой обнять, если они рядом сказать всем близким, как они дорого. Какое это счастье, когда есть любовь дети, семья, друзья, всё это великие ценности, которые во многом определяют смысл жизни каждого человека. Мы все хотим, чтобы в наступающем году они оставались для нас такой же надёжные опоры и сейчас спешим признаться дорогим для нас людям сокровенных чувств. Произнести искренние слова любви и благодарности, на которые порой не хватает времени в будничные суете. Но настоящее новогоднее волшебство в том и состоит, что открывает наши сердца чуткости и доверию благородство и милосердие. И где бы вы ни были вытянуты в кругу семьи друзей на площадях любимых городов, везде звучат самые тёплые пожелания. С удовольствием к ним присоединяюсь и хочу отдельно поздравить с Новым годом всех кто исполняет сейчас свой профессиональный и воинский долг спасает выхаживает больных находится на боевом посту обеспечивает правопорядок не прерывается работа на транспортных магистралях. Наведи производств и служб жизнеобеспечения. В этих сферах работают сотни тысяч наших граждан. Спасибо вам за ответственный важный для страны и общества труд. Дорогие друзья Через несколько секунд наступит Новый год и во многих семьях, в том числе и в наших соотечественников за пределами России прозвучит традиционное с Новым годом с новым счастьем эти простые слова мы произносим особым чувством, потому что они передаются из поколения в поколение. Искренне поздравляю вас. Главное пожелание всем, конечно же, крепкого здоровья, а к нему уверен, приложится успехи в работе в учёбе в творчестве или гемодиализ? Пусть в каждом доме будет как можно больше разных событий. Пусть чаще появляются новые семьи рождаются дети. Пусть они вырастут здоровыми умными и свободными. Пусть любовь будет В каждом сердце и вдохновляет всех нас на достижение поставленных целей и покорения самых больших высот. Ради своих любимых и ради нашей единственной Великой родины. С Новым годом дорогие друзья С новым 2022 года
    '''

    tt = big_text_tts(long_string, VOICES[0], filename, output_folder)

    # print(len(long_string))



    # a = split_big_text(long_string)

    # total = 0
    # for el in a:
    #     print(len(el))
    #     total+=len(el)
    #     print(f"Total: {total}")

    print('Hello world!')
