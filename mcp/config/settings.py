"""
Centralized configuration settings for the MCP backend.
Loads environment variables with production defaults.
"""
import os
from typing import List

# Environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
IS_PRODUCTION = ENVIRONMENT == 'production'

# API Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.casewisemd.org')
MCP_PORT = int(os.getenv('MCP_PORT', '8000'))

# CORS Configuration
ALLOWED_ORIGINS_STR = os.getenv(
    'ALLOWED_ORIGINS',
    'https://app.casewisemd.org,https://casewisemd.org,https://www.casewisemd.org'
)
ALLOWED_ORIGINS: List[str] = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(',')]

# OHIF Viewer Configuration
OHIF_BASE_URL = os.getenv('OHIF_BASE_URL', 'https://viewer.casewisemd.org/viewer')

# DICOMweb Configuration
DICOMWEB_ENDPOINT = os.getenv('DICOMWEB_ENDPOINT', 'https://api.casewisemd.org/orthanc/dicom-web')

# Orthanc Configuration
ORTHANC_URL = os.getenv('ORTHANC_URL', 'http://localhost:8042')
ORTHANC_PORT = int(os.getenv('ORTHANC_PORT', '8042'))

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Debug Mode
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

def get_config_summary():
    """Return a summary of the current configuration for logging purposes."""
    return {
        'environment': ENVIRONMENT,
        'api_base_url': API_BASE_URL,
        'mcp_port': MCP_PORT,
        'allowed_origins': ALLOWED_ORIGINS,
        'ohif_base_url': OHIF_BASE_URL,
        'dicomweb_endpoint': DICOMWEB_ENDPOINT,
        'orthanc_url': ORTHANC_URL,
        'orthanc_port': ORTHANC_PORT,
        'openai_configured': bool(OPENAI_API_KEY),
        'debug': DEBUG
    }