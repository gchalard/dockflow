"""
Docker Service for DockFlow POC
"""

import subprocess
import json
import os
from typing import Dict, List, Any

class DockerService:
    """Service for Docker operations"""
    
    def __init__(self):
        self.docker_host = os.getenv('DOCKER_HOST', 'unix:///var/run/docker.sock')
    
    def deploy_compose(self, compose_file: str, app_name: str) -> Dict[str, Any]:
        """Deploy application using Docker Compose"""
        try:
            # Run docker compose up
            result = subprocess.run(
                ['docker', 'compose', '-f', compose_file, 'up', '-d'],
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                'success': True,
                'message': f'Application {app_name} deployed successfully',
                'output': result.stdout
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'message': f'Failed to deploy {app_name}: {e.stderr}',
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Unexpected error deploying {app_name}: {str(e)}',
                'error': str(e)
            }
    
    def deploy_container(self, container_name: str, image: str) -> Dict[str, Any]:
        """Deploy a simple container"""
        try:
            # Stop and remove existing container
            subprocess.run(
                ['docker', 'stop', container_name],
                capture_output=True,
                text=True
            )
            subprocess.run(
                ['docker', 'rm', container_name],
                capture_output=True,
                text=True
            )
            
            # Run new container
            result = subprocess.run(
                [
                    'docker', 'run', '-d',
                    '--name', container_name,
                    '-p', '8080:80',
                    image
                ],
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                'success': True,
                'message': f'Container {container_name} deployed successfully',
                'container_id': result.stdout.strip()
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'message': f'Failed to deploy container {container_name}: {e.stderr}',
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Unexpected error deploying container {container_name}: {str(e)}',
                'error': str(e)
            }
    
    def get_container_status(self, app_name: str) -> List[Dict[str, Any]]:
        """Get container status for an application"""
        try:
            # Get containers by name pattern
            result = subprocess.run(
                [
                    'docker', 'ps', '-a',
                    '--filter', f'name={app_name}',
                    '--format', 'json'
                ],
                capture_output=True,
                text=True,
                check=True
            )
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    container_info = json.loads(line)
                    containers.append({
                        'id': container_info.get('ID', ''),
                        'name': container_info.get('Names', ''),
                        'status': container_info.get('Status', ''),
                        'ports': container_info.get('Ports', ''),
                        'image': container_info.get('Image', '')
                    })
            
            return containers
            
        except subprocess.CalledProcessError as e:
            return [{'error': f'Failed to get container status: {e.stderr}'}]
        except Exception as e:
            return [{'error': f'Unexpected error getting container status: {str(e)}'}]
    
    def stop_container(self, container_name: str) -> Dict[str, Any]:
        """Stop a container"""
        try:
            result = subprocess.run(
                ['docker', 'stop', container_name],
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                'success': True,
                'message': f'Container {container_name} stopped successfully'
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'message': f'Failed to stop container {container_name}: {e.stderr}'
            }
    
    def remove_container(self, container_name: str) -> Dict[str, Any]:
        """Remove a container"""
        try:
            result = subprocess.run(
                ['docker', 'rm', container_name],
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                'success': True,
                'message': f'Container {container_name} removed successfully'
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'message': f'Failed to remove container {container_name}: {e.stderr}'
            } 