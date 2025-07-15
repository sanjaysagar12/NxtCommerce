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
    price_match = re.search(r'₹(\d+)', user_input)
    discount_match = re.search(r'(\d+)%\s*discount', user_input)
    stock_match = re.search(r'(\d+)\s*in\s*stock', user_input)
    size_matches = re.findall(r'size[s]?\s*([A-Z,\s]+)', user_input, re.IGNORECASE)
    sizes = []
    if size_matches:
        sizes = [s.strip() for s in size_matches[0].replace('and', ',').split(',') if s.strip()]
    base_sku = "KUR" + str(random.randint(1000, 9999))
    price = int(price_match.group(1)) if price_match else 999
    discount = int(discount_match.group(1)) if discount_match else 20
    stock = int(stock_match.group(1)) if stock_match else 10
    variants = []
    for size in sizes if sizes else ['S', 'M']:
        variants.append({
            "name": f"Size {size}",
            "sku": f"{base_sku}-{size}",
            "price": price,
            "stock": stock // len(sizes) if sizes else stock // 2,
            "thumbnail": "https://example.com/kurta-red-thumbnail.jpg",
            "images": [
                {"url": "https://example.com/kurta-red-front.jpg"},
                {"url": "https://example.com/kurta-red-back.jpg"}
            ]
        })
    return {
        "name": "Red Cotton Kurta for Women",
        "description": "Beautiful red cotton kurta perfect for ethnic occasions. Made from premium cotton fabric with 3/4th sleeves for comfort and style.",
        "stock": stock,
        "price": price,
        "discount": discount,
        "sku": base_sku,
        "thumbnail": "https://example.com/kurta-red-main.jpg",
        "images": [
            {"url": "https://example.com/kurta-red-image1.jpg"},
            {"url": "https://example.com/kurta-red-image2.jpg"},
            {"url": "https://example.com/kurta-red-image3.jpg"}
        ],
        "variants": variants,
        "categoryIds": [],
        "attributes": [
            {"name": "Fabric", "value": "Cotton"},
            {"name": "Sleeve", "value": "3/4th"},
            {"name": "Color", "value": "Red"},
            {"name": "Gender", "value": "Women"}
        ]
    }

def generate_product_json(user_input, use_mock=False):
    if use_mock:
        print("Using mock generator (API unavailable)")
        return generate_mock_product_json(user_input)
    try:
        chain = prompt | llm | output_parser
        return chain.invoke({
            "input": user_input,
            "format_instructions": output_parser.get_format_instructions()
        })
    except Exception as e:
        if "insufficient_quota" in str(e) or "rate_limit" in str(e).lower():
            print("Error: OpenAI API quota exceeded or rate limit reached.")
            print("Falling back to mock generator...")
            return generate_mock_product_json(user_input)
        else:
            print(f"Error generating product JSON: {e}")
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

def build_search_url(search_params, base_url="http://localhost:3000"):
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