from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pydantic import BaseModel, Field
from typing import Optional, Union
import os
import sys
from werkzeug.utils import secure_filename
import tempfile

# Add the modelengine directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'model-engine'))
from language import audio_to_text, text_to_audio, translate_text, detect_language

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'flac', 'aiff', 'mp3'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Pydantic models for request/response
class BaseResponse(BaseModel):
    success: bool
    message: str

class TextToAudioRequest(BaseModel):
    text: str = Field(..., description="Text to convert to audio")
    language: str = Field(default="en", description="Language code (e.g., 'en', 'es', 'fr')")

class TextToAudioResponse(BaseResponse):
    audio_file_id: Optional[str] = None
    audio_file_path: Optional[str] = None

class AudioToTextResponse(BaseResponse):
    text: Optional[str] = None
    language: Optional[str] = None

class TranslateRequest(BaseModel):
    text: str = Field(..., description="Text to translate")
    target_language: str = Field(..., description="Target language code (e.g., 'en', 'es', 'fr')")
    source_language: str = Field(default="auto", description="Source language code (e.g., 'en', 'es', 'auto')")

class TranslateResponse(BaseResponse):
    translated_text: Optional[str] = None
    source_language: Optional[str] = None
    target_language: Optional[str] = None

class ErrorResponse(BaseResponse):
    error: str

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify(BaseResponse(success=True, message="API is healthy").dict())

@app.route('/text-to-audio', methods=['POST'])
def convert_text_to_audio():
    """Convert text to audio file"""
    try:
        data = request.get_json()
        
        # Validate request data
        if not data or 'text' not in data:
            return jsonify(ErrorResponse(
                success=False,
                message="Invalid request",
                error="Missing 'text' field in request body"
            ).dict()), 400
        
        text = data['text']
        language = data.get('language', 'en')
        
        if not text.strip():
            return jsonify(ErrorResponse(
                success=False,
                message="Invalid request",
                error="Text cannot be empty"
            ).dict()), 400
        
        # Convert text to audio
        audio_path, file_id = text_to_audio(
            text=text,
            language=language,
            audio_dir=os.path.join(app.config['UPLOAD_FOLDER'], 'audio_output')
        )
        
        response = TextToAudioResponse(
            success=True,
            message="Text successfully converted to audio",
            audio_file_id=file_id,
            audio_file_path=audio_path
        )
        
        return jsonify(response.dict()), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            success=False,
            message="Internal server error",
            error=str(e)
        ).dict()), 500

@app.route('/translate', methods=['POST'])
def translate():
    """Translate text from one language to another"""
    try:
        data = request.get_json()
        
        # Validate request data
        if not data or 'text' not in data or 'target_language' not in data:
            return jsonify(ErrorResponse(
                success=False,
                message="Invalid request",
                error="Missing required fields: 'text' and 'target_language'"
            ).dict()), 400
        
        text = data['text']
        target_language = data['target_language']
        source_language = data.get('source_language', 'auto')
        
        if not text.strip():
            return jsonify(ErrorResponse(
                success=False,
                message="Invalid request",
                error="Text cannot be empty"
            ).dict()), 400
        
        # Translate text
        translated_text, detected_source_language = translate_text(
            text=text,
            target_language=target_language,
            source_language=source_language
        )
        
        response = TranslateResponse(
            success=True,
            message="Text successfully translated",
            translated_text=translated_text,
            source_language=detected_source_language,
            target_language=target_language
        )
        
        return jsonify(response.dict()), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            success=False,
            message="Internal server error",
            error=str(e)
        ).dict()), 500

@app.route('/detect-language', methods=['POST'])
def detect_language_endpoint():
    """Detect the language of the given text"""
    try:
        data = request.get_json()
        
        # Validate request data
        if not data or 'text' not in data:
            return jsonify(ErrorResponse(
                success=False,
                message="Invalid request",
                error="Missing 'text' field in request body"
            ).dict()), 400
        
        text = data['text']
        
        if not text.strip():
            return jsonify(ErrorResponse(
                success=False,
                message="Invalid request",
                error="Text cannot be empty"
            ).dict()), 400
        
        # Detect language
        detected_language = detect_language(text)
        
        response = BaseResponse(
            success=True,
            message=f"Language detected: {detected_language}"
        )
        
        # Add detected language to response
        response_dict = response.dict()
        response_dict['detected_language'] = detected_language
        
        return jsonify(response_dict), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            success=False,
            message="Internal server error",
            error=str(e)
        ).dict()), 500

@app.route('/audio-to-text', methods=['POST'])
def convert_audio_to_text():
    """Convert audio file to text"""
    try:
        # Check if file is present in request
        if 'audio' not in request.files:
            return jsonify(ErrorResponse(
                success=False,
                message="Invalid request",
                error="No audio file provided"
            ).dict()), 400
        
        file = request.files['audio']
        language = request.form.get('language', 'en-US')
        
        if file.filename == '':
            return jsonify(ErrorResponse(
                success=False,
                message="Invalid request",
                error="No file selected"
            ).dict()), 400
        
        if not allowed_file(file.filename):
            return jsonify(ErrorResponse(
                success=False,
                message="Invalid file type",
                error=f"Supported formats: {', '.join(ALLOWED_EXTENSIONS)}"
            ).dict()), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        try:
            # Convert audio to text
            text = audio_to_text(temp_path, language)
            
            if text is None:
                return jsonify(ErrorResponse(
                    success=False,
                    message="Speech recognition failed",
                    error="Could not recognize speech in the audio file"
                ).dict()), 400
            
            response = AudioToTextResponse(
                success=True,
                message="Audio successfully converted to text",
                text=text,
                language=language
            )
            
            return jsonify(response.dict()), 200
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        return jsonify(ErrorResponse(
            success=False,
            message="Internal server error",
            error=str(e)
        ).dict()), 500

@app.route('/download-audio/<file_id>', methods=['GET'])
def download_audio(file_id):
    """Download audio file by ID"""
    try:
        audio_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'audio_output')
        file_path = os.path.join(audio_dir, f"{file_id}.mp3")
        
        if not os.path.exists(file_path):
            return jsonify(ErrorResponse(
                success=False,
                message="File not found",
                error="Audio file does not exist"
            ).dict()), 404
        
        return send_file(file_path, as_attachment=True, download_name=f"{file_id}.mp3")
        
    except Exception as e:
        return jsonify(ErrorResponse(
            success=False,
            message="Internal server error",
            error=str(e)
        ).dict()), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify(ErrorResponse(
        success=False,
        message="File too large",
        error="File size exceeds the maximum limit of 16MB"
    ).dict()), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify(ErrorResponse(
        success=False,
        message="Endpoint not found",
        error="The requested endpoint does not exist"
    ).dict()), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify(ErrorResponse(
        success=False,
        message="Internal server error",
        error="An unexpected error occurred"
    ).dict()), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)