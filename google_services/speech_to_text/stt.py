from google.cloud import speech_v1 as speech
from google_services.authorization.get_oauth_creds import get_creds

def speech_to_text(config, audio):
    creds = get_creds()
    client = speech.SpeechClient(credentials=creds)
    response = client.recognize(config=config, audio=audio)
    
    final_transcript = ""
    confidence_row = []
    for result in response.results:
        best_alternative = result.alternatives[0]
        transcript = best_alternative.transcript
        confidence = best_alternative.confidence
        final_transcript += transcript
        confidence_row.append(confidence)
    
    avg_confidence = sum(confidence_row)/len(confidence_row)
    
    print(f"{'='*10}\nAVG confidence: {avg_confidence:.0f}\n{'='*10}")
    
    return final_transcript

def long_speech_to_text(gcs_uri, lang_code="ru-RU", voice_name=None):
    creds = get_creds()
    client = speech.SpeechClient(credentials=creds)

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        language_code=lang_code,
        enable_automatic_punctuation=True
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    if not voice_name:
        print("ИИ расшифровывает аудио...")
    else:
        print(f"ИИ расшифровывает аудио {voice_name}...")
    response = operation.result(timeout=720)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    final_transcript = ""
    for idx, result in enumerate(response.results, start=1):
        final_transcript += result.alternatives[0].transcript
        print(f"Part #{idx}. Confidence: {result.alternatives[0].confidence}")

    return final_transcript

if __name__ == '__main__':
    # config = dict(language_code="en-US")
    # audio = dict(uri="gs://no-war-poem-bucket/full_new_year_speech_putin.flac")
    # speech_to_text(config=config, audio=audio)

    putin_uri = "gs://no-war-poem-test-bucket/full_new_year_speech_putin.flac"
    final_transcript = long_speech_to_text(putin_uri)

    print('Hello world')