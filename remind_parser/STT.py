import json
import subprocess

from vosk import Model, KaldiRecognizer


# thanks for this code to https://habr.com/ru/articles/694632/
class STT:
    """
    Класс для распознавания аудио через Vosk и преобразования его в текст.
    Поддерживаются форматы аудио: wav, ogg
    """
    default_init = {
        "model_path": "models/vosk",  # путь к папке с файлами STT модели Vosk
        "sample_rate": 16000,
        "ffmpeg_path": "models/ffmpeg/ffmpeg.exe"  # путь к ffmpeg
    }

    def __init__(self,
                 model_path=None,
                 sample_rate=None,
                 ffmpeg_path=None
                 ) -> None:
        """
        Настройка модели Vosk для распознавания аудио и
        преобразования его в текст.

        :arg model_path:  str  путь до модели Vosk
        :arg sample_rate: int  частота выборки, обычно 16000
        :arg ffmpeg_path: str  путь к ffmpeg
        """
        self.model_path = model_path if model_path else STT.default_init["model_path"]
        self.sample_rate = sample_rate if sample_rate else STT.default_init["sample_rate"]
        self.ffmpeg_path = ffmpeg_path if ffmpeg_path else STT.default_init["ffmpeg_path"]

        # self._check_model()

        model = Model(self.model_path)

        self.recognizer = KaldiRecognizer(model, self.sample_rate)
        self.recognizer.SetWords(True)

    def audio_to_text(self, audio_file_name=None) -> str:
        """
        Offline-распознавание аудио в текст через Vosk
        :param audio_file_name: str путь и имя аудио файла
        :return: str распознанный текст
        """
        # Конвертация аудио в wav и результат в process.stdout
        process = subprocess.Popen(
            [self.ffmpeg_path,
             "-loglevel", "quiet",
             "-i", audio_file_name,  # имя входного файла
             "-ar", str(self.sample_rate),  # частота выборки
             "-ac", "1",  # кол-во каналов
             "-f", "s16le",  # кодек для перекодирования, у нас wav
             "-"  # имя выходного файла нет, тк читаем из stdout
             ],
            stdout=subprocess.PIPE
        )

        # Чтение данных кусками и распознование через модель
        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if self.recognizer.AcceptWaveform(data):
                pass

        # Возвращаем распознанный текст в виде str
        result_json = self.recognizer.FinalResult()  # это json в виде str
        result_dict = json.loads(result_json)  # это dict
        return result_dict["text"]  # текст в виде str