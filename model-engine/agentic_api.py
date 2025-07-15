import requests

class AgenticAPI:
    """Handles all API-related operations: authentication, category/attribute fetching, product posting, and searching."""

    def __init__(self, base_url="https://api-ecommerce.sanjaysagar.com"):
        self.base_url = base_url

    def authenticate_user(self, email="sanjay@gmail.com", password="password"):
        """Authenticate user and get access token"""
        try:
            auth_url = f"{self.base_url}/api/auth/signin"
            auth_data = {
                "email": email,
                "password": password
            }
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }
            response = requests.post(auth_url, headers=headers, json=auth_data)
            if response.status_code in [200, 201]:
                auth_response = response.json()
                access_token = auth_response.get("access_token")
                if access_token:
                    print(f"✅ Authentication successful!")
                    return access_token
                else:
                    print(f"❌ No access token in response: {auth_response}")
                    return None
            else:
                print(f"❌ Authentication failed. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except requests.exceptions.ConnectionError:
            print("❌ Failed to connect to authentication API. Make sure the server is running")
            return None
        except Exception as e:
            print(f"❌ Error during authentication: {e}")
            return None

    def send_product_to_api(self, product_json, access_token):
        """Send the generated product JSON to the API endpoint with authentication"""
        api_url = f"{self.base_url}/api/seller-product"
        try:
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.post(api_url, headers=headers, json=product_json)
            if response.status_code in [200, 201]:
                print(f"✅ Product successfully added to catalog!")
                try:
                    response_data = response.json()
                    if 'id' in response_data:
                        print(f"Product ID: {response_data['id']}")
                    return True
                except:
                    return True
            else:
                print(f"❌ Failed to add product. Status: {response.status_code}")
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        print(f"Error: {error_data['message']}")
                except:
                    print(f"Response: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Failed to connect to API. Make sure the server is running on {self.base_url}")
            return False
        except Exception as e:
            print(f"❌ Error sending product to API: {e}")
            return False

    def get_available_categories(self, access_token):
        """Fetch available categories from the API"""
        try:
            headers = {
                'accept': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.get(f"{self.base_url}/api/categories", headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get('categories', [])
            else:
                print(f"❌ Failed to fetch categories. Status: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error fetching categories: {e}")
            return []

    def get_available_attributes(self, access_token):
        """Fetch available attributes from the API"""
        try:
            headers = {
                'accept': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.get(f"{self.base_url}/api/attributes", headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get('attributes', [])
            else:
                print(f"❌ Failed to fetch attributes. Status: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error fetching attributes: {e}")
            return []

    def search_products(self, search_url, access_token):
        """Perform the actual GET request for product search"""
        try:
            headers = {
                'accept': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.get(search_url, headers=headers)
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Found products!")
                return results
            else:
                print(f"❌ Search failed. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error during search: {e}")
            return None