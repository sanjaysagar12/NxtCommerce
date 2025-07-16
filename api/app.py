from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin
from pydantic import BaseModel, Field
from typing import Optional, Union
import os
import sys
from werkzeug.utils import secure_filename
import tempfile

# Add the modelengine directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'model-engine'))
from language import audio_to_text, text_to_audio, translate_text, detect_language

# Import ecommerce API functions
from ecommerce import add_product_api, search_products_api, catalog_ai_api

app = Flask(__name__)

# Enable CORS for all routes with proper configuration
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://localhost:4000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

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
    return jsonify(BaseResponse(success=True, message="API is healthy").model_dump())

@app.before_request
def handle_preflight():
    """Handle preflight requests"""
    if request.method == "OPTIONS":
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

@app.route('/text-to-audio', methods=['POST', 'OPTIONS'])
@cross_origin()
def convert_text_to_audio():
    """Convert text to audio file"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        
    try:
        data = request.get_json()
        
        # Validate request data
        if not data or 'text' not in data:
            return jsonify(ErrorResponse(
                success=False,
                message="Invalid request",
                error="Missing 'text' field in request body"
            ).model_dump()), 400
        
        text = data['text']
        language = data.get('language', 'en')
        
        if not text.strip():
            return jsonify(ErrorResponse(
                success=False,
                message="Invalid request",
                error="Text cannot be empty"
            ).model_dump()), 400
        
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
        
        return jsonify(response.model_dump()), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            success=False,
            message="Internal server error",
            error=str(e)
        ).model_dump()), 500

@app.route('/translate', methods=['POST', 'OPTIONS'])
@cross_origin()
def translate():
    """Translate text from one language to another"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        
    try:
        data = request.get_json()
        
        # Validate request data
        if not data or 'text' not in data or 'target_language' not in data:
            return jsonify(ErrorResponse(
                success=False,
                message="Invalid request",
                error="Missing required fields: 'text' and 'target_language'"
            ).model_dump()), 400
        
        text = data['text']
        target_language = data['target_language']
        source_language = data.get('source_language', 'auto')
        
        if not text.strip():
            return jsonify(ErrorResponse(
                success=False,
                message="Invalid request",
                error="Text cannot be empty"
            ).model_dump()), 400
        
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
        
        return jsonify(response.model_dump()), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            success=False,
            message="Internal server error",
            error=str(e)
        ).model_dump()), 500

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
            ).model_dump()), 400
        
        text = data['text']
        
        if not text.strip():
            return jsonify(ErrorResponse(
                success=False,
                message="Invalid request",
                error="Text cannot be empty"
            ).model_dump()), 400
        
        # Detect language
        detected_language = detect_language(text)
        
        response = BaseResponse(
            success=True,
            message=f"Language detected: {detected_language}"
        )
        
        # Add detected language to response
        response_dict = response.model_dump()
        response_dict['detected_language'] = detected_language
        
        return jsonify(response_dict), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            success=False,
            message="Internal server error",
            error=str(e)
        ).model_dump()), 500

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
            ).model_dump()), 400
        
        file = request.files['audio']
        language = request.form.get('language', 'en-US')
        
        if file.filename == '':
            return jsonify(ErrorResponse(
                success=False,
                message="Invalid request",
                error="No file selected"
            ).model_dump()), 400
        
        if not allowed_file(file.filename):
            return jsonify(ErrorResponse(
                success=False,
                message="Invalid file type",
                error=f"Supported formats: {', '.join(ALLOWED_EXTENSIONS)}"
            ).model_dump()), 400
        
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
                ).model_dump()), 400
            
            response = AudioToTextResponse(
                success=True,
                message="Audio successfully converted to text",
                text=text,
                language=language
            )
            
            return jsonify(response.model_dump()), 200
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        return jsonify(ErrorResponse(
            success=False,
            message="Internal server error",
            error=str(e)
        ).model_dump()), 500

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
            ).model_dump()), 404
        
        return send_file(file_path, as_attachment=True, download_name=f"{file_id}.mp3")
        
    except Exception as e:
        return jsonify(ErrorResponse(
            success=False,
            message="Internal server error",
            error=str(e)
        ).model_dump()), 500

@app.route('/add-product', methods=['POST'])
def add_product_endpoint():
    """Add a product using natural language input"""
    try:
        data = request.get_json()
        if not data or 'user_input' not in data:
            return jsonify({
                "success": False,
                "message": "Missing 'user_input' in request body."
            }), 400
        user_input = data['user_input']
        result = add_product_api(user_input)
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal server error.",
            "error": str(e)
        }), 500

@app.route('/search-products', methods=['POST'])
def search_products_endpoint():
    """Search products using natural language input"""
    try:
        data = request.get_json()
        if not data or 'user_input' not in data:
            return jsonify({
                "success": False,
                "message": "Missing 'user_input' in request body."
            }), 400
        user_input = data['user_input']
        result = search_products_api(user_input)
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal server error.",
            "error": str(e)
        }), 500

@app.route('/catalog/process-text', methods=['POST', 'OPTIONS'])
@cross_origin()
def process_catalog_text():
    """Process text input for catalog operations"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        
    try:
        data = request.get_json()
        
        # Validate request data
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "message": "Missing 'text' field in request body"
            }), 400
        
        text_input = data['text']
        action = data.get('action', 'summary')  # Default action is summary
        page = data.get('page', 1)
        limit = data.get('limit', 10)
        sort_by = data.get('sortBy', 'createdAt')
        sort_order = data.get('sortOrder', 'desc')
        
        if not text_input.strip():
            return jsonify({
                "success": False,
                "message": "Text input cannot be empty"
            }), 400
        
        # Process text based on action
        if action == 'summary' or action == 'ai-summary':
            # Use AI to generate catalog summary with text context
            from ecommerce import get_ai_catalog_summary_with_context
            result = get_ai_catalog_summary_with_context(
                text_input, page, limit, sort_by, sort_order
            )
            
            if result:
                # Extract only the text summary part and enhance with inventory details
                text_summary = ""
                if isinstance(result, dict):
                    # Get AI summary first
                    ai_summary = result.get('ai_summary', result.get('text_summary', ''))
                    
                    # Add inventory analysis
                    products_data = result.get('products_data', {})
                    if products_data and 'products' in products_data:
                        products = products_data['products']
                        
                        # Calculate inventory statistics
                        total_products = len(products)
                        total_stock = sum(int(p.get('stock', 0)) for p in products)
                        low_stock_products = [p for p in products if int(p.get('stock', 0)) < 10]
                        high_stock_products = [p for p in products if int(p.get('stock', 0)) > 50]
                        out_of_stock = [p for p in products if int(p.get('stock', 0)) == 0]
                        
                        # Calculate total inventory value
                        total_value = sum(int(p.get('price', 0)) * int(p.get('stock', 0)) for p in products)
                        
                        # Create inventory summary
                        inventory_summary = f"\n\n📊 INVENTORY ANALYSIS:\n"
                        inventory_summary += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        inventory_summary += f"📦 Total Products: {total_products}\n"
                        inventory_summary += f"📈 Total Stock Units: {total_stock}\n"
                        inventory_summary += f"💰 Total Inventory Value: ₹{total_value:,}\n"
                        inventory_summary += f"📊 Average Stock per Product: {total_stock//total_products if total_products > 0 else 0}\n\n"
                        
                        # Stock level breakdown
                        inventory_summary += f"📋 STOCK LEVEL BREAKDOWN:\n"
                        inventory_summary += f"🔴 Out of Stock: {len(out_of_stock)} products\n"
                        inventory_summary += f"🟡 Low Stock (<10): {len(low_stock_products)} products\n"
                        inventory_summary += f"🟢 High Stock (>50): {len(high_stock_products)} products\n"
                        inventory_summary += f"🔵 Normal Stock (10-50): {total_products - len(out_of_stock) - len(low_stock_products) - len(high_stock_products)} products\n\n"
                        
                        # Detailed product stock list
                        inventory_summary += f"📝 DETAILED STOCK STATUS:\n"
                        for i, product in enumerate(products, 1):
                            stock = int(product.get('stock', 0))
                            price = int(product.get('price', 0))
                            name = product.get('name', 'N/A')
                            
                            # Stock status indicator
                            if stock == 0:
                                status = "🔴 OUT OF STOCK"
                            elif stock < 10:
                                status = "🟡 LOW STOCK"
                            elif stock > 50:
                                status = "🟢 HIGH STOCK"
                            else:
                                status = "🔵 NORMAL"
                            
                            inventory_summary += f"{i}. {name}\n"
                            inventory_summary += f"   Stock: {stock} units | Price: ₹{price} | Value: ₹{stock * price:,} | {status}\n"
                        
                        # If user mentions selling offline, provide adjustment guidance
                        if 'sold' in text_input.lower() or 'offline' in text_input.lower() or 'sell' in text_input.lower():
                            inventory_summary += f"\n\n💡 OFFLINE SALES ADJUSTMENT GUIDE:\n"
                            inventory_summary += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            inventory_summary += f"If you've sold products offline, here's your current stock:\n"
                            inventory_summary += f"• Update stock levels by deducting offline sales\n"
                            inventory_summary += f"• Current total: {total_stock} units across all products\n"
                            inventory_summary += f"• Monitor low stock items for reordering\n"
                            inventory_summary += f"• Consider updating inventory management system\n"
                        
                        text_summary = ai_summary + inventory_summary
                    else:
                        text_summary = ai_summary or str(result)
                else:
                    text_summary = str(result)
                
                return jsonify({
                    "success": True,
                    "message": "AI catalog summary with inventory analysis generated successfully",
                    "text_summary": text_summary,
                    "processed_text": text_input
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "message": "Failed to generate AI catalog summary with text context"
                }), 400
        
        elif action == 'search':
            # Use text as search query  
            from ecommerce import search_products_api
            result = search_products_api(text_input)
            
            if result and result.get('success'):
                # Generate text summary of search results
                products = result.get('results', [])
                if products:
                    search_summary = f"Found {len(products)} products matching '{text_input}':\n\n"
                    for i, product in enumerate(products[:5], 1):  # Show first 5 results
                        search_summary += f"{i}. {product.get('name', 'N/A')}\n"
                        search_summary += f"   Price: ₹{product.get('price', 'N/A')}\n"
                        search_summary += f"   Stock: {product.get('stock', 'N/A')}\n"
                        search_summary += f"   Description: {product.get('description', 'N/A')[:100]}...\n\n"
                    
                    if len(products) > 5:
                        search_summary += f"... and {len(products) - 5} more products."
                else:
                    search_summary = f"No products found matching '{text_input}'"
                
                return jsonify({
                    "success": True,
                    "message": f"Search completed for: '{text_input}'",
                    "text_summary": search_summary,
                    "processed_text": text_input
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "message": f"Search failed for: '{text_input}'",
                    "text_summary": f"No products found matching '{text_input}'",
                    "processed_text": text_input
                }), 400
        
        elif action == 'add-product':
            # Use text to add a product
            from ecommerce import add_product_api
            result = add_product_api(text_input)
            
            if result and result.get('success'):
                # Generate text summary of product addition
                product_data = result.get('data', {})
                if isinstance(product_data, dict):
                    add_summary = f"Product successfully added based on: '{text_input}'\n\n"
                    add_summary += f"Product Name: {product_data.get('name', 'N/A')}\n"
                    add_summary += f"Price: ₹{product_data.get('price', 'N/A')}\n"
                    add_summary += f"Stock: {product_data.get('stock', 'N/A')}\n"
                    add_summary += f"SKU: {product_data.get('sku', 'N/A')}\n"
                    add_summary += f"Description: {product_data.get('description', 'N/A')}\n"
                    
                    # Add attributes if available
                    attributes = product_data.get('attributes', [])
                    if attributes:
                        add_summary += "\nAttributes:\n"
                        for attr in attributes:
                            add_summary += f"- {attr.get('name', 'N/A')}: {attr.get('value', 'N/A')}\n"
                else:
                    add_summary = f"Product addition processed for: '{text_input}'\n\nDetails: {str(product_data)}"
                
                return jsonify({
                    "success": True,
                    "message": f"Product addition processed successfully",
                    "text_summary": add_summary,
                    "processed_text": text_input
                }), 200
            else:
                error_msg = result.get('message', 'Unknown error') if result else 'Failed to add product'
                return jsonify({
                    "success": False,
                    "message": f"Product addition failed",
                    "text_summary": f"Failed to add product from: '{text_input}'\n\nError: {error_msg}",
                    "processed_text": text_input
                }), 400
        
        elif action == 'analyze':
            # Analyze text and provide catalog insights
            from ecommerce import analyze_catalog_text
            result = analyze_catalog_text(text_input, page, limit, sort_by, sort_order)
            
            if result:
                # Convert analysis result to text summary
                if isinstance(result, dict):
                    analysis_summary = f"Text Analysis Results for: '{text_input}'\n\n"
                    analysis_summary += f"Analysis: {result.get('analysis', 'No analysis available')}\n\n"
                    
                    # Add any insights or recommendations
                    if result.get('insights'):
                        analysis_summary += f"Insights: {result.get('insights')}\n\n"
                    if result.get('recommendations'):
                        analysis_summary += f"Recommendations: {result.get('recommendations')}\n"
                else:
                    analysis_summary = f"Analysis for: '{text_input}'\n\n{str(result)}"
                
                return jsonify({
                    "success": True,
                    "message": "Text analysis completed successfully",
                    "text_summary": analysis_summary,
                    "processed_text": text_input
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "message": "Failed to analyze text",
                    "text_summary": f"Failed to analyze text: '{text_input}'\n\nPlease try again with different text.",
                    "processed_text": text_input
                }), 400
        
        else:
            return jsonify({
                "success": False,
                "message": f"Unknown action: {action}. Supported actions: summary, ai-summary, search, add-product, analyze"
            }), 400
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal server error.",
            "error": str(e)
        }), 500

@app.route('/catalog/text-summary', methods=['POST'])
def text_catalog_summary():
    """Generate catalog summary based on text input"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "message": "Missing 'text' field in request body"
            }), 400
        
        text_input = data['text']
        page = data.get('page', 1)
        limit = data.get('limit', 10)
        sort_by = data.get('sortBy', 'createdAt')
        sort_order = data.get('sortOrder', 'desc')
        
        if not text_input.strip():
            return jsonify({
                "success": False,
                "message": "Text input cannot be empty"
            }), 400
        
        # Generate AI summary with text context
        from ecommerce import get_ai_catalog_summary_with_context
        result = get_ai_catalog_summary_with_context(
            text_input, page, limit, sort_by, sort_order
        )
        
        if result:
            return jsonify({
                "success": True,
                "message": "Text-based catalog summary generated successfully",
                "data": result,
                "input_text": text_input
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Failed to generate text-based catalog summary"
            }), 400
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal server error.",
            "error": str(e)
        }), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify(ErrorResponse(
        success=False,
        message="File too large",
        error="File size exceeds the maximum limit of 16MB"
    ).model_dump()), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify(ErrorResponse(
        success=False,
        message="Endpoint not found",
        error="The requested endpoint does not exist"
    ).model_dump()), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify(ErrorResponse(
        success=False,
        message="Internal server error",
        error="An unexpected error occurred"
    ).model_dump()), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)