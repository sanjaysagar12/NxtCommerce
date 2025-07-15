import os
import json
import urllib.parse
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from agentic_api import AgenticAPI

# Load environment variables from .env file
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable not set.")
    exit(1)

response_schemas = [
    ResponseSchema(name="name", description="Product name"),
    ResponseSchema(name="description", description="Detailed description of the product"),
    ResponseSchema(name="stock", description="Total stock available", type="int"),
    ResponseSchema(name="price", description="Price in INR", type="int"),
    ResponseSchema(name="discount", description="Discount in percentage", type="int"),
    ResponseSchema(name="sku", description="SKU of the product"),
    ResponseSchema(name="thumbnail", description="Main thumbnail image URL"),
    ResponseSchema(name="images", description="List of image objects with url field", type="list"),
    ResponseSchema(name="variants", description="List of product variants with name, sku, price, stock, thumbnail, and images", type="list"),
    ResponseSchema(name="categoryIds", description="List of category IDs or names", type="list"),
    ResponseSchema(name="attributes", description="List of attribute objects with name and value fields", type="list"),
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an intelligent assistant that generates JSON objects for product catalogs."),
    ("user", "Generate a product JSON based on the following input:\n{input}\n\n{format_instructions}")
])

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

def generate_mock_product_json(user_input):
    import re
    import random
    
    # Extract basic information
    price_match = re.search(r'₹(\d+)', user_input)
    discount_match = re.search(r'(\d+)%\s*discount', user_input)
    stock_match = re.search(r'(\d+)\s*in\s*stock', user_input)
    
    # Extract sizes - improved regex to handle multiple size formats
    size_matches = re.findall(r'size[s]?\s*([A-Z,\s]+|XS|S|M|L|XL|XXL)', user_input, re.IGNORECASE)
    sizes = []
    if size_matches:
        for size_match in size_matches:
            sizes.extend([s.strip().upper() for s in size_match.replace('and', ',').replace('to', ',').split(',') if s.strip()])
    
    # Remove duplicates and sort
    sizes = list(dict.fromkeys(sizes))  # Remove duplicates while preserving order
    
    # Extract colors
    color_match = re.search(r'\b(red|blue|green|yellow|black|white|pink|purple|orange|brown|gray|grey|navy|hot pink|olive|emerald)\b', user_input, re.IGNORECASE)
    color = color_match.group(1).title() if color_match else "Black"
    
    # Extract materials/fabrics
    fabric_match = re.search(r'\b(cotton|silk|wool|polyester|linen|denim|leather|spandex|satin|rayon|blend)\b', user_input, re.IGNORECASE)
    fabric = fabric_match.group(1).title() if fabric_match else "Cotton"
    
    # Extract product type
    product_type_match = re.search(r'\b(dress|kurta|shirt|pants|skirt|top|blouse|jacket|coat|sweater|bodycon|maxi|mini|sheath|wrap)\b', user_input, re.IGNORECASE)
    product_type = product_type_match.group(1).title() if product_type_match else "Dress"
    
    # Extract gender
    gender_match = re.search(r'\b(men|women|male|female|boys?|girls?|kids?|children)\b', user_input, re.IGNORECASE)
    gender = "Women"
    if gender_match:
        gender_value = gender_match.group(1).lower()
        if gender_value in ['men', 'male', 'boys', 'boy']:
            gender = 'Men'
        elif gender_value in ['women', 'female', 'girls', 'girl']:
            gender = 'Women'
        elif gender_value in ['kids', 'children', 'kid']:
            gender = 'Kids'
    
    # Extract sleeve information
    sleeve_match = re.search(r'\b(sleeveless|short sleeve|long sleeve|3/4|¾|three quarter|spaghetti straps)\b', user_input, re.IGNORECASE)
    sleeve = sleeve_match.group(1).title() if sleeve_match else "Short Sleeve"
    
    # Extract length for dresses
    length_match = re.search(r'\b(mini|maxi|midi|knee|above-knee|full length)\b', user_input, re.IGNORECASE)
    length = length_match.group(1).title() if length_match else "Knee Length"
    
    # Generate product name
    name = f"{color} {fabric} {product_type} for {gender}"
    
    # Generate description
    description = f"Stylish {color.lower()} {product_type.lower()} made from premium {fabric.lower()} fabric. Perfect for casual and formal occasions."
    
    # Generate SKU
    base_sku = product_type[:3].upper() + str(random.randint(1000, 9999))
    
    # Set defaults
    price = int(price_match.group(1)) if price_match else random.randint(500, 2000)
    discount = int(discount_match.group(1)) if discount_match else random.randint(10, 30)
    stock = int(stock_match.group(1)) if stock_match else random.randint(5, 50)
    
    # Generate variants
    variants = []
    if not sizes:
        sizes = ['S', 'M', 'L']
    
    for size in sizes:
        variants.append({
            "name": f"Size {size}",
            "sku": f"{base_sku}-{size}",
            "price": price,
            "stock": stock // len(sizes) if len(sizes) > 0 else stock // 2,
            "thumbnail": f"https://example.com/{product_type.lower()}-{color.lower()}-thumbnail.jpg",
            "images": [
                {"url": f"https://example.com/{product_type.lower()}-{color.lower()}-front.jpg"},
                {"url": f"https://example.com/{product_type.lower()}-{color.lower()}-back.jpg"}
            ]
        })
    
    # Generate attributes
    attributes = [
        {"name": "Fabric", "value": fabric},
        {"name": "Color", "value": color},
        {"name": "Gender", "value": gender}
    ]
    
    if sleeve:
        attributes.append({"name": "Sleeve", "value": sleeve})
    if length and product_type.lower() in ['dress', 'skirt']:
        attributes.append({"name": "Length", "value": length})
    
    return {
        "name": name,
        "description": description,
        "stock": stock,
        "price": price,
        "discount": discount,
        "sku": base_sku,
        "thumbnail": f"https://example.com/{product_type.lower()}-{color.lower()}-main.jpg",
        "images": [
            {"url": f"https://example.com/{product_type.lower()}-{color.lower()}-image1.jpg"},
            {"url": f"https://example.com/{product_type.lower()}-{color.lower()}-image2.jpg"},
            {"url": f"https://example.com/{product_type.lower()}-{color.lower()}-image3.jpg"}
        ],
        "variants": variants,
        "categoryIds": [],
        "attributes": attributes
    }

def generate_product_json(user_input, use_mock=False):
    if use_mock:
        print("Using mock generator (API unavailable)")
        return generate_mock_product_json(user_input)
    
    try:
        print("Attempting to use OpenAI API...")
        chain = prompt | llm | output_parser
        result = chain.invoke({
            "input": user_input,
            "format_instructions": output_parser.get_format_instructions()
        })
        print("✅ OpenAI API call successful!")
        return result
    except Exception as e:
        error_message = str(e).lower()
        if "insufficient_quota" in error_message:
            print("❌ OpenAI API quota exceeded.")
            print("Falling back to mock generator...")
            return generate_mock_product_json(user_input)
        elif "rate_limit" in error_message:
            print("❌ OpenAI API rate limit reached.")
            print("Falling back to mock generator...")
            return generate_mock_product_json(user_input)
        elif "authentication" in error_message or "api_key" in error_message:
            print("❌ OpenAI API authentication failed. Check your API key.")
            print("Falling back to mock generator...")
            return generate_mock_product_json(user_input)
        elif "connection" in error_message or "network" in error_message:
            print("❌ Network connection error with OpenAI API.")
            print("Falling back to mock generator...")
            return generate_mock_product_json(user_input)
        else:
            print(f"❌ OpenAI API error: {e}")
            print("Falling back to mock generator...")
            return generate_mock_product_json(user_input)

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