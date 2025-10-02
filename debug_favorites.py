import requests
import json
from bs4 import BeautifulSoup

def debug_favorites():
    # Start a session
    session = requests.Session()
    
    print("Debugging favorites functionality...")
    
    # First, let's check if we can access the main page
    response = session.get('http://127.0.0.1:8000/')
    print(f"Main page status: {response.status_code}")
    
    # Check if user is authenticated by looking for profile links
    soup = BeautifulSoup(response.content, 'html.parser')
    profile_link = soup.find('a', href=lambda x: x and 'profile' in x) if soup.find('a') else None
    print(f"Profile link found: {profile_link is not None}")
    
    # Try to check favorite status for product ID 1
    response = session.get('http://127.0.0.1:8000/ru/favorites/check/1/')
    print(f"Check favorite status for product 1: {response.status_code}")
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"Favorite status result: {result}")
        except:
            print("Response content:", response.text[:200])
    else:
        print("Response headers:", dict(response.headers))
        print("Response content:", response.text[:200])
    
    # Try to add to favorites
    # First get CSRF token
    csrf_token = response.cookies.get('csrftoken', '')
    print(f"CSRF token: {csrf_token}")
    
    response = session.post(
        'http://127.0.0.1:8000/ru/favorites/add/1/',
        headers={
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json'
        },
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
        print("Response headers:", dict(response.headers))
        print("Response content:", response.text[:200])

if __name__ == "__main__":
    debug_favorites()