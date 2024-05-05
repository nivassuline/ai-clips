from clipsai import Transcriber
from core.utils.common import check_negative

class STT:
    def __init__(self):
        self.duration = 0 # save the duration for keep the timing during the merge

    def get_transcript(self, video_path: str) -> list[tuple[str, float, float]]:

        transcriber = Transcriber(model_size='large-v3')
        transcription = transcriber.transcribe(audio_file_path=video_path, batch_size=4)

        result_string = ""
        words = []

        for sentence in transcription.sentences:
            result_string += f"{sentence.text}: {sentence.start_time} - {sentence.end_time}\n"

        for word in transcription.words:
            if check_negative(word.end_time - word.start_time):
                start = word.end_time
                end = word.start_time
            else:
                start = word.start_time
                end = word.end_time
            words.append({'word' : word.text.strip(), 'start': start, 'end': end})

        return result_string, transcription, words, transcription.language

    
    @staticmethod
    def calc_chunks_size(duration):
        return max(1, int((duration / 60) / 15))

    def __call_whisper__(self, audio_path: str):
        transcriber = Transcriber()
        transcription = transcriber.transcribe(audio_file_path=audio_path, batch_size=4)
        result = []

        for word in transcription.words:
            result.append({'word' : word.text.strip(), 'start': word.start_time, 'end': word.end_time})

        return result
        
    def __clean_global__(self):
        self.duration = 0

