import soundfile as sf
import io
from pydub import AudioSegment
import wave
import json
from vosk import Model, KaldiRecognizer

def transcribe_audio(file_path: str) -> str:
    # Открываем WAV-файл
    wf = wave.open(file_path, "rb")
    # Проверяем, что аудио соответствует требованиям модели (моно, PCM)
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        raise ValueError("Аудиофайл должен быть в формате WAV (моно, PCM).")

    # Загружаем модель Vosk
    model = Model("voice_message_process/vosk-model-small-ru-0.22")  # Укажите путь к скачанной модели Vosk
    recognizer = KaldiRecognizer(model, wf.getframerate())

    # Инициализируем переменную для накопления результатов
    transcription = ""

    # Читаем данные по частям
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            transcription += " " + result.get("text", "")

    # Добавляем финальный результат
    final_result = json.loads(recognizer.FinalResult())
    transcription += " " + final_result.get("text", "")

    return transcription.strip()
