#!/usr/bin/env python3
"""
Environment Configuration Manager for Booking System
Manages environment variables and configuration across all services
"""

import os
import json
import secrets
from pathlib import Path
from datetime import datetime

class ConfigManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config = {
            'development': {
                'database': {
                    'backend': 'sqlite:///booking_system.db',
                    'crm': 'sqlite:///crm.db',
                    'notification': 'sqlite:///notifications.db'
                },
                'security': {
                    'jwt_secret': 'dev-jwt-secret-key',
                    'crm_bearer_token': 'dev-static-bearer-token',
                    'backend_service_token': 'dev-backend-service-token',
                    'flask_secret': 'dev-secret-key'
                },
                'services': {
                    'backend_url': 'http://localhost:5000',
                    'crm_url': 'http://localhost:5001',
                    'notification_url': 'http://localhost:5002',
                    'frontend_url': 'http://localhost:3000'
                }
            },
            'production': {
                'database': {
                    'backend': 'postgresql://postgres:password123@db:5432/booking_system',
                    'crm': 'postgresql://postgres:password123@db:5432/crm',
                    'notification': 'postgresql://postgres:password123@db:5432/notifications'
                },
                'security': {
                    'jwt_secret': secrets.token_urlsafe(32),
                    'crm_bearer_token': secrets.token_urlsafe(32),
                    'backend_service_token': secrets.token_urlsafe(32),
                    'flask_secret': secrets.token_urlsafe(32)
                },
                'services': {
                    'backend_url': 'http://backend:5000',
                    'crm_url': 'http://crm:5001',
                    'notification_url': 'http://notification:5002',
                    'frontend_url': 'http://frontend:3000'
                }
            }
        }
    
    def generate_env_file(self, environment='development'):
        """Generate .env file for specified environment"""
        config = self.config[environment]
        
        env_content = f"""# {environment.upper()} Environment Configuration
# Generated automatically - do not edit manually

# Database Configuration
DATABASE_URL_BACKEND={config['database']['backend']}
DATABASE_URL_CRM={config['database']['crm']}
DATABASE_URL_NOTIFICATION={config['database']['notification']}

# Security Configuration
JWT_SECRET_KEY={config['security']['jwt_secret']}
CRM_BEARER_TOKEN={config['security']['crm_bearer_token']}
BACKEND_SERVICE_TOKEN={config['security']['backend_service_token']}
SECRET_KEY={config['security']['flask_secret']}

# Service URLs
CRM_SERVICE_URL={config['services']['crm_url']}
NOTIFICATION_SERVICE_URL={config['services']['notification_url']}
REACT_APP_API_URL={config['services']['backend_url']}
REACT_APP_NOTIFICATION_URL={config['services']['notification_url']}

# Flask Configuration
FLASK_ENV={environment}
FLASK_DEBUG={'1' if environment == 'development' else '0'}

# Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        env_file = self.base_dir / f'.env.{environment[:4]}'
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✅ Generated {env_file}")
        return env_file
    
    def validate_config(self):
        """Validate configuration for all environments"""
        errors = []
        
        for env_name, env_config in self.config.items():
            # Check required sections
            required_sections = ['database', 'security', 'services']
            for section in required_sections:
                if section not in env_config:
                    errors.append(f"{env_name}: Missing {section} section")
            
            # Check security tokens
            if env_name == 'production':
                security = env_config.get('security', {})
                for key, value in security.items():
                    if len(value) < 16:
                        errors.append(f"{env_name}: {key} is too short")
        
        if errors:
            print("❌ Configuration validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False
        else:
            print("✅ Configuration validation passed")
            return True
    
    def generate_docker_secrets(self):
        """Generate Docker secrets for production"""
        secrets_dir = self.base_dir / 'secrets'
        secrets_dir.mkdir(exist_ok=True)
        
        prod_config = self.config['production']
        
        secrets_data = {
            'jwt_secret': prod_config['security']['jwt_secret'],
            'crm_bearer_token': prod_config['security']['crm_bearer_token'],
            'backend_service_token': prod_config['security']['backend_service_token'],
            'flask_secret': prod_config['security']['flask_secret']
        }
        
        for name, value in secrets_data.items():
            secret_file = secrets_dir / f'{name}.txt'
            with open(secret_file, 'w') as f:
                f.write(value)
            os.chmod(secret_file, 0o600)
        
        print(f"✅ Generated Docker secrets in {secrets_dir}")
    
    def print_config_summary(self):
        """Print configuration summary"""
        print("\n📋 Configuration Summary:")
        print("=" * 50)
        
        for env_name, env_config in self.config.items():
            print(f"\n{env_name.upper()} Environment:")
            print(f"  Backend DB: {env_config['database']['backend']}")
            print(f"  CRM URL: {env_config['services']['crm_url']}")
            print(f"  Notification URL: {env_config['services']['notification_url']}")
            print(f"  Frontend URL: {env_config['services']['frontend_url']}")

def main():
    """Main configuration script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Booking System Configuration Manager')
    parser.add_argument('--env', choices=['development', 'production'], 
                       default='development', help='Environment to configure')
    parser.add_argument('--generate-secrets', action='store_true',
                       help='Generate Docker secrets')
    parser.add_argument('--validate', action='store_true',
                       help='Validate configuration')
    parser.add_argument('--summary', action='store_true',
                       help='Show configuration summary')
    
    args = parser.parse_args()
    
    config_manager = ConfigManager()
    
    if args.validate:
        config_manager.validate_config()
    
    if args.generate_secrets:
        config_manager.generate_docker_secrets()
    
    if args.summary:
        config_manager.print_config_summary()
    
    if not any([args.validate, args.generate_secrets, args.summary]):
        # Default action: generate env file
        config_manager.generate_env_file(args.env)
        print(f"✅ Configuration ready for {args.env}")

if __name__ == "__main__":
    main()
