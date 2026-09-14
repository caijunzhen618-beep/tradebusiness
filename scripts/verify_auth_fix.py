#!/usr/bin/env python3
"""
Authorization Fix Verification Script
Tests the complete authentication flow after configuration fixes
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Colors for terminal output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_section(title: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def test_backend_health() -> bool:
    """Test if backend is running"""
    print_section("1. Testing Backend Health")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success(f"Backend is running: {BASE_URL}")
            print_info(f"Response: {response.json()}")
            return True
        else:
            print_error(f"Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend - is it running?")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_login_api() -> Dict[str, Any]:
    """Test login API and return token"""
    print_section("2. Testing Login API")

    login_data = {
        "username": "admin",
        "password": "Admin123"
    }

    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Login successful")
            print_info(f"User: {data.get('user', {}).get('username')}")
            print_info(f"Token: {data.get('access_token', '')[:50]}...")
            return data
        else:
            print_error(f"Login failed with status {response.status_code}")
            print_info(f"Response: {response.text}")
            return {}
    except Exception as e:
        print_error(f"Login request failed: {str(e)}")
        return {}

def test_authenticated_request(token: str) -> bool:
    """Test authenticated request with Authorization header"""
    print_section("3. Testing Authenticated Request")

    if not token:
        print_error("No token provided")
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        # Test /api/v1/users/me endpoint
        response = requests.get(
            f"{API_BASE}/users/me",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Authenticated request successful")
            print_info(f"User ID: {data.get('id')}")
            print_info(f"Username: {data.get('username')}")
            print_info(f"Email: {data.get('email')}")
            return True
        else:
            print_error(f"Request failed with status {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

def test_notifications_api(token: str) -> bool:
    """Test the notifications API that was failing before"""
    print_section("4. Testing Notifications API (Previously Failing)")

    if not token:
        print_error("No token provided")
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{API_BASE}/notifications",
            headers=headers,
            params={"skip": 0, "limit": 20}
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Notifications API successful")
            print_info(f"Total: {data.get('total', 0)} notifications")
            print_info(f"Items: {len(data.get('items', []))} returned")
            return True
        else:
            print_error(f"Notifications API failed with status {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Notifications API request failed: {str(e)}")
        return False

def test_customers_api(token: str) -> bool:
    """Test the customers API"""
    print_section("5. Testing Customers API")

    if not token:
        print_error("No token provided")
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{API_BASE}/customers",
            headers=headers,
            params={"skip": 0, "limit": 20}
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Customers API successful")
            print_info(f"Total: {data.get('total', 0)} customers")
            print_info(f"Items: {len(data.get('items', []))} returned")
            return True
        else:
            print_error(f"Customers API failed with status {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Customers API request failed: {str(e)}")
        return False

def check_environment_configs():
    """Check frontend environment configurations"""
    print_section("6. Checking Frontend Configurations")

    configs = [
        {
            "name": "Admin Frontend",
            "path": "tradebusiness-admin/.env.development"
        },
        {
            "name": "Client Frontend",
            "path": "tradebusiness-client/.env.development"
        }
    ]

    all_correct = True
    for config in configs:
        try:
            with open(config["path"], "r") as f:
                content = f.read()
                if "VITE_APP_BASE_API=http://localhost:8000" in content:
                    print_success(f"{config['name']}: baseURL is correct")
                else:
                    print_error(f"{config['name']}: baseURL is incorrect")
                    all_correct = False

                if "/api/v1" not in content.split("VITE_APP_BASE_API=")[1].split("\n")[0]:
                    print_success(f"{config['name']}: No duplicate /api/v1 path")
                else:
                    print_error(f"{config['name']}: baseURL contains /api/v1 (should not)")
                    all_correct = False
        except FileNotFoundError:
            print_error(f"{config['name']}: Config file not found")
            all_correct = False

    return all_correct

def main():
    """Run all verification tests"""
    print(f"\n{Colors.BOLD}")
    print("="*60)
    print("AUTHORIZATION FIX VERIFICATION".center(60))
    print("="*60)
    print(f"{Colors.END}\n")

    # Run tests
    backend_ok = test_backend_health()
    if not backend_ok:
        print_section("❌ VERIFICATION FAILED")
        print_error("Backend is not running. Please start the backend first:")
        print("  cd tradebusiness-backend")
        print("  venv\\Scripts\\activate")
        print("  python -m uvicorn app.main:app --reload")
        return

    login_result = test_login_api()
    if not login_result:
        print_section("❌ VERIFICATION FAILED")
        print_error("Login failed. Please check your credentials.")
        return

    token = login_result.get("access_token")
    auth_ok = test_authenticated_request(token)
    notifications_ok = test_notifications_api(token)
    customers_ok = test_customers_api(token)
    configs_ok = check_environment_configs()

    # Summary
    print_section("VERIFICATION SUMMARY")
    results = {
        "Backend Health": backend_ok,
        "Login API": bool(login_result),
        "Authenticated Request": auth_ok,
        "Notifications API": notifications_ok,
        "Customers API": customers_ok,
        "Frontend Configs": configs_ok
    }

    all_passed = True
    for test_name, passed in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if passed else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.END}")
        print()
        print(f"{Colors.BOLD}Next Steps:{Colors.END}")
        print("  1. Restart your frontend development servers:")
        print("     - Admin: cd tradebusiness-admin && npm run dev")
        print("     - Client: cd tradebusiness-client && npm run dev")
        print("  2. Clear browser cache (Ctrl+Shift+R)")
        print("  3. Login and test all menu items")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.END}")
        print()
        print("Please fix the issues above before restarting frontends.")

    print()

if __name__ == "__main__":
    main()
