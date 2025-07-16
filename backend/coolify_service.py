import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from models import db, CoolifyConfig, Deployment, DeploymentStatus
import re
from urllib.parse import urlparse

class CoolifyService:
    
    def __init__(self, config_id: int):
        self.config = CoolifyConfig.query.get(config_id)
        if not self.config:
            raise ValueError(f"Coolify config with ID {config_id} not found")
        
        self.api_url = self.config.api_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {self.config.api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def detect_project_type(self, github_url: str) -> Tuple[str, Dict]:
        """Detect project type from GitHub repository"""
        try:
            parsed = urlparse(github_url)
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) < 2:
                return 'unknown', {}
            
            owner, repo = path_parts[0], path_parts[1]
            
            files_to_check = [
                'package.json',
                'requirements.txt', 
                'pyproject.toml',
                'Dockerfile',
                'docker-compose.yml',
                'pom.xml',
                'go.mod'
            ]
            
            detected_files = []
            for file in files_to_check:
                url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file}"
                response = requests.get(url)
                if response.status_code == 200:
                    detected_files.append(file)
            
            if 'Dockerfile' in detected_files:
                return 'docker', {'detected_files': detected_files}
            elif 'package.json' in detected_files:
                return 'nodejs', {'detected_files': detected_files}
            elif any(f in detected_files for f in ['requirements.txt', 'pyproject.toml']):
                return 'python', {'detected_files': detected_files}
            elif 'docker-compose.yml' in detected_files:
                return 'docker-compose', {'detected_files': detected_files}
            elif 'pom.xml' in detected_files:
                return 'java', {'detected_files': detected_files}
            elif 'go.mod' in detected_files:
                return 'go', {'detected_files': detected_files}
            else:
                return 'static', {'detected_files': detected_files}
                
        except Exception as e:
            print(f"Error detecting project type: {str(e)}")
            return 'unknown', {'error': str(e)}
    
    def create_application(self, deployment: Deployment) -> bool:
        """Create application in Coolify"""
        try:
            project_type, detection_info = self.detect_project_type(deployment.github_url)
            deployment.project_type = project_type
            
            app_data = {
                'name': deployment.name,
                'git_repository': deployment.github_url,
                'git_branch': 'main',
                'build_pack': self._get_build_pack(project_type),
                'ports_exposes': self._get_default_port(project_type),
                'environment_variables': json.loads(deployment.environment_variables) if deployment.environment_variables else {}
            }
            
            response = requests.post(
                f"{self.api_url}/api/v1/applications",
                headers=self.headers,
                json=app_data
            )
            
            if response.status_code in [200, 201]:
                app_data = response.json()
                deployment.coolify_app_id = app_data.get('uuid', app_data.get('id'))
                deployment.status = DeploymentStatus.BUILDING
                db.session.commit()
                return True
            else:
                print(f"Failed to create application: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error creating application: {str(e)}")
            deployment.status = DeploymentStatus.FAILED
            db.session.commit()
            return False
    
    def deploy_application(self, deployment: Deployment) -> bool:
        """Deploy application in Coolify"""
        try:
            if not deployment.coolify_app_id:
                return False
            
            response = requests.post(
                f"{self.api_url}/api/v1/applications/{deployment.coolify_app_id}/deploy",
                headers=self.headers
            )
            
            if response.status_code in [200, 201]:
                deployment.status = DeploymentStatus.DEPLOYING
                db.session.commit()
                return True
            else:
                print(f"Failed to deploy application: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error deploying application: {str(e)}")
            return False
    
    def get_deployment_status(self, deployment: Deployment) -> Dict:
        """Get deployment status from Coolify"""
        try:
            if not deployment.coolify_app_id:
                return {'status': 'unknown'}
            
            response = requests.get(
                f"{self.api_url}/api/v1/applications/{deployment.coolify_app_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                app_data = response.json()
                status = app_data.get('status', 'unknown')
                
                status_mapping = {
                    'running': DeploymentStatus.RUNNING,
                    'building': DeploymentStatus.BUILDING,
                    'deploying': DeploymentStatus.DEPLOYING,
                    'stopped': DeploymentStatus.STOPPED,
                    'failed': DeploymentStatus.FAILED
                }
                
                deployment.status = status_mapping.get(status, DeploymentStatus.PENDING)
                deployment.deployment_url = app_data.get('fqdn', app_data.get('url'))
                db.session.commit()
                
                return {
                    'status': deployment.status.value,
                    'url': deployment.deployment_url,
                    'logs': app_data.get('logs', '')
                }
            else:
                return {'status': 'error', 'message': 'Failed to fetch status'}
                
        except Exception as e:
            print(f"Error getting deployment status: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def update_environment_variables(self, deployment: Deployment, env_vars: Dict) -> bool:
        """Update environment variables for deployment"""
        try:
            if not deployment.coolify_app_id:
                return False
            
            response = requests.put(
                f"{self.api_url}/api/v1/applications/{deployment.coolify_app_id}/environment-variables",
                headers=self.headers,
                json=env_vars
            )
            
            if response.status_code in [200, 201]:
                deployment.environment_variables = json.dumps(env_vars)
                db.session.commit()
                return True
            else:
                print(f"Failed to update environment variables: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error updating environment variables: {str(e)}")
            return False
    
    def _get_build_pack(self, project_type: str) -> str:
        """Get appropriate build pack for project type"""
        build_packs = {
            'nodejs': 'nodejs',
            'python': 'python',
            'docker': 'dockerfile',
            'docker-compose': 'docker-compose',
            'static': 'static',
            'java': 'java',
            'go': 'go'
        }
        return build_packs.get(project_type, 'static')
    
    def _get_default_port(self, project_type: str) -> str:
        """Get default port for project type"""
        default_ports = {
            'nodejs': '3000',
            'python': '8001',
            'java': '8080',
            'go': '8080',
            'static': '80'
        }
        return default_ports.get(project_type, '3000')
