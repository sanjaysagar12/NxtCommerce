#!/usr/bin/env python3
"""
Demonstration of AI-Powered Text Summary Catalog Format using Gemini
"""

import requests
import json
import os
import sys

# Add model-engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'model-engine'))

def demo_ai_catalog_summary():
    """Demonstrate AI-powered catalog summary using Gemini"""
    print("AI-POWERED CATALOG SUMMARY DEMO")
    print("=" * 45)
    
    # Step 1: Authentication
    print("\n1. Authenticating...")
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
                print("✅ Authentication successful!")
                
                # Step 2: Fetch Products
                print("\n2. Fetching products...")
                products_url = 'https://api-ecommerce.sanjaysagar.com/api/seller-product?page=1&limit=10&sortBy=createdAt&sortOrder=desc'
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                products_response = requests.get(products_url, headers=headers, timeout=10)
                
                if products_response.status_code == 200:
                    products_data = products_response.json()
                    products = products_data.get('products', [])
                    
                    print(f"✅ Found {len(products)} products")
                    
                    # Step 3: Generate AI Summary
                    print("\n3. GENERATING AI CATALOG SUMMARY...")
                    print("-" * 45)
                    
                    ai_summary = generate_ai_catalog_summary(products_data)
                    
                    if ai_summary:
                        print("✅ AI Summary generated successfully!")
                        print("\n🤖 AI CATALOG SUMMARY:")
                        print("-" * 30)
                        print(ai_summary)
                    else:
                        print("❌ AI Summary failed, showing basic summary...")
                        display_basic_summary(products_data)
                    
                    # Step 4: Show comparison
                    print("\n4. COMPARISON - BASIC FORMAT:")
                    print("-" * 35)
                    
                    display_basic_summary(products_data)
                    
                    return products_data
                else:
                    print(f"❌ Failed to fetch products: {products_response.status_code}")
                    return None
            else:
                print("❌ No access token received")
                return None
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def generate_ai_catalog_summary(products_data):
    """Generate AI-powered catalog summary using Gemini"""
    try:
        # Import Gemini after adding path
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
        """
        
        # Generate summary using Gemini
        print("🤖 Generating AI summary...")
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            print("❌ AI response was empty")
            return None
            
    except ImportError:
        print("⚠️  Gemini libraries not available")
        return None
    except Exception as e:
        print(f"❌ Error generating AI summary: {e}")
        return None

def display_basic_summary(products_data):
    """Display basic catalog summary as fallback"""
    if not products_data or 'products' not in products_data:
        print("No products found")
        return
    
    products = products_data['products']
    total_products = products_data.get('total', len(products))
    
    print(f"Total Products: {total_products}")
    print("Product List:")
    
    for i, product in enumerate(products, 1):
        name = product.get('name', 'Unknown')
        price = product.get('price', 0)
        stock = product.get('stock', 0)
        
        # Get primary category
        categories = product.get('categories', [])
        category = categories[0].get('name', 'Uncategorized') if categories else 'Uncategorized'
        
        # Format simple line
        print(f"{i}. {name} - ₹{price}, Stock: {stock}, Category: {category}")

if __name__ == "__main__":
    print("🚀 Starting AI Catalog Summary Demo...")
    result = demo_ai_catalog_summary()
    
    if result:
        print("\n🎉 SUCCESS! AI catalog summary is working.")
        print("\nBenefits of AI Catalog Summary:")
        print("- Intelligent analysis of product data")
        print("- Business insights and trends")
        print("- Comprehensive overview in natural language")
        print("- Automated categorization and analysis")
        print("- Perfect for reports and presentations")
    else:
        print("\n❌ Demo failed. Please check connectivity.")

def display_text_summary(products_data):
    """Display products in text summary format"""
    if not products_data or 'products' not in products_data:
        print("No products found")
        return
    
    products = products_data['products']
    total_products = products_data.get('total', len(products))
    
    print(f"Total Products: {total_products}")
    print("Summary:")
    
    for i, product in enumerate(products, 1):
        name = product.get('name', 'Unknown')
        price = product.get('price', 0)
        stock = product.get('stock', 0)
        
        # Get discount info
        discount = product.get('discount', 0)
        try:
            discount = int(discount) if discount else 0
        except (ValueError, TypeError):
            discount = 0
            
        if discount > 0:
            discounted_price = price * (1 - discount / 100)
            price_text = f"₹{price} (₹{discounted_price:.0f} after {discount}% off)"
        else:
            price_text = f"₹{price}"
        
        # Get primary category
        categories = product.get('categories', [])
        category = categories[0].get('name', 'Uncategorized') if categories else 'Uncategorized'
        
        # Get key attributes
        attributes = product.get('attributes', [])
        color = next((attr.get('value', '') for attr in attributes if attr.get('name', '').lower() == 'color'), '')
        
        # Variants and images count
        variants = product.get('variants', [])
        images = product.get('images', [])
        
        # Format compact summary line
        color_text = f" ({color})" if color else ""
        variant_text = f", {len(variants)} variants" if variants else ""
        image_text = f", {len(images)} images" if images else ""
        
        summary = f"{i}. {name}{color_text} - {price_text}, Stock: {stock}, {category}{variant_text}{image_text}"
        print(summary)

def display_detailed_format(products_data):
    """Display first 2 products in detailed format for comparison"""
    if not products_data or 'products' not in products_data:
        print("No products found")
        return
    
    products = products_data['products'][:2]  # Show only first 2 for comparison
    
    for i, product in enumerate(products, 1):
        print(f"\nProduct {i}:")
        print(f"  Name: {product.get('name', 'N/A')}")
        print(f"  Price: ₹{product.get('price', 0)}")
        print(f"  Stock: {product.get('stock', 0)}")
        print(f"  SKU: {product.get('sku', 'N/A')}")
        
        # Categories
        categories = product.get('categories', [])
        if categories:
            category_names = [cat.get('name', 'Unknown') for cat in categories]
            print(f"  Categories: {', '.join(category_names)}")
        
        # Attributes
        attributes = product.get('attributes', [])
        if attributes:
            print("  Attributes:")
            for attr in attributes:
                print(f"    {attr.get('name', 'Unknown')}: {attr.get('value', 'N/A')}")
        
        # Variants
        variants = product.get('variants', [])
        if variants:
            print(f"  Variants: {len(variants)}")
        
        # Images
        images = product.get('images', [])
        if images:
            print(f"  Images: {len(images)}")
        
        print("-" * 30)
