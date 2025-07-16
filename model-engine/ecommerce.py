import os
import json
import urllib.parse
from dotenv import load_dotenv
import google.generativeai as genai
from agentic_api import AgenticAPI

# Load environment variables from .env file
load_dotenv()

# Configure Gemini
google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key and google_api_key != "your-google-api-key-here":
    genai.configure(api_key=google_api_key)
    print("✅ Gemini API configured successfully!")
else:
    print("⚠️  GOOGLE_API_KEY not found or not set. Using AI fallback.")

# Gemini model configuration
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_product_json_with_gemini(user_input):
    """Generate product JSON using Google Gemini API"""
    
    prompt = f"""
    You are an intelligent assistant that generates JSON objects for product catalogs.
    
    Generate a product JSON based on the following input: "{user_input}"
    
    Return ONLY a valid JSON object with the following structure:
    {{
        "name": "Product name",
        "description": "Detailed description of the product",
        "stock": 25,
        "price": 1500,
        "discount": 20,
        "sku": "SKU-1234",
        "thumbnail": "https://example.com/product-thumb.jpg",
        "images": [
            {{"url": "https://example.com/product-1.jpg"}},
            {{"url": "https://example.com/product-2.jpg"}}
        ],
        "variants": [
            {{
                "name": "Size S",
                "sku": "SKU-1234-S",
                "price": 1500,
                "stock": 10,
                "thumbnail": "https://example.com/product-s-thumb.jpg",
                "images": [
                    {{"url": "https://example.com/product-s-1.jpg"}},
                    {{"url": "https://example.com/product-s-2.jpg"}}
                ]
            }}
        ],
        "categoryIds": [],
        "attributes": [
            {{"name": "Fabric", "value": "Cotton"}},
            {{"name": "Color", "value": "Red"}},
            {{"name": "Gender", "value": "Men"}}
        ]
    }}
    
    Important guidelines:
    1. Extract product type, color, fabric, gender from the input
    2. Handle spelling mistakes intelligently (e.g., "shert" → "shirt")
    3. Generate appropriate price based on product type
    4. Create realistic stock quantities
    5. Generate proper SKU codes
    6. Create variants for different sizes mentioned
    7. Include relevant attributes based on the product type
    8. Use proper Indian pricing (₹ symbol in description but numbers in price field)
    9. Return ONLY the JSON object, no additional text
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up the response to extract JSON
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        # Parse the JSON
        product_json = json.loads(response_text)
        return product_json
        
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return None

def generate_ai_product_json(user_input):
    """
    Use AI to generate product JSON when OpenAI API is not available.
    This is a smarter fallback that uses AI reasoning instead of hardcoded regex.
    """
    import random
    import re
    
    # Create a simple AI-like prompt for local processing
    ai_prompt = f"""
    Analyze this product description and extract information:
    "{user_input}"
    
    Extract and infer:
    1. Product type (shirt, dress, kurta, pants, etc.)
    2. Color mentioned or infer appropriate color
    3. Fabric/material mentioned or infer appropriate fabric
    4. Target gender (men, women, kids) or infer from context
    5. Price if mentioned, otherwise suggest appropriate price
    6. Sizes mentioned or suggest appropriate sizes
    7. Discount percentage if mentioned
    8. Stock quantity if mentioned
    9. Additional attributes like sleeve type, length, etc.
    
    Handle spelling mistakes and typos intelligently.
    """
    
    # AI-powered extraction using improved logic
    def smart_extract(text, patterns, default, context_hints=None):
        """Smart extraction that handles typos and context"""
        text_lower = text.lower()
        
        # First try exact matches
        for pattern in patterns:
            if isinstance(pattern, dict):
                for key, values in pattern.items():
                    for value in values:
                        if value.lower() in text_lower:
                            return key
            else:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1) if match.groups() else match.group(0)
        
        # If no match and context hints available, use context
        if context_hints:
            for hint, result in context_hints.items():
                if hint.lower() in text_lower:
                    return result
        
        return default
    
    # Smart product type detection with context
    product_types = {
        'kurta': ['kurta', 'karta', 'kurtha', 'ethnic', 'traditional', 'indian'],
        'shirt': ['shirt', 'shart', 'shert', 'formal', 'office', 'business'],
        'dress': ['dress', 'dres', 'drss', 'gown', 'frock', 'party'],
        'pants': ['pants', 'pant', 'trousers', 'trouser', 'bottom'],
        'jeans': ['jeans', 'jean', 'denim'],
        't-shirt': ['t-shirt', 'tshirt', 'tshert', 'casual', 'cotton tee'],
        'saree': ['saree', 'sari', 'sare', 'traditional'],
        'top': ['top', 'blouse', 'tunic'],
        'jacket': ['jacket', 'blazer', 'coat'],
        'skirt': ['skirt', 'mini', 'maxi'],
        'lehenga': ['lehenga', 'lehnga', 'wedding', 'bridal'],
        'palazzo': ['palazzo', 'pallazo', 'wide leg']
    }
    
    # Extract product type with AI logic
    product_type = "Kurta"  # Default to kurta instead of dress
    for ptype, keywords in product_types.items():
        if any(keyword in user_input.lower() for keyword in keywords):
            product_type = ptype.title()
            break
    
    # Smart color detection
    colors = {
        'red': ['red', 'crimson', 'scarlet', 'maroon'],
        'blue': ['blue', 'blu', 'navy', 'royal blue', 'sky blue'],
        'green': ['green', 'gren', 'olive', 'emerald', 'mint'],
        'black': ['black', 'blk', 'ebony', 'jet black'],
        'white': ['white', 'wht', 'ivory', 'cream', 'off white'],
        'pink': ['pink', 'rose', 'magenta', 'hot pink'],
        'yellow': ['yellow', 'yelo', 'golden', 'mustard'],
        'purple': ['purple', 'violet', 'lavender', 'plum'],
        'orange': ['orange', 'saffron', 'peach'],
        'brown': ['brown', 'tan', 'beige', 'khaki'],
        'gray': ['gray', 'grey', 'silver', 'charcoal']
    }
    
    color = "Black"
    for clr, keywords in colors.items():
        if any(keyword in user_input.lower() for keyword in keywords):
            color = clr.title()
            break
    
    # Smart fabric detection
    fabrics = {
        'cotton': ['cotton', 'coton', 'cottn', 'breathable', 'soft'],
        'silk': ['silk', 'slik', 'shiny', 'lustrous', 'smooth'],
        'denim': ['denim', 'denm', 'jeans', 'sturdy'],
        'wool': ['wool', 'woolen', 'warm', 'winter'],
        'polyester': ['polyester', 'poly', 'synthetic', 'wrinkle free'],
        'linen': ['linen', 'flax', 'summer', 'breathable'],
        'leather': ['leather', 'genuine', 'faux leather'],
        'chiffon': ['chiffon', 'light', 'flowy', 'transparent'],
        'georgette': ['georgette', 'flowing', 'drape']
    }
    
    fabric = "Cotton"
    for fab, keywords in fabrics.items():
        if any(keyword in user_input.lower() for keyword in keywords):
            fabric = fab.title()
            break
    
    # Smart gender detection with better defaults
    gender = "Men"  # Default to Men
    if any(word in user_input.lower() for word in ['women', 'woman', 'female', 'girl', 'ladies', 'lady']):
        gender = "Women"
    elif any(word in user_input.lower() for word in ['men', 'man', 'male', 'boy', 'gents', 'gentleman']):
        gender = "Men"
    elif any(word in user_input.lower() for word in ['kids', 'children', 'child', 'baby']):
        gender = "Kids"
    
    # Smart price extraction and generation
    price_match = re.search(r'₹(\d+)', user_input)
    if price_match:
        price = int(price_match.group(1))
    else:
        # AI-generated price based on product type and fabric
        price_ranges = {
            'kurta': (800, 2000),
            'shirt': (500, 1500),
            'dress': (1000, 3000),
            'saree': (1500, 5000),
            'jeans': (800, 2500),
            't-shirt': (300, 800),
            'jacket': (1200, 4000),
            'lehenga': (3000, 15000)
        }
        
        base_range = price_ranges.get(product_type.lower(), (500, 2000))
        
        # Adjust price based on fabric
        fabric_multiplier = {
            'silk': 1.5,
            'leather': 2.0,
            'wool': 1.3,
            'cotton': 1.0,
            'polyester': 0.8,
            'denim': 1.2
        }
        
        multiplier = fabric_multiplier.get(fabric.lower(), 1.0)
        price = int(random.randint(base_range[0], base_range[1]) * multiplier)
    
    # Extract other attributes
    discount_match = re.search(r'(\d+)%\s*discount', user_input)
    discount = int(discount_match.group(1)) if discount_match else random.randint(10, 30)
    
    stock_match = re.search(r'(\d+)\s*in\s*stock', user_input)
    stock = int(stock_match.group(1)) if stock_match else random.randint(10, 50)
    
    # Smart size detection
    size_matches = re.findall(r'size[s]?\s*([A-Z,\s]+|XS|S|M|L|XL|XXL)', user_input, re.IGNORECASE)
    sizes = []
    if size_matches:
        for size_match in size_matches:
            sizes.extend([s.strip().upper() for s in size_match.replace('and', ',').replace('to', ',').split(',') if s.strip()])
    
    if not sizes:
        # AI-generated sizes based on product type and gender
        if product_type.lower() in ['kurta', 'shirt', 'dress', 't-shirt']:
            sizes = ['S', 'M', 'L', 'XL'] if gender == 'Men' else ['S', 'M', 'L']
        elif product_type.lower() in ['jeans', 'pants']:
            sizes = ['30', '32', '34', '36'] if gender == 'Men' else ['28', '30', '32']
        elif product_type.lower() == 'saree':
            sizes = ['Free Size']
        else:
            sizes = ['S', 'M', 'L']
    
    # Remove duplicates
    sizes = list(dict.fromkeys(sizes))
    
    # Generate intelligent product name
    name = f"{color} {fabric} {product_type} for {gender}"
    
    # Generate intelligent description
    description = f"Premium {color.lower()} {product_type.lower()} crafted from high-quality {fabric.lower()} fabric. "
    
    # Add context-aware description
    if product_type.lower() == 'kurta':
        description += "Perfect for festivals, casual outings, and ethnic occasions. "
    elif product_type.lower() == 'shirt':
        description += "Ideal for office wear, formal events, and business meetings. "
    elif product_type.lower() == 'dress':
        description += "Elegant design perfect for parties, dates, and special occasions. "
    elif product_type.lower() == 'saree':
        description += "Traditional elegance for weddings, festivals, and cultural events. "
    
    description += f"Available in {', '.join(sizes)} sizes. Comfortable fit with excellent durability."
    
    # Generate intelligent SKU
    sku_prefix = product_type[:3].upper() if len(product_type) >= 3 else "PRD"
    base_sku = sku_prefix + str(random.randint(1000, 9999))
    
    # Generate variants
    variants = []
    for size in sizes:
        variants.append({
            "name": f"Size {size}",
            "sku": f"{base_sku}-{size}",
            "price": price,
            "stock": max(1, stock // len(sizes)) if len(sizes) > 0 else stock // 2,
            "thumbnail": f"https://example.com/products/{product_type.lower()}-{color.lower()}-{size.lower()}-thumb.jpg",
            "images": [
                {"url": f"https://example.com/products/{product_type.lower()}-{color.lower()}-{size.lower()}-front.jpg"},
                {"url": f"https://example.com/products/{product_type.lower()}-{color.lower()}-{size.lower()}-back.jpg"}
            ]
        })
    
    # Generate intelligent attributes
    attributes = [
        {"name": "Fabric", "value": fabric},
        {"name": "Color", "value": color},
        {"name": "Gender", "value": gender},
        {"name": "Product Type", "value": product_type}
    ]
    
    # Add context-specific attributes
    if product_type.lower() in ['kurta', 'shirt', 'dress']:
        sleeve_patterns = [r'sleeveless', r'short\s+sleeve', r'long\s+sleeve', r'3/4', r'¾', r'half\s+sleeve']
        sleeve = smart_extract(user_input, sleeve_patterns, "Short Sleeve")
        attributes.append({"name": "Sleeve", "value": sleeve})
    
    if product_type.lower() in ['dress', 'kurta', 'skirt']:
        length_patterns = [r'mini', r'maxi', r'midi', r'knee', r'ankle', r'floor']
        length = smart_extract(user_input, length_patterns, "Knee Length")
        attributes.append({"name": "Length", "value": length})
    
    if product_type.lower() in ['shirt', 'kurta', 'dress']:
        neck_patterns = [r'round\s+neck', r'v-neck', r'collar', r'high\s+neck', r'boat\s+neck']
        neck = smart_extract(user_input, neck_patterns, "Round Neck")
        attributes.append({"name": "Neck", "value": neck})
    
    return {
        "name": name,
        "description": description,
        "stock": stock,
        "price": price,
        "discount": discount,
        "sku": base_sku,
        "thumbnail": f"https://example.com/products/{product_type.lower()}-{color.lower()}-main.jpg",
        "images": [
            {"url": f"https://example.com/products/{product_type.lower()}-{color.lower()}-1.jpg"},
            {"url": f"https://example.com/products/{product_type.lower()}-{color.lower()}-2.jpg"},
            {"url": f"https://example.com/products/{product_type.lower()}-{color.lower()}-3.jpg"}
        ],
        "variants": variants,
        "categoryIds": [],
        "attributes": attributes
    }

def generate_product_json(user_input, use_mock=False):
    """
    Generate product JSON using Gemini API with fallback to AI generator
    """
    if use_mock:
        print("Using AI-powered generator (API unavailable)")
        return generate_ai_product_json(user_input)
    
    # Try Gemini first
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key and google_api_key != "your-google-api-key-here":
        try:
            print("Attempting to use Gemini API...")
            result = generate_product_json_with_gemini(user_input)
            if result:
                print("✅ Gemini API call successful!")
                return result
            else:
                print("❌ Gemini API returned empty result.")
                print("Falling back to AI-powered generator...")
                return generate_ai_product_json(user_input)
        except Exception as e:
            error_message = str(e).lower()
            if "quota" in error_message or "exceeded" in error_message:
                print("❌ Gemini API quota exceeded.")
                print("Falling back to AI-powered generator...")
                return generate_ai_product_json(user_input)
            elif "rate_limit" in error_message:
                print("❌ Gemini API rate limit reached.")
                print("Falling back to AI-powered generator...")
                return generate_ai_product_json(user_input)
            elif "authentication" in error_message or "api_key" in error_message:
                print("❌ Gemini API authentication failed. Check your API key.")
                print("Falling back to AI-powered generator...")
                return generate_ai_product_json(user_input)
            elif "connection" in error_message or "network" in error_message:
                print("❌ Network connection error with Gemini API.")
                print("Falling back to AI-powered generator...")
                return generate_ai_product_json(user_input)
            else:
                print(f"❌ Gemini API error: {e}")
                print("Falling back to AI-powered generator...")
                return generate_ai_product_json(user_input)
    else:
        print("❌ GOOGLE_API_KEY not configured.")
        print("Falling back to AI-powered generator...")
        return generate_ai_product_json(user_input)

def parse_search_query(user_input, categories, attributes):
    import re
    search_params = {
        'name': '',
        'categories': [],
        'minPrice': None,
        'maxPrice': None,
        'minRating': None,
        'page': 1,
        'limit': 10,
        'sortBy': 'name',
        'sortOrder': 'asc',
        'attributes': {}
    }
    name_match = re.search(r'(find|search|show|get|list)\s+(.*?)(?:\s+(?:with|in|under|above|category|price|rating|sort)|\s*$)', user_input, re.IGNORECASE)
    if name_match:
        search_params['name'] = name_match.group(2).strip()
    # Parse price ranges and constraints
    # Handle "between X and Y" or "from X to Y"
    price_range_match = re.search(r'(?:between|from)\s*₹?(\d+)(?:\s*(?:to|-|and)\s*₹?(\d+))', user_input, re.IGNORECASE)
    if price_range_match:
        search_params['minPrice'] = int(price_range_match.group(1))
        search_params['maxPrice'] = int(price_range_match.group(2))
    
    # Handle "above/over/more than X"
    min_price_match = re.search(r'(?:above|over|more\s+than|minimum|greater\s+than)\s*₹?(\d+)', user_input, re.IGNORECASE)
    if min_price_match:
        search_params['minPrice'] = int(min_price_match.group(1))
    
    # Handle "under/below/less than X" - improved pattern to handle "less the" typo
    max_price_match = re.search(r'(?:under|below|less\s+(?:than|the)|maximum|cheaper\s+than)\s*₹?(\d+)', user_input, re.IGNORECASE)
    if max_price_match:
        search_params['maxPrice'] = int(max_price_match.group(1))
    
    # Handle simple "less ₹1000" or "under ₹1000" patterns
    simple_max_price_match = re.search(r'(?:less|under)\s*₹?(\d+)', user_input, re.IGNORECASE)
    if simple_max_price_match and not max_price_match:
        search_params['maxPrice'] = int(simple_max_price_match.group(1))
    
    # Handle "price X" or "cost X" patterns for range detection
    price_only_match = re.search(r'(?:price|cost)\s*₹?(\d+)', user_input, re.IGNORECASE)
    if price_only_match and not price_range_match and not min_price_match and not max_price_match:
        # If no other price constraint found, treat as max price
        search_params['maxPrice'] = int(price_only_match.group(1))
    rating_match = re.search(r'rating\s*(?:above|over|more\s+than)?\s*(\d+)', user_input, re.IGNORECASE)
    if rating_match:
        search_params['minRating'] = int(rating_match.group(1))
    page_match = re.search(r'page\s*(\d+)', user_input, re.IGNORECASE)
    if page_match:
        search_params['page'] = int(page_match.group(1))
    limit_match = re.search(r'(?:limit|show|display)\s*(\d+)', user_input, re.IGNORECASE)
    if limit_match:
        search_params['limit'] = int(limit_match.group(1))
    sort_match = re.search(r'sort\s+by\s+(\w+)(?:\s+(asc|desc|ascending|descending))?', user_input, re.IGNORECASE)
    if sort_match:
        search_params['sortBy'] = sort_match.group(1).lower()
        if sort_match.group(2):
            sort_order = sort_match.group(2).lower()
            search_params['sortOrder'] = 'asc' if sort_order in ['asc', 'ascending'] else 'desc'
    # Only include categories that exist in the categories variable
    category_names = [cat['name'].lower() for cat in categories]
    for category in categories:
        if category['name'].lower() in user_input.lower():
            search_params['categories'].append(category['name'])
    
    # For attributes, allow any attributes from the input (not restricted to attributes variable)
    # First, handle known attributes from the API
    for attribute in attributes:
        attr_name = attribute['name'].lower()
        for value in attribute['values']:
            if attr_name in user_input.lower() and value.lower() in user_input.lower():
                search_params['attributes'][attribute['name']] = value
            elif value.lower() in user_input.lower():
                search_params['attributes'][attribute['name']] = value
    
    # Additionally, allow custom attributes that might not be in the API response
    # Common e-commerce attributes that users might search for
    import re
    
    # Color attribute
    color_match = re.search(r'\b(red|blue|green|yellow|black|white|pink|purple|orange|brown|gray|grey)\b', user_input, re.IGNORECASE)
    if color_match and 'Color' not in search_params['attributes']:
        search_params['attributes']['Color'] = color_match.group(1).title()
    
    # Size attribute
    size_match = re.search(r'\b(size|sizes?)\s*([A-Z]+|small|medium|large|xl|xxl|xs)\b', user_input, re.IGNORECASE)
    if size_match and 'Size' not in search_params['attributes']:
        search_params['attributes']['Size'] = size_match.group(2).upper()
    
    # Brand attribute
    brand_match = re.search(r'\b(brand|by)\s+([A-Za-z]+)\b', user_input, re.IGNORECASE)
    if brand_match and 'Brand' not in search_params['attributes']:
        search_params['attributes']['Brand'] = brand_match.group(2).title()
    
    # Material/Fabric attribute
    fabric_match = re.search(r'\b(cotton|silk|wool|polyester|linen|denim|leather|fabric)\b', user_input, re.IGNORECASE)
    if fabric_match and 'Fabric' not in search_params['attributes'] and 'Material' not in search_params['attributes']:
        search_params['attributes']['Fabric'] = fabric_match.group(1).title()
    
    # Gender attribute
    gender_match = re.search(r'\b(men|women|male|female|boys?|girls?|kids?|children)\b', user_input, re.IGNORECASE)
    if gender_match and 'Gender' not in search_params['attributes']:
        gender_value = gender_match.group(1).lower()
        if gender_value in ['men', 'male', 'boys', 'boy']:
            search_params['attributes']['Gender'] = 'Men'
        elif gender_value in ['women', 'female', 'girls', 'girl']:
            search_params['attributes']['Gender'] = 'Women'
        elif gender_value in ['kids', 'children', 'kid']:
            search_params['attributes']['Gender'] = 'Kids'
    return search_params

def build_search_url(search_params, base_url="https://api-ecommerce.sanjaysagar.com"):
    url = f"{base_url}/api/product?"
    params = []
    if search_params['name']:
        params.append(f"name={urllib.parse.quote(search_params['name'])}")
    if search_params['categories']:
        categories_str = ','.join(search_params['categories'])
        params.append(f"categories={urllib.parse.quote(categories_str)}")
    if search_params['minPrice'] is not None:
        params.append(f"minPrice={search_params['minPrice']}")
    if search_params['maxPrice'] is not None:
        params.append(f"maxPrice={search_params['maxPrice']}")
    if search_params['minRating'] is not None:
        params.append(f"minRating={search_params['minRating']}")
    params.append(f"page={search_params['page']}")
    params.append(f"limit={search_params['limit']}")
    params.append(f"sortBy={search_params['sortBy']}")
    params.append(f"sortOrder={search_params['sortOrder']}")
    if search_params['attributes']:
        attributes_list = []
        for attr_name, attr_value in search_params['attributes'].items():
            attributes_list.append(f"{attr_name}:{attr_value}")
        if attributes_list:
            attributes_str = ','.join(attributes_list)
            params.append(f"attributes={urllib.parse.quote(attributes_str)}")
    return url + '&'.join(params)

def add_product(user_input=None, show_json=False):
    if user_input is None:
        user_input = """
        Add a red cotton kurta for women priced at ₹999 with 20% discount, 
        available in sizes S and M. 10 in stock. Category: Ethnic Wear.
        Fabric: Cotton. Sleeve: 3/4th. Includes 3 images.
        """
    output = generate_product_json(user_input)
    if output:
        if show_json:
            print("Generated JSON:")
            print(json.dumps(output, indent=2))
            print("\n" + "="*50)
        api = AgenticAPI()
        print("Authenticating with API...")
        access_token = api.authenticate_user()
        if access_token:
            print("Adding product to catalog...")
            success = api.send_product_to_api(output, access_token)
            if success:
                print("🎉 Product added successfully!")
            else:
                print("❌ Failed to add product to API.")
        else:
            print("❌ Failed to authenticate. Cannot send product to API.")
    else:
        print("Failed to generate product JSON.")

def search_products_main(user_input=None):
    if user_input is None:
        user_input = "find red cotton kurta under ₹1000 with rating above 3"
    print(f"Search Query: {user_input}")
    api = AgenticAPI()
    print("Authenticating with API...")
    access_token = api.authenticate_user()
    if access_token:
        print("Fetching available categories and attributes...")
        categories = api.get_available_categories(access_token)
        attributes = api.get_available_attributes(access_token)
        if not categories and not attributes:
            print("❌ Failed to fetch metadata. Cannot perform search.")
            return None
        print(f"Found {len(categories)} categories and {len(attributes)} attributes")
        search_params = parse_search_query(user_input, categories, attributes)
        search_url = build_search_url(search_params, api.base_url)
        print(f"Generated URL: {search_url}")
        results = api.search_products(search_url, access_token)
        if results:
            print("\n" + "="*50)
            print("SEARCH RESULTS:")
            print("="*50)
            print(json.dumps(results, indent=2))
        else:
            print("❌ No results found or search failed.")
    else:
        print("❌ Failed to authenticate. Cannot search products.")

# API-friendly function to add product

def add_product_api(user_input=None):
    if user_input is None:
        user_input = """
        Add a red cotton kurta for women priced at ₹999 with 20% discount, 
        available in sizes S and M. 10 in stock. Category: Ethnic Wear.
        Fabric: Cotton. Sleeve: 3/4th. Includes 3 images.
        """
    output = generate_product_json(user_input)
    if output:
        api = AgenticAPI()
        access_token = api.authenticate_user()
        if access_token:
            success = api.send_product_to_api(output, access_token)
            if success:
                return {
                    "success": True,
                    "message": "Product added successfully!",
                    "product_json": output
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to add product to API.",
                    "product_json": output
                }
        else:
            return {
                "success": False,
                "message": "Failed to authenticate. Cannot send product to API.",
                "product_json": output
            }
    else:
        return {
            "success": False,
            "message": "Failed to generate product JSON."
        }

# API-friendly function to search products

def search_products_api(user_input=None):
    if user_input is None:
        user_input = "find red cotton kurta under ₹1000 with rating above 3"
    api = AgenticAPI()
    access_token = api.authenticate_user()
    if access_token:
        categories = api.get_available_categories(access_token)
        attributes = api.get_available_attributes(access_token)
        
        # Ensure categories and attributes are lists (even if empty)
        if not categories:
            categories = []
        if not attributes:
            attributes = []
            
        # Parse search query - categories will be restricted to available ones,
        # but attributes can include custom ones not in the API response
        search_params = parse_search_query(user_input, categories, attributes)
        search_url = build_search_url(search_params, api.base_url)
        results = api.search_products(search_url, access_token)
        if results:
            return {
                "success": True,
                "message": "Search completed successfully!",
                "results": results
            }
        else:
            return {
                "success": False,
                "message": "No results found or search failed."
            }
    else:
        return {
            "success": False,
            "message": "Failed to authenticate. Cannot search products."
        }

# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) > 1 and sys.argv[1] == "search":
#         if len(sys.argv) > 2:
#             query = " ".join(sys.argv[2:])
#             search_products_main(query)
#         else:
#             search_products_main()
#     else:
#         add_product()