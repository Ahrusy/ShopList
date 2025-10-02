import requests
import json

def test_favorites():
    # Start a session
    session = requests.Session()
    
    # First, let's try to access the favorites page without login
    response = session.get('http://127.0.0.1:8000/ru/favorites/')
    print(f"Favorites page status (not logged in): {response.status_code}")
    
    # Try to add a product to favorites without login
    response = session.post('http://127.0.0.1:8000/ru/favorites/add/1/', 
                           headers={'X-CSRFToken': 'dummy'})
    print(f"Add to favorites status (not logged in): {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Try to check favorite status without login
    response = session.get('http://127.0.0.1:8000/ru/favorites/check/1/')
    print(f"Check favorite status (not logged in): {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_favorites()