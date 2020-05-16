from google.cloud import texttospeech
from google.oauth2 import service_account
from autocorrect import Speller

class Reader:
    """Class Description"""
    
    def __init__(self):
        # Initializes text to speech variables
        credentials = service_account.Credentials.from_service_account_file('../tts_auth/AudioEyes-68236ea78337.json')
        self.client = texttospeech.TextToSpeechClient(credentials=credentials)
        self.voice = texttospeech.types.VoiceSelectionParams(
            language_code='en-US',
            ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)
        self.audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)
        
        # Initializes autocorrect
        self.autocorrect = Speller(lang='en')

    def read_list(self, inputList, autocorrect=False):
        
        audioArray = []
        for phrase in inputList:
            if autocorrect:
                phrase = self.autocorrect(phrase)
            synthesis_input = texttospeech.types.SynthesisInput(text=phrase)
            response = self.client.synthesize_speech(synthesis_input, self.voice, self.audio_config)
            audioArray.append(response)
        
        return audioArray
    
    def read_item(self, inputItem, autocorrect=False):
        if autocorrect:
            inputItem = self.autocorrect(inputItem)
        synthesis_input = texttospeech.types.SynthesisInput(text=inputItem)
        return self.client.synthesize_speech(synthesis_input, self.voice, self.audio_config)