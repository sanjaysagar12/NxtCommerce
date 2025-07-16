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
    print("⚠️  GOOGLE_API_KEY not found or not set. Using fallback generator.")

# Gemini model configuration
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_product_json_with_gemini(user_input, categories=None):
    """Generate product JSON using Google Gemini API"""
    
    # Get valid category IDs if provided
    category_info = ""
    if categories:
        category_info = f"""
        Available categories to use:
        {json.dumps(categories, indent=2)}
        
        Important: Use ONLY the category IDs from the list above. Do not make up category IDs.
        """
    
    prompt = f"""
    You are an intelligent assistant that generates JSON objects for product catalogs.
    
    Generate a product JSON based on the following input: "{user_input}"
    
    {category_info}
    
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
            {{"url": "https://example.com/product-2.jpg"}},
            {{"url": "https://example.com/product-3.jpg"}}
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
            }},
            {{
                "name": "Size M",
                "sku": "SKU-1234-M",
                "price": 1500,
                "stock": 12,
                "thumbnail": "https://example.com/product-m-thumb.jpg",
                "images": [
                    {{"url": "https://example.com/product-m-1.jpg"}},
                    {{"url": "https://example.com/product-m-2.jpg"}}
                ]
            }}
        ],
        "categoryIds": ["valid-category-id-1", "valid-category-id-2"],
        "attributes": [
            {{"name": "Fabric", "value": "Cotton"}},
            {{"name": "Color", "value": "Red"}},
            {{"name": "Gender", "value": "Women"}},
            {{"name": "Style", "value": "Traditional"}},
            {{"name": "Sleeve", "value": "3/4th"}},
            {{"name": "Fit", "value": "Regular"}}
        ]
    }}
    
    Important guidelines:
    1. Extract product type, color, fabric, gender from the input
    2. Handle spelling mistakes intelligently (e.g., "shert" → "shirt", "kurtha" → "kurta")
    3. Generate appropriate price based on product type and quality described
    4. Create realistic stock quantities (10-50 range)
    5. Generate proper SKU codes using product type abbreviations
    6. Create variants for different sizes mentioned in input
    7. Include relevant attributes based on the product type
    8. Use proper Indian pricing (₹ symbol in description but numbers in price field)
    9. Generate realistic product names that match the input
    10. Create comprehensive descriptions highlighting key features
    11. MOST IMPORTANT: Use only valid category IDs from the provided list above
    12. Return ONLY the JSON object, no additional text or markdown formatting
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

def generate_mock_product_json(user_input, categories=None):
    """
    Enhanced mock product generator with better AI-like intelligence
    """
    import re
    import random
    
    # Smart product type detection
    product_types = {
        'kurta': ['kurta', 'karta', 'kurtha', 'ethnic', 'traditional'],
        'shirt': ['shirt', 'shart', 'shert', 'formal', 'office'],
        'dress': ['dress', 'dres', 'drss', 'gown', 'frock'],
        'pants': ['pants', 'pant', 'trousers', 'trouser'],
        'jeans': ['jeans', 'jean', 'denim'],
        't-shirt': ['t-shirt', 'tshirt', 'tshert', 'casual'],
        'saree': ['saree', 'sari', 'sare'],
        'top': ['top', 'blouse', 'tunic']
    }
    
    product_type = "kurta"  # default
    for ptype, keywords in product_types.items():
        if any(keyword in user_input.lower() for keyword in keywords):
            product_type = ptype
            break
    
    # Smart color detection
    colors = {
        'red': ['red', 'crimson', 'scarlet'],
        'blue': ['blue', 'navy', 'royal'],
        'green': ['green', 'olive', 'emerald'],
        'black': ['black', 'ebony'],
        'white': ['white', 'ivory', 'cream'],
        'pink': ['pink', 'rose'],
        'yellow': ['yellow', 'golden'],
        'purple': ['purple', 'violet']
    }
    
    color = "red"  # default
    for clr, keywords in colors.items():
        if any(keyword in user_input.lower() for keyword in keywords):
            color = clr
            break
    
    # Smart gender detection
    gender = "Women"  # default
    if any(word in user_input.lower() for word in ['men', 'man', 'male', 'boy', 'gents']):
        gender = "Men"
    elif any(word in user_input.lower() for word in ['kids', 'children', 'child']):
        gender = "Kids"
    
    # Extract numerical values
    price_match = re.search(r'₹(\d+)', user_input)
    discount_match = re.search(r'(\d+)%\s*discount', user_input)
    stock_match = re.search(r'(\d+)\s*in\s*stock', user_input)
    size_matches = re.findall(r'size[s]?\s*([A-Z,\s]+)', user_input, re.IGNORECASE)
    
    # Generate realistic values
    price = int(price_match.group(1)) if price_match else random.randint(500, 2000)
    discount = int(discount_match.group(1)) if discount_match else random.randint(10, 30)
    stock = int(stock_match.group(1)) if stock_match else random.randint(10, 50)
    
    # Process sizes
    sizes = []
    if size_matches:
        sizes = [s.strip().upper() for s in size_matches[0].replace('and', ',').split(',') if s.strip()]
    else:
        sizes = ['S', 'M', 'L'] if gender != 'Kids' else ['S', 'M']
    
    # Generate SKU
    sku_prefix = product_type[:3].upper() if len(product_type) >= 3 else "PRD"
    base_sku = sku_prefix + str(random.randint(1000, 9999))
    
    # Generate variants
    variants = []
    for size in sizes:
        variants.append({
            "name": f"Size {size}",
            "sku": f"{base_sku}-{size}",
            "price": price,
            "stock": max(1, stock // len(sizes)),
            "thumbnail": f"https://example.com/{product_type}-{color}-{size.lower()}-thumb.jpg",
            "images": [
                {"url": f"https://example.com/{product_type}-{color}-{size.lower()}-front.jpg"},
                {"url": f"https://example.com/{product_type}-{color}-{size.lower()}-back.jpg"}
            ]
        })
    
    # Generate product name
    name = f"{color.title()} {product_type.title()} for {gender}"
    
    # Generate description based on product type
    descriptions = {
        'kurta': f"Beautiful {color} {product_type} perfect for ethnic occasions. Made from premium cotton fabric with comfortable fit.",
        'shirt': f"Elegant {color} {product_type} ideal for formal and casual wear. Premium quality fabric ensures comfort and durability.",
        'dress': f"Stunning {color} {product_type} perfect for special occasions. Stylish design with comfortable fit.",
        't-shirt': f"Comfortable {color} {product_type} for everyday wear. Soft fabric and modern design.",
        'saree': f"Graceful {color} {product_type} for traditional occasions. Elegant design with premium fabric.",
        'jeans': f"Trendy {color} {product_type} for casual wear. Comfortable fit with durable fabric.",
        'pants': f"Stylish {color} {product_type} suitable for various occasions. Premium quality and comfortable fit."
    }
    
    description = descriptions.get(product_type, f"Premium {color} {product_type} with excellent quality and comfort.")
    
    # Generate valid category IDs
    category_ids = []
    if categories:
        # Find matching categories based on product type and gender
        for category in categories:
            cat_name = category.get('name', '').lower()
            if any(keyword in cat_name for keyword in [product_type, gender.lower(), 'clothing', 'apparel']):
                category_ids.append(category.get('id', category.get('_id', '')))
        
        # If no matches found, use first available category
        if not category_ids and categories:
            category_ids = [categories[0].get('id', categories[0].get('_id', ''))]
    
    # Fallback if no categories provided
    if not category_ids:
        category_ids = ["default-category"]
    
    return {
        "name": name,
        "description": description,
        "stock": stock,
        "price": price,
        "discount": discount,
        "sku": base_sku,
        "thumbnail": f"https://example.com/{product_type}-{color}-main.jpg",
        "images": [
            {"url": f"https://example.com/{product_type}-{color}-image1.jpg"},
            {"url": f"https://example.com/{product_type}-{color}-image2.jpg"},
            {"url": f"https://example.com/{product_type}-{color}-image3.jpg"}
        ],
        "variants": variants,
        "categoryIds": category_ids,
        "attributes": [
            {"name": "Fabric", "value": "Cotton"},
            {"name": "Color", "value": color.title()},
            {"name": "Gender", "value": gender},
            {"name": "Product Type", "value": product_type.title()},
            {"name": "Style", "value": "Modern" if product_type in ['shirt', 'jeans', 't-shirt'] else "Traditional"}
        ]
    }

def generate_product_json(user_input, use_mock=False):
    """
    Generate product JSON using Gemini API with fallback to mock generator
    """
    # Fetch categories to ensure valid category IDs
    import requests
    categories = []
    
    try:
        print("Fetching valid category IDs...")
        response = requests.get("https://api-ecommerce.sanjaysagar.com/api/categories")
        if response.status_code == 200:
            data = response.json()
            categories = data.get('categories', [])
            print(f"✅ Found {len(categories)} valid categories")
        else:
            print(f"⚠️  Could not fetch categories, status code: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Error fetching categories: {e}")
    
    if use_mock:
        print("Using mock generator (API unavailable)")
        return generate_mock_product_json(user_input, categories)
    
    # Try Gemini first
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key and google_api_key != "your-google-api-key-here":
        try:
            print("Attempting to use Gemini API...")
            result = generate_product_json_with_gemini(user_input, categories)
            if result:
                print("✅ Gemini API call successful!")
                return result
            else:
                print("❌ Gemini API returned empty result.")
                print("Falling back to mock generator...")
                return generate_mock_product_json(user_input, categories)
        except Exception as e:
            error_message = str(e).lower()
            if "quota" in error_message or "exceeded" in error_message:
                print("❌ Gemini API quota exceeded.")
                print("Falling back to mock generator...")
                return generate_mock_product_json(user_input, categories)
            elif "rate_limit" in error_message:
                print("❌ Gemini API rate limit reached.")
                print("Falling back to mock generator...")
                return generate_mock_product_json(user_input, categories)
            elif "authentication" in error_message or "api_key" in error_message:
                print("❌ Gemini API authentication failed. Check your API key.")
                print("Falling back to mock generator...")
                return generate_mock_product_json(user_input, categories)
            elif "connection" in error_message or "network" in error_message:
                print("❌ Network connection error with Gemini API.")
                print("Falling back to mock generator...")
                return generate_mock_product_json(user_input, categories)
            else:
                print(f"❌ Gemini API error: {e}")
                print("Falling back to mock generator...")
                return generate_mock_product_json(user_input, categories)
    else:
        print("❌ GOOGLE_API_KEY not configured.")
        print("Falling back to mock generator...")
        return generate_mock_product_json(user_input, categories)

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
    price_matches = re.findall(r'(?:price|cost)\s*(?:between|from)?\s*₹?(\d+)(?:\s*(?:to|-)\s*₹?(\d+))?', user_input, re.IGNORECASE)
    if price_matches:
        min_price, max_price = price_matches[0]
        search_params['minPrice'] = int(min_price) if min_price else None
        search_params['maxPrice'] = int(max_price) if max_price else None
    min_price_match = re.search(r'(?:above|over|more\s+than|minimum)\s*₹?(\d+)', user_input, re.IGNORECASE)
    if min_price_match:
        search_params['minPrice'] = int(min_price_match.group(1))
    max_price_match = re.search(r'(?:under|below|less\s+than|maximum)\s*₹?(\d+)', user_input, re.IGNORECASE)
    if max_price_match:
        search_params['maxPrice'] = int(max_price_match.group(1))
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
    category_names = [cat['name'].lower() for cat in categories]
    for category in categories:
        if category['name'].lower() in user_input.lower():
            search_params['categories'].append(category['name'])
    for attribute in attributes:
        attr_name = attribute['name'].lower()
        for value in attribute['values']:
            if attr_name in user_input.lower() and value.lower() in user_input.lower():
                search_params['attributes'][attribute['name']] = value
            elif value.lower() in user_input.lower():
                search_params['attributes'][attribute['name']] = value
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
        if not categories and not attributes:
            return {
                "success": False,
                "message": "Failed to fetch metadata. Cannot perform search."
            }
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