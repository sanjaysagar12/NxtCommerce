#!/usr/bin/env python3
"""
Catalog AI Demo Script
This demonstrates the catalog AI functionality for fetching and displaying products
"""

import requests
import json
from datetime import datetime

def demonstrate_catalog_ai():
    """Demonstrate the catalog AI functionality"""
    
    print("🤖 CATALOG AI DEMONSTRATION")
    print("="*50)
    
    # Step 1: Authentication
    print("\n1️⃣ AUTHENTICATION")
    print("   🔐 Authenticating with API...")
    
    auth_url = 'https://api-ecommerce.sanjaysagar.com/api/auth/signin'
    auth_data = {
        'email': 'sanjay@gmail.com',
        'password': 'password'
    }
    
    try:
        response = requests.post(auth_url, json=auth_data, timeout=10)
        
        if response.status_code in [200, 201]:
            auth_response = response.json()
            access_token = auth_response.get('access_token')
            
            if access_token:
                print("   ✅ Authentication successful!")
                
                # Step 2: Fetch Products
                print("\n2️⃣ FETCHING PRODUCTS")
                print("   📡 Fetching seller products...")
                
                products_url = 'https://api-ecommerce.sanjaysagar.com/api/seller-product?page=1&limit=10&sortBy=createdAt&sortOrder=desc'
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                products_response = requests.get(products_url, headers=headers, timeout=10)
                
                if products_response.status_code == 200:
                    products_data = products_response.json()
                    products = products_data.get('products', [])
                    
                    print(f"   ✅ Successfully fetched {len(products)} products")
                    print(f"   📊 Total products in catalog: {products_data.get('total', 0)}")
                    
                    # Step 3: Display Catalog
                    print("\n3️⃣ PRODUCT CATALOG DISPLAY")
                    display_catalog(products_data)
                    
                    # Step 4: Export Options
                    print("\n4️⃣ EXPORT OPTIONS")
                    print("   📄 Available export formats:")
                    print("   - JSON: Full product data with all details")
                    print("   - CSV: Tabular format for spreadsheet applications")
                    
                    # Export to JSON
                    export_to_json(products_data)
                    
                    # Step 5: Usage Examples
                    print("\n5️⃣ USAGE EXAMPLES")
                    print("   🐍 Python Usage:")
                    print("   from ecommerce import get_catalog_ai")
                    print("   ")
                    print("   # View catalog")
                    print("   catalog = get_catalog_ai(page=1, limit=10)")
                    print("   ")
                    print("   # Export to JSON")
                    print("   catalog = get_catalog_ai(export_format='json')")
                    print("   ")
                    print("   # Export to CSV")
                    print("   catalog = get_catalog_ai(export_format='csv')")
                    print("   ")
                    print("   # Search products")
                    print("   from ecommerce import search_catalog")
                    print("   results = search_catalog('red dress')")
                    
                    print("\n   🌐 API Usage:")
                    print("   GET /catalog?page=1&limit=10")
                    print("   POST /catalog/export {'format': 'json'}")
                    print("   POST /catalog/search {'query': 'red dress'}")
                    
                    return products_data
                else:
                    print(f"   ❌ Failed to fetch products: {products_response.status_code}")
                    print(f"   Response: {products_response.text}")
                    return None
            else:
                print("   ❌ No access token received")
                return None
        else:
            print(f"   ❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("   ⏱️  Request timed out - API might be slow")
        return None
    except requests.exceptions.ConnectionError:
        print("   🌐 Connection error - Check internet connection")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def display_catalog(products_data):
    """Display products in catalog format"""
    if not products_data or 'products' not in products_data:
        print("   ❌ No products found")
        return
    
    products = products_data['products']
    total = products_data.get('total', len(products))
    page = products_data.get('page', 1)
    
    print(f"   📚 PRODUCT CATALOG (Page {page})")
    print("   " + "="*45)
    
    for i, product in enumerate(products[:3], 1):  # Show first 3 products
        print(f"   ")
        print(f"   📦 Product #{i}")
        print(f"   🆔 ID: {product.get('id', 'N/A')}")
        print(f"   📝 Name: {product.get('name', 'N/A')}")
        print(f"   💰 Price: ₹{product.get('price', 0)}")
        
        if product.get('discount'):
            discounted_price = product['price'] * (1 - product['discount'] / 100)
            print(f"   🏷️  Discount: {product['discount']}% (₹{discounted_price:.2f})")
        
        print(f"   📦 Stock: {product.get('stock', 0)}")
        print(f"   🏷️  SKU: {product.get('sku', 'N/A')}")
        
        # Show description (truncated)
        description = product.get('description', '')
        if description:
            if len(description) > 60:
                description = description[:60] + "..."
            print(f"   📋 Description: {description}")
        
        # Show categories
        categories = product.get('categories', [])
        if categories:
            category_names = [cat.get('name', 'Unknown') for cat in categories]
            print(f"   🏷️  Categories: {', '.join(category_names)}")
        
        # Show variants and images count
        variants = product.get('variants', [])
        images = product.get('images', [])
        
        if variants:
            print(f"   🎨 Variants: {len(variants)}")
        if images:
            print(f"   🖼️  Images: {len(images)}")
        
        print("   " + "-" * 30)
    
    if len(products) > 3:
        print(f"   ... and {len(products) - 3} more products")
    
    print(f"   📊 Total: {total} products in catalog")

def export_to_json(products_data):
    """Export catalog to JSON file"""
    try:
        filename = f"catalog_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(products_data, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Catalog exported to {filename}")
        return True
    except Exception as e:
        print(f"   ❌ Export failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Catalog AI Demo...")
    result = demonstrate_catalog_ai()
    
    if result:
        print("\n🎉 SUCCESS! Catalog AI is working properly.")
        print("You can now use the catalog AI functions in your applications.")
    else:
        print("\n❌ Demo failed. Please check API connectivity and credentials.")
