from openai import OpenAI
from config import Config

class AudioTranscriber:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def transcribe_audio(self, audio_file_path):
        """
        Transcrit un fichier audio en utilisant l'API OpenAI Whisper
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            return transcript
            
        except Exception as e:
            raise Exception(f"Erreur lors de la transcription: {str(e)}")
    
    def transcribe_with_language_detection(self, audio_file_path):
        """
        Transcrit un fichier audio avec détection automatique de la langue
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json"
                )
            
            return {
                'text': transcript.text,
                'language': getattr(transcript, 'language', 'auto-detected')
            }
            
        except Exception as e:
            raise Exception(f"Erreur lors de la transcription avec détection de langue: {str(e)}") 