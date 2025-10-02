import requests
import json
from bs4 import BeautifulSoup

# Test the favorites functionality
def test_favorites():
    # Start a session
    session = requests.Session()
    
    # Get the login page to extract CSRF token
    response = session.get('http://127.0.0.1:8000/ru/auth/login/')
    print("Login page status:", response.status_code)
    
    # Parse the CSRF token from the login page
    soup = BeautifulSoup(response.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if csrf_token:
        csrf_token = csrf_token['value']
        print("CSRF token extracted:", csrf_token)
    else:
        print("Could not find CSRF token")
        return
    
    # Login with test user using email method
    login_data = {
        'email': 'test@example.com',
        'password': 'testpass123',
        'login_method': 'email',
        'csrfmiddlewaretoken': csrf_token
    }
    
    # Set the referer header
    headers = {
        'Referer': 'http://127.0.0.1:8000/ru/auth/login/',
        'X-CSRFToken': csrf_token
    }
    
    # Perform login
    response = session.post('http://127.0.0.1:8000/ru/auth/login/', data=login_data, headers=headers)
    print("Login response status:", response.status_code)
    print("Login response URL:", response.url)
    
    # Check if login was successful by trying to access a protected page
    response = session.get('http://127.0.0.1:8000/ru/favorites/')
    print("Favorites page status after login:", response.status_code)
    
    # Get a new CSRF token after login
    response = session.get('http://127.0.0.1:8000/')
    soup = BeautifulSoup(response.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if csrf_token:
        csrf_token = csrf_token['value']
        print("New CSRF token after login:", csrf_token)
    else:
        print("Could not find CSRF token after login")
        return
    
    # Try to add a product to favorites
    # First, let's find a valid product ID
    response = session.get('http://127.0.0.1:8000/')
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Try to find a product card with a data-product-id attribute
    product_card = soup.find('div', {'class': 'product-card'})
    if product_card:
        product_link = product_card.find('a', href=True)
        if product_link:
            # Extract product ID from the URL
            import re
            match = re.search(r'/product/(\d+)/', product_link['href'])
            if match:
                product_id = match.group(1)
                print(f"Found product ID: {product_id}")
            else:
                product_id = '1'  # Fallback to ID 1
                print("Could not extract product ID from URL, using ID 1")
        else:
            product_id = '1'  # Fallback to ID 1
            print("Could not find product link, using ID 1")
    else:
        product_id = '1'  # Fallback to ID 1
        print("Could not find product card, using ID 1")
    
    # Check favorite status
    response = session.get(f'http://127.0.0.1:8000/ru/favorites/check/{product_id}/')
    print("Check favorite status:", response.status_code)
    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("Response text:", response.text[:200])
    
    # Add to favorites
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token,
        'X-Requested-With': 'XMLHttpRequest'
    }
    response = session.post(f'http://127.0.0.1:8000/ru/favorites/add/{product_id}/', 
                           headers=headers)
    print("Add to favorites:", response.status_code)
    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("Response text:", response.text[:200])
    
    # Check favorite status again
    response = session.get(f'http://127.0.0.1:8000/ru/favorites/check/{product_id}/')
    print("Check favorite status after adding:", response.status_code)
    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("Response text:", response.text[:200])
    
    # Remove from favorites
    response = session.post(f'http://127.0.0.1:8000/ru/favorites/remove/{product_id}/',
                           headers=headers)
    print("Remove from favorites:", response.status_code)
    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("Response text:", response.text[:200])
    
    # Check favorite status one more time
    response = session.get(f'http://127.0.0.1:8000/ru/favorites/check/{product_id}/')
    print("Check favorite status after removing:", response.status_code)
    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("Response text:", response.text[:200])

if __name__ == "__main__":
    test_favorites()