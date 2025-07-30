#!/usr/bin/env python3
"""
Test Runner for DockFlow POC
"""

import subprocess
import time
import requests
import sys
import os
from pathlib import Path

def wait_for_api(url, max_wait=120):
    """Wait for API to be ready"""
    print(f"Waiting for API at {url}...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)
    
    print("❌ API failed to start within timeout")
    return False

def run_docker_compose():
    """Start the test environment with Docker Compose"""
    print("🚀 Starting test environment...")
    
    try:
        # Start services
        subprocess.run(
            ["docker", "compose", "-f", "docker-compose.test.yml", "up", "-d"],
            check=True
        )
        print("✅ Test environment started")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start test environment: {e}")
        return False

def stop_docker_compose():
    """Stop the test environment"""
    print("🛑 Stopping test environment...")
    
    try:
        subprocess.run(
            ["docker", "compose", "-f", "docker-compose.test.yml", "down"],
            check=True
        )
        print("✅ Test environment stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to stop test environment: {e}")

def run_pytest():
    """Run pytest tests"""
    print("🧪 Running tests...")
    
    try:
        result = subprocess.run(
            ["pytest", "tests/test_poc_deployment.py", "-v", "--tb=short"],
            check=True
        )
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        return False

def main():
    """Main test runner"""
    api_url = "http://localhost:8000"
    
    print("=" * 50)
    print("🧪 DockFlow POC Test Runner")
    print("=" * 50)
    
    # Start test environment
    if not run_docker_compose():
        sys.exit(1)
    
    # Wait for API
    if not wait_for_api(api_url):
        stop_docker_compose()
        sys.exit(1)
    
    # Run tests
    success = run_pytest()
    
    # Cleanup
    # stop_docker_compose()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 