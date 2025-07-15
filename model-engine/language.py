import speech_recognition as sr
import os
from typing import Optional
from gtts import gTTS
from googletrans import Translator
import uuid
def audio_to_text(audio_file_path: str, language: str = "en-US") -> Optional[str]:
    """
    Convert audio file to text using speech recognition.
    
    Args:
        audio_file_path (str): Path to the audio file (supports WAV, FLAC, AIFF)
        language (str): Language code for recognition (e.g., "en-US", "es-ES", "fr-FR")
    
    Returns:
        Optional[str]: Recognized text or None if recognition fails
    
    Raises:
        FileNotFoundError: If audio file doesn't exist
        ValueError: If audio file format is not supported
    """
    # Check if file exists
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    try:
        # Load audio file
        with sr.AudioFile(audio_file_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source)
            # Record the audio
            audio_data = recognizer.record(source)
        
        # Recognize speech using Google Speech Recognition
        text = recognizer.recognize_google(audio_data, language=language)
        return text
        
    except sr.UnknownValueError:
        print(f"Could not understand audio in language: {language}")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from speech recognition service: {e}")
        return None
    except Exception as e:
        print(f"An error occurred during speech recognition: {e}")
        return None

def text_to_audio(text: str, language: str = "en-US", audio_dir: str = "audio") -> str:
    """
    Convert text to audio using text-to-speech (TTS) and save in specified directory.
    
    Args:
        text (str): Text to convert to audio
        language (str): Language code for TTS (e.g., "en-US", "es-ES", "fr-FR")
        audio_dir (str): Directory to save audio files
    
    Returns:
        str: Path to the saved audio file
    """
    
    # Create audio directory if it doesn't exist
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    
    # Generate a unique ID for the filename
    file_id = str(uuid.uuid4())
    output_path = os.path.join(audio_dir, f"{file_id}.mp3")
    
    # Generate and save the audio file
    tts = gTTS(text=text, lang=language)
    tts.save(output_path)

    return output_path, file_id

def translate_text(text: str, target_language: str = "en", source_language: str = "auto") -> tuple[str, str]:
    """
    Translate text from one language to another using Google Translate.
    
    Args:
        text (str): Text to translate
        target_language (str): Target language code (e.g., "en", "es", "fr")
        source_language (str): Source language code (e.g., "en", "es", "auto")
    
    Returns:
        tuple[str, str]: Tuple containing (translated_text, detected_source_language)
    
    Raises:
        Exception: If translation fails
    """
    try:
        # Initialize translator
        translator = Translator()
        
        # Translate text
        result = translator.translate(text, src=source_language, dest=target_language)
        
        return result.text, result.src
        
    except Exception as e:
        print(f"An error occurred during translation: {e}")
        raise Exception(f"Translation failed: {str(e)}")

def detect_language(text: str) -> str:
    """
    Detect the language of the given text.
    
    Args:
        text (str): Text to detect language for
    
    Returns:
        str: Detected language code
    
    Raises:
        Exception: If language detection fails
    """
    try:
        # Initialize translator
        translator = Translator()
        
        # Detect language
        result = translator.detect(text)
        
        return result.lang
        
    except Exception as e:
        print(f"An error occurred during language detection: {e}")
        raise Exception(f"Language detection failed: {str(e)}")

