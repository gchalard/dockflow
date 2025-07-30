"""
Applications Controller for DockFlow POC
"""

from flask import Blueprint, request, jsonify
from app.models.application import Application
from app.services.docker_service import DockerService
from app import db
import subprocess
import os

bp = Blueprint('applications', __name__)
docker_service = DockerService()

@bp.route('/applications', methods=['GET'])
def list_applications():
    """List all applications"""
    applications = Application.query.all()
    return jsonify([app.to_dict() for app in applications])

@bp.route('/applications', methods=['POST'])
def create_application():
    """Create a new application"""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('name'):
        return jsonify({"error": "Application name is required"}), 400
    
    # Create application
    app = Application(
        name=data['name'],
        namespace=data.get('namespace', 'default'),
        repository_url=data.get('repository', {}).get('url'),
        repository_branch=data.get('repository', {}).get('branch', 'main'),
        compose_file=data.get('docker', {}).get('composeFile'),
        context=data.get('docker', {}).get('context', '.'),
        docker_host=data.get('environments', [{}])[0].get('dockerHost', 'localhost')
    )
    
    db.session.add(app)
    db.session.commit()
    
    return jsonify(app.to_dict()), 201

@bp.route('/applications/<app_id>', methods=['GET'])
def get_application(app_id):
    """Get application by ID"""
    app = Application.query.get(app_id)
    if not app:
        return jsonify({"error": "Application not found"}), 404
    
    return jsonify(app.to_dict())

@bp.route('/applications/<app_id>/deploy', methods=['POST'])
def deploy_application(app_id):
    """Deploy an application"""
    app = Application.query.get(app_id)
    if not app:
        return jsonify({"error": "Application not found"}), 404
    
    try:
        # Update status to deploying
        app.status = 'deploying'
        db.session.commit()
        
        # Deploy using Docker Compose if compose file exists
        if app.compose_file and os.path.exists(app.compose_file):
            result = docker_service.deploy_compose(app.compose_file, app.name)
            if result['success']:
                app.status = 'running'
            else:
                app.status = 'failed'
        else:
            # Simple container deployment
            result = docker_service.deploy_container(app.name, 'nginx:alpine')
            if result['success']:
                app.status = 'running'
            else:
                app.status = 'failed'
        
        db.session.commit()
        
        return jsonify({
            "id": app.id,
            "status": app.status,
            "message": result.get('message', 'Deployment completed')
        })
        
    except Exception as e:
        app.status = 'failed'
        db.session.commit()
        return jsonify({"error": str(e)}), 500

@bp.route('/applications/<app_id>/status', methods=['GET'])
def get_application_status(app_id):
    """Get application deployment status"""
    app = Application.query.get(app_id)
    if not app:
        return jsonify({"error": "Application not found"}), 404
    
    try:
        # Get container status from Docker
        containers = docker_service.get_container_status(app.name)
        
        return jsonify({
            "id": app.id,
            "name": app.name,
            "status": app.status,
            "containers": containers
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 