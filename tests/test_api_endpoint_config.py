# SPDX-FileCopyrightText: 2025 GitHub
# SPDX-License-Identifier: MIT

"""
Test API endpoint configuration.
"""

import pytest
import os
from urllib.parse import urlparse
from seclab_taskflow_agent.available_tools import AvailableTools

class TestAPIEndpoint:
    """Test API endpoint configuration."""
    
    @staticmethod
    def _reload_capi_module():
        """Helper method to reload the capi module."""
        import importlib
        import seclab_taskflow_agent.capi
        importlib.reload(seclab_taskflow_agent.capi)
    
    def test_default_api_endpoint(self):
        """Test that default API endpoint is set to models.github.ai/inference."""
        from seclab_taskflow_agent.capi import AI_API_ENDPOINT, AI_API_ENDPOINT_ENUM
        # When no env var is set, it should default to models.github.ai/inference
        # Note: We can't easily test this without manipulating the environment
        # so we'll just import and verify the constant exists
        assert AI_API_ENDPOINT is not None
        assert isinstance(AI_API_ENDPOINT, str)
        assert urlparse(AI_API_ENDPOINT).netloc == AI_API_ENDPOINT_ENUM.AI_API_MODELS_GITHUB
    
    def test_api_endpoint_env_override(self):
        """Test that AI_API_ENDPOINT can be overridden by environment variable."""
        # Save original env
        original_env = os.environ.get('AI_API_ENDPOINT')
        
        try:
            # Set custom endpoint
            test_endpoint = 'https://test.example.com'
            os.environ['AI_API_ENDPOINT'] = test_endpoint
            
            # Reload the module to pick up the new env var
            self._reload_capi_module()
            
            from seclab_taskflow_agent.capi import AI_API_ENDPOINT
            assert AI_API_ENDPOINT == test_endpoint
        finally:
            # Restore original env
            if original_env is None:
                os.environ.pop('AI_API_ENDPOINT', None)
            else:
                os.environ['AI_API_ENDPOINT'] = original_env
            # Reload again to restore original state
            self._reload_capi_module()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
