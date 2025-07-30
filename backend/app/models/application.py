"""
Application Model for DockFlow POC
"""

from app import db
from datetime import datetime
import uuid

class Application(db.Model):
    """Application model for managing Docker applications"""
    
    __tablename__ = 'applications'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    namespace = db.Column(db.String(255), nullable=False, default='default')
    repository_url = db.Column(db.String(500))
    repository_branch = db.Column(db.String(255), default='main')
    compose_file = db.Column(db.String(500))
    context = db.Column(db.String(500), default='.')
    docker_host = db.Column(db.String(255), default='localhost')
    status = db.Column(db.String(50), default='created')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Application {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'namespace': self.namespace,
            'repository': {
                'url': self.repository_url,
                'branch': self.repository_branch
            },
            'docker': {
                'composeFile': self.compose_file,
                'context': self.context
            },
            'environments': [
                {
                    'name': 'development',
                    'dockerHost': self.docker_host
                }
            ],
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 