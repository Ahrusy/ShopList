import requests
import json
from bs4 import BeautifulSoup

def test_favorites_functionality():
    # Start a session
    session = requests.Session()
    
    print("Testing favorites functionality...")
    
    # Get the login page to extract CSRF token
    response = session.get('http://127.0.0.1:8000/ru/auth/login/')
    print(f"Login page status: {response.status_code}")
    
    if response.status_code != 200:
        print("Failed to access login page")
        return
    
    # Parse the CSRF token from the login page
    soup = BeautifulSoup(response.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if csrf_token:
        csrf_token = csrf_token['value']
        print(f"CSRF token extracted: {csrf_token}")
    else:
        print("Could not find CSRF token")
        return
    
    # Login with test user
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
    print(f"Login response status: {response.status_code}")
    print(f"Login response URL: {response.url}")
    
    # Check if login was successful
    if response.status_code == 200 or response.url == 'http://127.0.0.1:8000/':
        print("Login successful!")
    else:
        print("Login failed!")
        return
    
    # Get a new CSRF token after login
    response = session.get('http://127.0.0.1:8000/')
    soup = BeautifulSoup(response.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if csrf_token:
        csrf_token = csrf_token['value']
        print(f"New CSRF token after login: {csrf_token}")
    else:
        print("Could not find CSRF token after login")
        return
    
    # Try to add a product to favorites
    # Let's use product ID 1 for testing
    product_id = 1
    
    # Add to favorites
    headers['X-CSRFToken'] = csrf_token
    response = session.post(
        f'http://127.0.0.1:8000/ru/favorites/add/{product_id}/',
        headers=headers,
        json={}
    )
    print(f"Add to favorites status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"Add to favorites result: {result}")
        except:
            print("Response content:", response.text[:200])
    else:
        print("Response content:", response.text[:200])
    
    # Check favorite status
    response = session.get(f'http://127.0.0.1:8000/ru/favorites/check/{product_id}/')
    print(f"Check favorite status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"Favorite status: {result}")
        except:
            print("Response content:", response.text[:200])
    else:
        print("Response content:", response.text[:200])
    
    # Remove from favorites
    response = session.post(
        f'http://127.0.0.1:8000/ru/favorites/remove/{product_id}/',
        headers=headers,
        json={}
    )
    print(f"Remove from favorites status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"Remove from favorites result: {result}")
        except:
            print("Response content:", response.text[:200])
    else:
        print("Response content:", response.text[:200])

if __name__ == "__main__":
    test_favorites_functionality()