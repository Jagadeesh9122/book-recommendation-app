#!/usr/bin/env python3
"""
Test script for the Book Recommendation System Backend
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_api():
    """Test the API endpoints"""
    print("🧪 Testing Book Recommendation System API")
    print("=" * 50)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    try:
        # Test root endpoint
        print("1. Testing root endpoint...")
        response = requests.get(f"{API_BASE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test creating a user
        print("\n2. Creating a test user...")
        user_data = {"name": "Test User"}
        response = requests.post(f"{API_BASE_URL}/users/", json=user_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            user = response.json()
            user_id = user["id"]
            print(f"   Created user: {user['name']} (ID: {user_id})")
        else:
            print(f"   Error: {response.text}")
            return
        
        # Test getting users
        print("\n3. Getting all users...")
        response = requests.get(f"{API_BASE_URL}/users/")
        print(f"   Status: {response.status_code}")
        users = response.json()
        print(f"   Found {len(users)} users")
        
        # Test adding a book
        print("\n4. Adding a test book...")
        book_data = {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "genre": "Fiction",
            "cover_url": "https://example.com/cover.jpg"
        }
        response = requests.post(f"{API_BASE_URL}/books/?user_id={user_id}", json=book_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            book = response.json()
            print(f"   Added book: {book['title']} by {book['author']}")
        else:
            print(f"   Error: {response.text}")
        
        # Test getting user books
        print("\n5. Getting user books...")
        response = requests.get(f"{API_BASE_URL}/users/{user_id}/books")
        print(f"   Status: {response.status_code}")
        books = response.json()
        print(f"   User has {len(books)} books")
        
        # Test getting user stats
        print("\n6. Getting user statistics...")
        response = requests.get(f"{API_BASE_URL}/users/{user_id}/stats")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"   Total books: {stats['total_books']}")
            print(f"   Favorite genre: {stats['favorite_genre']}")
        
        # Test getting recommendations
        print("\n7. Getting recommendations...")
        response = requests.get(f"{API_BASE_URL}/users/{user_id}/recommendations")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            recommendations = response.json()
            print(f"   Recommended genre: {recommendations['recommended_genre']}")
            print(f"   Reason: {recommendations['reason']}")
            print(f"   Suggested books: {len(recommendations['suggested_books'])}")
        
        print("\n✅ All tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_api()
