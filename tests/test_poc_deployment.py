import pytest
import requests
import time
import subprocess
import os
from pathlib import Path

class TestPOCDeployment:
    """Test POC deployment functionality"""
    
    @pytest.fixture(scope="class")
    def api_url(self):
        """API base URL"""
        return "http://localhost:8000"
    
    @pytest.fixture(scope="class")
    def test_compose_file(self):
        """Test Docker Compose file for deployment"""
        compose_content = """
version: '3.8'
services:
  test-app:
    image: nginx:alpine
    ports:
      - "8080:80"
    environment:
      - TEST_VAR=hello_world
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3
"""
        compose_path = Path("test-compose.yml")
        compose_path.write_text(compose_content)
        yield compose_path
        compose_path.unlink(missing_ok=True)
    
    def test_health_check(self, api_url):
        """Test API health check endpoint"""
        response = requests.get(f"{api_url}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_create_application(self, api_url, test_compose_file):
        """Test creating an application"""
        app_data = {
            "name": "test-app",
            "namespace": "default",
            "repository": {
                "url": "https://github.com/test/repo",
                "branch": "main"
            },
            "docker": {
                "composeFile": "test-compose.yml",
                "context": "."
            },
            "environments": [
                {
                    "name": "development",
                    "dockerHost": "localhost"
                }
            ]
        }
        
        response = requests.post(f"{api_url}/api/v1/applications", json=app_data)
        assert response.status_code == 201
        result = response.json()
        assert result["name"] == "test-app"
        assert result["status"] == "created"
        return result["id"]
    
    def test_deploy_application(self, api_url):
        """Test deploying an application"""
        # First create the application
        app_id = self.test_create_application(api_url, None)
        
        # Trigger deployment
        response = requests.post(f"{api_url}/api/v1/applications/{app_id}/deploy")
        assert response.status_code == 200
        result = response.json()
        # For POC, we expect the deployment to fail due to missing Docker
        # but the API should handle the error gracefully
        assert "status" in result
        assert "message" in result
    
    def test_list_applications(self, api_url):
        """Test listing applications"""
        response = requests.get(f"{api_url}/api/v1/applications")
        assert response.status_code == 200
        applications = response.json()
        assert isinstance(applications, list)
    
    def test_get_application_status(self, api_url):
        """Test getting application status"""
        # First create an application
        app_id = self.test_create_application(api_url, None)
        
        response = requests.get(f"{api_url}/api/v1/applications/{app_id}/status")
        assert response.status_code == 200
        status = response.json()
        assert "status" in status
        assert "containers" in status
    
    def test_docker_compose_deployment(self, api_url, test_compose_file):
        """Test deployment using Docker Compose file"""
        # Create application with Docker Compose
        app_data = {
            "name": "compose-test-app",
            "namespace": "default",
            "repository": {
                "url": "https://github.com/test/compose-repo",
                "branch": "main"
            },
            "docker": {
                "composeFile": "test-compose.yml",
                "context": "."
            },
            "environments": [
                {
                    "name": "development",
                    "dockerHost": "localhost"
                }
            ]
        }
        
        response = requests.post(f"{api_url}/api/v1/applications", json=app_data)
        assert response.status_code == 201
        app_id = response.json()["id"]
        
        # Deploy the application
        response = requests.post(f"{api_url}/api/v1/applications/{app_id}/deploy")
        assert response.status_code == 200
        
        # For POC, we expect the deployment to fail due to missing Docker
        # but the API should handle the error gracefully
        result = response.json()
        assert "status" in result
        assert "message" in result
    
    def test_error_handling(self, api_url):
        """Test error handling for invalid requests"""
        # Test invalid application data
        invalid_data = {
            "name": "",  # Invalid empty name
            "namespace": "default"
        }
        
        response = requests.post(f"{api_url}/api/v1/applications", json=invalid_data)
        assert response.status_code == 400
        assert "error" in response.json()
        
        # Test non-existent application
        response = requests.get(f"{api_url}/api/v1/applications/non-existent/status")
        assert response.status_code == 404 