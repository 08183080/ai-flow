#!/usr/bin/env python3
import requests
import socket
import time

# Test different approaches to access GitHub

def test_github_access():
    print("Testing GitHub access...")
    
    # Test 1: Basic GET to github.com
    try:
        print("Test 1: Basic GET to github.com")
        r = requests.get('https://github.com', timeout=30)
        print(f"  Status: {r.status_code}")
        print(f"  Success: {r.status_code == 200}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test 2: GET to trending/python with simple headers
    try:
        print("\nTest 2: GET to trending/python with simple headers")
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get('https://github.com/trending/python', headers=headers, timeout=45)
        print(f"  Status: {r.status_code}")
        print(f"  Success: {r.status_code == 200}")
        if r.status_code == 200:
            print(f"  Content length: {len(r.text)} chars")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test 3: GET to api.github.com
    try:
        print("\nTest 3: GET to api.github.com")
        r = requests.get('https://api.github.com', timeout=30)
        print(f"  Status: {r.status_code}")
        print(f"  Success: {r.status_code == 200}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test 4: Direct socket test
    print("\nTest 4: Direct socket connection to github.com:443")
    try:
        sock = socket.create_connection(('github.com', 443), timeout=30)
        print(f"  Socket connection successful")
        sock.close()
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == '__main__':
    test_github_access()