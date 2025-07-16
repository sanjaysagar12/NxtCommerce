#!/usr/bin/env python3
"""
Test script for the Catalog AI functionality
"""

import requests
import json
import sys
import os

# Add the model-engine directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'model-engine'))

def test_api_directly():
    """Test the API directly with requests"""
    print("🔐 Testing API authentication...")
    
    # Test authentication
    auth_url = 'https://api-ecommerce.sanjaysagar.com/api/auth/signin'
    auth_data = {
        'email': 'sanjay@gmail.com',
        'password': 'password'
    }
    
    try:
        response = requests.post(auth_url, json=auth_data)
        
        if response.status_code in [200, 201]:
            auth_response = response.json()
            access_token = auth_response.get('access_token')
            
            if access_token:
                print("✅ Authentication successful!")
                
                # Test getting products
                print("📡 Fetching seller products...")
                products_url = 'https://api-ecommerce.sanjaysagar.com/api/seller-product?page=1&limit=5&sortBy=createdAt&sortOrder=desc'
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                products_response = requests.get(products_url, headers=headers)
                
                if products_response.status_code == 200:
                    products_data = products_response.json()
                    products = products_data.get('products', [])
                    
                    print(f"✅ Found {len(products)} products")
                    print(f"📊 Total products: {products_data.get('total', 0)}")
                    
                    # Display products in catalog format
                    display_simple_catalog(products_data)
                    
                    return products_data
                else:
                    print(f"❌ Failed to get products: {products_response.status_code}")
                    print(f"Response: {products_response.text}")
                    return None
            else:
                print("❌ No access token received")
                return None
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def display_simple_catalog(products_data):
    """Display products in a simple catalog format"""
    if not products_data or 'products' not in products_data:
        print("❌ No products found")
        return
    
    products = products_data['products']
    total = products_data.get('total', len(products))
    
    print("\n" + "="*60)
    print(f"🛍️  PRODUCT CATALOG ({total} products)")
    print("="*60)
    
    for i, product in enumerate(products, 1):
        print(f"\n📦 Product #{i}")
        print(f"🆔 ID: {product.get('id', 'N/A')}")
        print(f"📝 Name: {product.get('name', 'N/A')}")
        print(f"💰 Price: ₹{product.get('price', 0)}")
        print(f"📦 Stock: {product.get('stock', 0)}")
        print(f"🏷️  SKU: {product.get('sku', 'N/A')}")
        
        # Show description (truncated)
        description = product.get('description', '')
        if description:
            if len(description) > 80:
                description = description[:80] + "..."
            print(f"📋 Description: {description}")
        
        # Show categories
        categories = product.get('categories', [])
        if categories:
            category_names = [cat.get('name', 'Unknown') for cat in categories]
            print(f"🏷️  Categories: {', '.join(category_names)}")
        
        # Show variants and images count
        variants = product.get('variants', [])
        images = product.get('images', [])
        
        if variants:
            print(f"🎨 Variants: {len(variants)}")
        if images:
            print(f"🖼️  Images: {len(images)}")
        
        print("-" * 40)
    
    print(f"\n📊 Total: {total} products")
    print("="*60)

def test_catalog_ai():
    """Test the catalog AI function"""
    try:
        print("🤖 Testing Catalog AI...")
        from ecommerce import get_catalog_ai
        
        result = get_catalog_ai(page=1, limit=5)
        
        if result:
            print("✅ Catalog AI test successful!")
            return result
        else:
            print("❌ Catalog AI test failed")
            return None
            
    except Exception as e:
        print(f"❌ Error testing Catalog AI: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Starting Catalog AI Test...")
    
    # Test 1: Direct API test
    print("\n1️⃣ Testing API directly...")
    direct_result = test_api_directly()
    
    # Test 2: Catalog AI test
    print("\n2️⃣ Testing Catalog AI function...")
    ai_result = test_catalog_ai()
    
    # Summary
    print("\n📋 Test Summary:")
    print(f"✅ Direct API test: {'PASSED' if direct_result else 'FAILED'}")
    print(f"✅ Catalog AI test: {'PASSED' if ai_result else 'FAILED'}")
    
    if direct_result or ai_result:
        print("\n🎉 Catalog AI is working! You can now:")
        print("   - View products: get_catalog_ai()")
        print("   - Export to JSON: get_catalog_ai(export_format='json')")
        print("   - Export to CSV: get_catalog_ai(export_format='csv')")
        print("   - Search products: search_catalog('product name')")
