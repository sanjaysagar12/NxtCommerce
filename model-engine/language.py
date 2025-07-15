import speech_recognition as sr
import os
from typing import Optional
from gtts import gTTS
from googletrans import Translator
import uuid
import asyncio
import functools

def run_async(func):
    """Decorator to run async functions in sync context"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, func(*args, **kwargs))
                    return future.result()
            else:
                return loop.run_until_complete(func(*args, **kwargs))
        except RuntimeError:
            # No event loop, create a new one
            return asyncio.run(func(*args, **kwargs))
    return wrapper

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

def text_to_audio(text: str, language: str = "en-US", audio_dir: str = "audio") -> tuple[str, str]:
    """
    Convert text to audio using text-to-speech (TTS) and save in specified directory.
    
    Args:
        text (str): Text to convert to audio
        language (str): Language code for TTS (e.g., "en-US", "es-ES", "fr-FR")
        audio_dir (str): Directory to save audio files
    
    Returns:
        tuple[str, str]: Tuple containing (file_path, file_id)
    """
    
    # Create audio directory if it doesn't exist
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    
    # Generate a unique ID for the filename
    file_id = str(uuid.uuid4())
    output_path = os.path.join(audio_dir, f"{file_id}.mp3")
    
    # Convert language code format for gTTS (from en-US to en)
    lang_code = language.split('-')[0] if '-' in language else language
    
    # Generate and save the audio file
    tts = gTTS(text=text, lang=lang_code)
    tts.save(output_path)

    return output_path, file_id

def _sync_translate(text: str, target_language: str = "en", source_language: str = "auto") -> tuple[str, str]:
    """
    Synchronous translation function that handles both sync and async googletrans versions.
    """
    try:
        # Initialize translator
        translator = Translator()
        
        # Translate text
        result = translator.translate(text, src=source_language, dest=target_language)
        
        # Check if result is a coroutine (async)
        if hasattr(result, '__await__'):
            # It's a coroutine, we need to await it
            async def _async_translate():
                return await result
            
            # Run the async function
            loop = None
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running, create a new thread
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, _async_translate())
                        result = future.result()
                else:
                    result = loop.run_until_complete(_async_translate())
            except RuntimeError:
                # No event loop, create a new one
                result = asyncio.run(_async_translate())
        
        return result.text, result.src
        
    except Exception as e:
        print(f"An error occurred during translation: {e}")
        raise Exception(f"Translation failed: {str(e)}")

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
    return _sync_translate(text, target_language, source_language)

def _sync_detect_language(text: str) -> str:
    """
    Synchronous language detection function that handles both sync and async googletrans versions.
    """
    try:
        # Initialize translator
        translator = Translator()
        
        # Detect language
        result = translator.detect(text)
        
        # Check if result is a coroutine (async)
        if hasattr(result, '__await__'):
            # It's a coroutine, we need to await it
            async def _async_detect():
                return await result
            
            # Run the async function
            loop = None
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running, create a new thread
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, _async_detect())
                        result = future.result()
                else:
                    result = loop.run_until_complete(_async_detect())
            except RuntimeError:
                # No event loop, create a new one
                result = asyncio.run(_async_detect())
        
        return result.lang
        
    except Exception as e:
        print(f"An error occurred during language detection: {e}")
        raise Exception(f"Language detection failed: {str(e)}")

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
    return _sync_detect_language(text)

