import os
import json
import urllib.parse
import re
import random
import requests
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

def display_product_catalog(products_data, show_full_details=False):
    """Display products in a text summary format"""
    if not products_data or 'products' not in products_data:
        print("No products found in catalog")
        return
    
    products = products_data['products']
    total_products = products_data.get('total', len(products))
    current_page = products_data.get('page', 1)
    total_pages = products_data.get('totalPages', 1)
    
    print(f"\nPRODUCT CATALOG SUMMARY ({total_products} products)")
    print("=" * 50)
    print(f"Page {current_page} of {total_pages}")
    print("-" * 50)
    
    if not products:
        print("No products found")
        return
    
    for i, product in enumerate(products, 1):
        # Basic product info
        name = product.get('name', 'Unknown Product')
        price = product.get('price', 0)
        stock = product.get('stock', 0)
        
        # Calculate discounted price if discount exists
        discount = product.get('discount', 0)
        if discount and discount > 0:
            discounted_price = price * (1 - discount / 100)
            price_text = f"₹{price} (₹{discounted_price:.0f} after {discount}% discount)"
        else:
            price_text = f"₹{price}"
        
        # Categories summary
        categories = product.get('categories', [])
        category_text = ", ".join([cat.get('name', 'Unknown') for cat in categories]) if categories else "No category"
        
        # Variants summary
        variants = product.get('variants', [])
        variant_text = f", {len(variants)} variants" if variants else ""
        
        # Images summary
        images = product.get('images', [])
        image_text = f", {len(images)} images" if images else ""
        
        # Key attributes summary
        attributes = product.get('attributes', [])
        key_attrs = []
        for attr in attributes:
            attr_name = attr.get('name', '').lower()
            attr_value = attr.get('value', '')
            if attr_name in ['color', 'fabric', 'size', 'gender', 'style'] and attr_value:
                key_attrs.append(f"{attr_name}: {attr_value}")
        
        attr_text = f" ({', '.join(key_attrs)})" if key_attrs else ""
        
        # Format the summary line
        summary = f"{i}. {name} - {price_text}, Stock: {stock}, Category: {category_text}{variant_text}{image_text}{attr_text}"
        print(summary)
    
    print(f"\nTotal: {total_products} products")
    if total_pages > 1:
        print(f"Page {current_page} of {total_pages}")
    print("-" * 50)

def export_catalog_to_json(products_data, filename="catalog_export.json"):
    """Export catalog data to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(products_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Catalog exported to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error exporting catalog: {e}")
        return False

def export_catalog_to_csv(products_data, filename="catalog_export.csv"):
    """Export catalog data to CSV file"""
    try:
        import csv
        
        if not products_data or 'products' not in products_data:
            print("❌ No products data to export")
            return False
        
        products = products_data['products']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'name', 'price', 'discount', 'stock', 'sku', 'description', 
                         'categories', 'attributes', 'variants_count', 'images_count', 
                         'createdAt', 'updatedAt']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for product in products:
                # Process categories
                categories = product.get('categories', [])
                categories_str = '; '.join([cat.get('name', 'Unknown') for cat in categories])
                
                # Process attributes
                attributes = product.get('attributes', [])
                attributes_str = '; '.join([f"{attr.get('name', 'Unknown')}: {attr.get('value', 'N/A')}" for attr in attributes])
                
                writer.writerow({
                    'id': product.get('id', ''),
                    'name': product.get('name', ''),
                    'price': product.get('price', 0),
                    'discount': product.get('discount', 0),
                    'stock': product.get('stock', 0),
                    'sku': product.get('sku', ''),
                    'description': product.get('description', ''),
                    'categories': categories_str,
                    'attributes': attributes_str,
                    'variants_count': len(product.get('variants', [])),
                    'images_count': len(product.get('images', [])),
                    'createdAt': product.get('createdAt', ''),
                    'updatedAt': product.get('updatedAt', '')
                })
        
        print(f"✅ Catalog exported to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error exporting catalog to CSV: {e}")
        return False

def get_catalog_ai(page=1, limit=10, sort_by="createdAt", sort_order="desc", export_format=None, show_full_details=False):
    """
    Catalog AI function to fetch and display seller products
    
    Args:
        page (int): Page number for pagination
        limit (int): Number of products per page
        sort_by (str): Field to sort by (createdAt, name, price, etc.)
        sort_order (str): Sort order (asc or desc)
        export_format (str): Export format ('json' or 'csv')
        show_full_details (bool): Show full product details
    """
    print("🤖 Catalog AI - Fetching your product catalog...")
    
    # Initialize API
    api = AgenticAPI()
    
    # Authenticate
    print("🔐 Authenticating...")
    access_token = api.authenticate_user()
    
    if not access_token:
        print("❌ Authentication failed. Cannot fetch catalog.")
        return None
    
    # Fetch products
    print(f"📡 Fetching products (Page {page}, Limit {limit})...")
    products_data = api.get_seller_products(access_token, page, limit, sort_by, sort_order)
    
    if not products_data:
        print("❌ Failed to fetch products from catalog.")
        return None
    
    # Display catalog
    display_product_catalog(products_data, show_full_details)
    
    # Export if requested
    if export_format:
        if export_format.lower() == 'json':
            export_catalog_to_json(products_data)
        elif export_format.lower() == 'csv':
            export_catalog_to_csv(products_data)
        else:
            print(f"⚠️  Unknown export format: {export_format}. Supported formats: 'json', 'csv'")
    
    return products_data

# Convenience functions for common use cases
def view_catalog(page=1, limit=10):
    """Quick view of the catalog"""
    return get_catalog_ai(page=page, limit=limit)

def export_catalog_json(filename="catalog_export.json"):
    """Export entire catalog to JSON"""
    return get_catalog_ai(limit=100, export_format='json')

def export_catalog_csv(filename="catalog_export.csv"):
    """Export entire catalog to CSV"""
    return get_catalog_ai(limit=100, export_format='csv')

def search_catalog(query, page=1, limit=10):
    """Search products in catalog by name/description"""
    print(f"🔍 Searching catalog for: '{query}'")
    # This would need to be implemented based on API search capabilities
    # For now, fetch all and filter locally
    products_data = get_catalog_ai(page=page, limit=limit)
    
    if not products_data or 'products' not in products_data:
        return None
    
    # Filter products based on query
    filtered_products = []
    for product in products_data['products']:
        name = product.get('name', '').lower()
        description = product.get('description', '').lower()
        if query.lower() in name or query.lower() in description:
            filtered_products.append(product)
    
    # Create filtered response
    filtered_data = {
        'products': filtered_products,
        'total': len(filtered_products),
        'page': page,
        'totalPages': 1
    }
    
    if filtered_products:
        display_product_catalog(filtered_data)
    else:
        print(f"❌ No products found matching '{query}'")
    
    return filtered_data

def display_catalog_summary(products_data):
    """Display products in a very concise text summary format"""
    if not products_data or 'products' not in products_data:
        print("No products found")
        return
    
    products = products_data['products']
    total_products = products_data.get('total', len(products))
    
    print(f"Catalog Summary: {total_products} products total")
    print("-" * 30)
    
    for i, product in enumerate(products, 1):
        name = product.get('name', 'Unknown')
        price = product.get('price', 0)
        stock = product.get('stock', 0)
        
        # Get primary category
        categories = product.get('categories', [])
        category = categories[0].get('name', 'Uncategorized') if categories else 'Uncategorized'
        
        # Get key attributes
        attributes = product.get('attributes', [])
        color = next((attr.get('value', '') for attr in attributes if attr.get('name', '').lower() == 'color'), '')
        
        # Format compact line
        color_text = f" ({color})" if color else ""
        print(f"{i}. {name}{color_text} - ₹{price}, {stock} in stock, {category}")
    
    print(f"\nTotal: {total_products} products")

def get_catalog_text_summary(page=1, limit=10, sort_by="createdAt", sort_order="desc"):
    """
    Get catalog as a simple text summary
    """
    print("Fetching catalog summary...")
    
    # Initialize API
    api = AgenticAPI()
    
    # Authenticate
    access_token = api.authenticate_user()
    
    if not access_token:
        print("Authentication failed. Cannot fetch catalog.")
        return None
    
    # Fetch products
    products_data = api.get_seller_products(access_token, page, limit, sort_by, sort_order)
    
    if not products_data:
        print("Failed to fetch products from catalog.")
        return None
    
    # Display as text summary
    display_catalog_summary(products_data)
    
    return products_data

# AI-powered catalog summary functions

def generate_ai_catalog_summary(products_data):
    """Generate AI-powered catalog summary using Gemini"""
    try:
        # Configure Gemini
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key or google_api_key == "your-google-api-key-here":
            print("⚠️  GOOGLE_API_KEY not configured, using fallback")
            return generate_basic_catalog_summary(products_data)
        
        # Prepare data for AI analysis
        products = products_data.get('products', [])
        total_products = products_data.get('total', len(products))
        
        # Create a structured summary of the products
        product_summary = []
        for i, product in enumerate(products, 1):
            summary_item = {
                "index": i,
                "name": product.get('name', 'Unknown'),
                "price": product.get('price', 0),
                "stock": product.get('stock', 0),
                "categories": [cat.get('name', 'Unknown') for cat in product.get('categories', [])],
                "attributes": {attr.get('name', 'Unknown'): attr.get('value', 'Unknown') for attr in product.get('attributes', [])},
                "variants_count": len(product.get('variants', [])),
                "images_count": len(product.get('images', []))
            }
            product_summary.append(summary_item)
        
        # Create prompt for AI summary
        prompt = f"""
        You are an intelligent e-commerce catalog analyst. Analyze the following product catalog data and provide a comprehensive text summary.

        Catalog Data:
        - Total Products: {total_products}
        - Products Shown: {len(products)}
        
        Product Details:
        {json.dumps(product_summary, indent=2)}

        Please provide a comprehensive catalog summary that includes:
        1. Overall catalog overview (total products, categories)
        2. Price range analysis
        3. Stock availability summary
        4. Popular categories and product types
        5. Key insights and trends
        6. Concise product listings in text format

        Format the response as a readable text summary suitable for business reporting.
        Keep it concise but informative. Use bullet points where appropriate.
        Make it professional and suitable for business analysis.
        """
        
        # Generate summary using Gemini
        print("🤖 Generating AI catalog summary...")
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            print("❌ AI response was empty, using fallback")
            return generate_basic_catalog_summary(products_data)
            
    except Exception as e:
        print(f"❌ Error generating AI summary: {e}")
        print("Using fallback summary...")
        return generate_basic_catalog_summary(products_data)

def generate_basic_catalog_summary(products_data):
    """Generate basic catalog summary as fallback"""
    if not products_data or 'products' not in products_data:
        return "No products found in catalog"
    
    products = products_data['products']
    total_products = products_data.get('total', len(products))
    
    # Basic analysis
    categories = {}
    total_stock = 0
    price_range = {"min": float('inf'), "max": 0}
    
    for product in products:
        # Count categories
        for cat in product.get('categories', []):
            cat_name = cat.get('name', 'Unknown')
            categories[cat_name] = categories.get(cat_name, 0) + 1
        
        # Calculate stock and price range
        stock = product.get('stock', 0)
        price = product.get('price', 0)
        
        total_stock += stock
        if price > 0:
            price_range["min"] = min(price_range["min"], price)
            price_range["max"] = max(price_range["max"], price)
    
    # Generate summary
    summary = f"""CATALOG SUMMARY REPORT
    
📊 OVERVIEW:
- Total Products: {total_products}
- Products Displayed: {len(products)}
- Total Stock Available: {total_stock}

💰 PRICE ANALYSIS:
- Price Range: ₹{price_range["min"]:.0f} - ₹{price_range["max"]:.0f}
- Average Price: ₹{(price_range["min"] + price_range["max"]) / 2:.0f}

🏷️ CATEGORY BREAKDOWN:
"""
    
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        summary += f"- {category}: {count} products\n"
    
    summary += "\n📦 PRODUCT LISTINGS:\n"
    for i, product in enumerate(products, 1):
        name = product.get('name', 'Unknown')
        price = product.get('price', 0)
        stock = product.get('stock', 0)
        
        # Get primary category
        categories_list = product.get('categories', [])
        category = categories_list[0].get('name', 'Uncategorized') if categories_list else 'Uncategorized'
        
        summary += f"{i}. {name} - ₹{price}, Stock: {stock}, Category: {category}\n"
    
    return summary

def get_ai_catalog_summary(page=1, limit=10, sort_by="createdAt", sort_order="desc"):
    """
    Get AI-powered catalog summary
    """
    print("🤖 AI Catalog Summary - Fetching and analyzing your catalog...")
    
    # Initialize API
    api = AgenticAPI()
    
    # Authenticate
    print("🔐 Authenticating...")
    access_token = api.authenticate_user()
    
    if not access_token:
        print("❌ Authentication failed. Cannot fetch catalog.")
        return None
    
    # Fetch products
    print(f"📡 Fetching products (Page {page}, Limit {limit})...")
    products_data = api.get_seller_products(access_token, page, limit, sort_by, sort_order)
    
    if not products_data:
        print("❌ Failed to fetch products from catalog.")
        return None
    
    # Generate AI summary
    ai_summary = generate_ai_catalog_summary(products_data)
    
    if ai_summary:
        print("\n" + "="*60)
        print("🤖 AI CATALOG SUMMARY")
        print("="*60)
        print(ai_summary)
        print("="*60)
    
    return {
        "products_data": products_data,
        "ai_summary": ai_summary
    }

def catalog_ai_api(action="view", page=1, limit=10, sort_by="createdAt", sort_order="desc", show_full_details=False, query=None):
    """
    API wrapper for catalog operations
    
    Args:
        action (str): Action to perform ('view', 'export_json', 'export_csv', 'search')
        page (int): Page number for pagination
        limit (int): Number of products per page
        sort_by (str): Field to sort by
        sort_order (str): Sort order
        show_full_details (bool): Show full product details
        query (str): Search query for search action
    
    Returns:
        dict: API response with success, message, and data
    """
    try:
        # Initialize API
        api = AgenticAPI()
        
        # Authenticate
        access_token = api.authenticate_user()
        
        if not access_token:
            return {
                "success": False,
                "message": "Authentication failed. Cannot access catalog.",
                "data": None
            }
        
        if action == "view":
            # Fetch products
            products_data = api.get_seller_products(access_token, page, limit, sort_by, sort_order)
            
            if not products_data:
                return {
                    "success": False,
                    "message": "Failed to fetch products from catalog.",
                    "data": None
                }
            
            return {
                "success": True,
                "message": "Catalog retrieved successfully",
                "data": products_data
            }
        
        elif action == "export_json":
            # Fetch products and export to JSON
            products_data = api.get_seller_products(access_token, page, limit, sort_by, sort_order)
            
            if not products_data:
                return {
                    "success": False,
                    "message": "Failed to fetch products for export.",
                    "data": None
                }
            
            filename = f"catalog_export_{page}_{limit}.json"
            export_catalog_to_json(products_data, filename)
            
            return {
                "success": True,
                "message": f"Catalog exported to {filename}",
                "data": {"filename": filename, "products": products_data}
            }
        
        elif action == "export_csv":
            # Fetch products and export to CSV
            products_data = api.get_seller_products(access_token, page, limit, sort_by, sort_order)
            
            if not products_data:
                return {
                    "success": False,
                    "message": "Failed to fetch products for export.",
                    "data": None
                }
            
            filename = f"catalog_export_{page}_{limit}.csv"
            export_catalog_to_csv(products_data, filename)
            
            return {
                "success": True,
                "message": f"Catalog exported to {filename}",
                "data": {"filename": filename, "products": products_data}
            }
        
        elif action == "search":
            if not query:
                return {
                    "success": False,
                    "message": "Search query is required for search action.",
                    "data": None
                }
            
            # Use the search function with the query
            result = search_products_api(query)
            return result
        
        else:
            return {
                "success": False,
                "message": f"Unknown action: {action}. Supported actions: view, export_json, export_csv, search",
                "data": None
            }
        
    except Exception as e:
        return {
            "success": False,
            "message": "Internal server error in catalog API.",
            "error": str(e),
            "data": None
        }

def get_ai_catalog_summary_with_context(text_input, page=1, limit=10, sort_by="createdAt", sort_order="desc"):
    """
    Generate AI catalog summary with additional text context
    
    Args:
        text_input (str): User text input for context
        page (int): Page number for pagination
        limit (int): Number of products per page
        sort_by (str): Field to sort by
        sort_order (str): Sort order
    
    Returns:
        dict: AI summary with text context
    """
    try:
        # Initialize API and get products
        api = AgenticAPI()
        access_token = api.authenticate_user()
        
        if not access_token:
            return None
        
        # Fetch products
        products_data = api.get_seller_products(access_token, page, limit, sort_by, sort_order)
        
        if not products_data:
            return None
        
        # Generate AI summary with text context
        ai_summary = generate_ai_catalog_summary_with_context(products_data, text_input)
        
        if ai_summary:
            return {
                "ai_summary": ai_summary,
                "products_data": products_data,
                "text_context": text_input,
                "page": page,
                "limit": limit,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        else:
            # Fallback to basic summary
            basic_summary = generate_basic_catalog_summary(products_data)
            return {
                "basic_summary": basic_summary,
                "products_data": products_data,
                "text_context": text_input,
                "page": page,
                "limit": limit,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        
    except Exception as e:
        print(f"❌ Error generating AI catalog summary with context: {e}")
        return None

def generate_ai_catalog_summary_with_context(products_data, text_input):
    """Generate AI-powered catalog summary with user text context"""
    try:
        # Import Gemini
        import google.generativeai as genai
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Configure Gemini
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key or google_api_key == "your-google-api-key-here":
            print("⚠️  GOOGLE_API_KEY not configured, using fallback")
            return None
        
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare data for AI analysis
        products = products_data.get('products', [])
        total_products = products_data.get('total', len(products))
        
        # Create a structured summary of the products
        product_summary = []
        for i, product in enumerate(products, 1):
            summary_item = {
                "index": i,
                "name": product.get('name', 'Unknown'),
                "price": product.get('price', 0),
                "stock": product.get('stock', 0),
                "categories": [cat.get('name', 'Unknown') for cat in product.get('categories', [])],
                "attributes": {attr.get('name', 'Unknown'): attr.get('value', 'Unknown') for attr in product.get('attributes', [])},
                "variants_count": len(product.get('variants', [])),
                "images_count": len(product.get('images', []))
            }
            product_summary.append(summary_item)
        
        # Create prompt for AI summary with text context
        prompt = f"""
        You are an intelligent e-commerce catalog analyst. Analyze the following product catalog data and provide a comprehensive text summary, considering the user's specific context and requirements.

        User Context/Request: "{text_input}"

        Catalog Data:
        - Total Products: {total_products}
        - Products Shown: {len(products)}
        
        Product Details:
        {json.dumps(product_summary, indent=2)}

        Please provide a comprehensive catalog summary that addresses the user's specific context and includes:
        1. Response to the user's specific request/context
        2. Overall catalog overview relevant to the user's needs
        3. Price range analysis in context of the user's request
        4. Stock availability summary
        5. Product recommendations based on user context
        6. Key insights and trends related to the user's needs
        7. Actionable recommendations tailored to the user's request

        Format the response as a readable text summary suitable for business reporting.
        Keep it concise but informative and directly address the user's context.
        Use bullet points where appropriate.
        """
        
        # Generate summary using Gemini
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return None
            
    except ImportError:
        print("⚠️  Gemini libraries not available")
        return None
    except Exception as e:
        print(f"❌ Error generating AI summary with context: {e}")
        return None

def analyze_catalog_text(text_input, page=1, limit=10, sort_by="createdAt", sort_order="desc"):
    """
    Analyze text input in relation to catalog data
    
    Args:
        text_input (str): User text input to analyze
        page (int): Page number for pagination
        limit (int): Number of products per page
        sort_by (str): Field to sort by
        sort_order (str): Sort order
    
    Returns:
        dict: Analysis results
    """
    try:
        # Initialize API and get products
        api = AgenticAPI()
        access_token = api.authenticate_user()
        
        if not access_token:
            return None
        
        # Fetch products
        products_data = api.get_seller_products(access_token, page, limit, sort_by, sort_order)
        
        if not products_data:
            return None
        
        # Analyze text in context of catalog
        analysis_result = perform_text_analysis(text_input, products_data)
        
        return {
            "analysis": analysis_result,
            "products_data": products_data,
            "input_text": text_input,
            "page": page,
            "limit": limit,
            "sort_by": sort_by,
            "sort_order": sort_order
        }
        
    except Exception as e:
        print(f"❌ Error analyzing catalog text: {e}")
        return None

def perform_text_analysis(text_input, products_data):
    """Perform AI-powered text analysis in context of catalog"""
    try:
        # Import Gemini
        import google.generativeai as genai
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Configure Gemini
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key or google_api_key == "your-google-api-key-here":
            return perform_basic_text_analysis(text_input, products_data)
        
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare data for analysis
        products = products_data.get('products', [])
        total_products = products_data.get('total', len(products))
        
        # Create prompt for text analysis
        prompt = f"""
        You are an intelligent e-commerce text analyzer. Analyze the following user text input in the context of the provided catalog data.

        User Text Input: "{text_input}"

        Catalog Context:
        - Total Products: {total_products}
        - Products Available: {len(products)}
        - Product Types: {[p.get('name', 'Unknown') for p in products[:5]]}
        - Price Range: ₹{min([int(p.get('price', 0)) for p in products if p.get('price')])} - ₹{max([int(p.get('price', 0)) for p in products if p.get('price')])}

        Please analyze the text and provide:
        1. Intent Analysis: What is the user trying to accomplish?
        2. Catalog Relevance: How does this relate to the current catalog?
        3. Recommendations: What actions should be taken based on this input?
        4. Matching Products: Which products in the catalog match this input?
        5. Business Insights: What business insights can be derived?
        6. Next Steps: What should the user do next?

        Format the response as a structured analysis with clear sections.
        """
        
        # Generate analysis using Gemini
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return perform_basic_text_analysis(text_input, products_data)
            
    except ImportError:
        return perform_basic_text_analysis(text_input, products_data)
    except Exception as e:
        print(f"❌ Error performing text analysis: {e}")
        return perform_basic_text_analysis(text_input, products_data)

def perform_basic_text_analysis(text_input, products_data):
    """Perform basic text analysis without AI"""
    products = products_data.get('products', [])
    total_products = products_data.get('total', len(products))
    
    # Basic keyword matching
    keywords = text_input.lower().split()
    matching_products = []
    
    for product in products:
        product_name = product.get('name', '').lower()
        product_desc = product.get('description', '').lower()
        
        for keyword in keywords:
            if keyword in product_name or keyword in product_desc:
                matching_products.append(product)
                break
    
    analysis = f"""
    Basic Text Analysis Results:
    
    Input: "{text_input}"
    
    1. Intent Analysis: 
       - Keywords found: {', '.join(keywords)}
       - Potential product search or inquiry
    
    2. Catalog Relevance:
       - Total products in catalog: {total_products}
       - Matching products found: {len(matching_products)}
    
    3. Matching Products:
       {chr(10).join([f"   - {p.get('name', 'Unknown')} (₹{p.get('price', 0)})" for p in matching_products[:5]])}
    
    4. Recommendations:
       - Review matching products for relevance
       - Consider expanding search terms
       - Add more products if no matches found
    
    5. Next Steps:
       - Refine search criteria
       - Add more product details
       - Consider product categorization
    """
    
    return analysis
