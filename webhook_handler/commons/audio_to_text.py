from google.cloud import speech


def transcribe(content):
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        enable_automatic_punctuation=True,
        audio_channel_count=2,
        language_code="th",
        sample_rate_hertz=16000,
    )

    response = client.recognize(request={"config": config, "audio": audio})
    total_speech_to_text = []
    for result in response.results:
        print(result.alternatives[0].transcript)
        total_speech_to_text.append(result.alternatives[0].transcript)

    return " ".join(total_speech_to_text)
