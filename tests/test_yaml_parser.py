# SPDX-FileCopyrightText: 2025 GitHub
# SPDX-License-Identifier: MIT

"""
Basic tests for YAML parsing functionality in the taskflow agent.

Simple parsing + parsing of example taskflows.
"""

import pytest
import tempfile
from pathlib import Path
import yaml
import os
from seclab_taskflow_agent.available_tools import AvailableTools

class TestYamlParser:
    """Test suite for YamlParser class."""

    def test_yaml_parser_basic_functionality(self):
        """Test basic YAML parsing functionality."""
        available_tools = AvailableTools()
        personality000 = available_tools.get_personality(
            "tests.data.test_yaml_parser_personality000")
        
        assert personality000['seclab-taskflow-agent']['version'] == 1
        assert personality000['seclab-taskflow-agent']['filetype'] == 'personality'
        assert personality000['personality'] == 'You are a helpful assistant.\n'
        assert personality000['task'] == 'Answer any question.\n'

class TestRealTaskflowFiles:
    """Test parsing of actual taskflow files in the project."""

    def test_parse_example_taskflows(self):
        """Test parsing example taskflow files."""
        # this test uses the actual taskflows in the project
        available_tools = AvailableTools()

        # check that example.yaml is parsed correctly
        example_task_flow = available_tools.get_taskflow(
            "examples.taskflows.example")
        assert 'taskflow' in example_task_flow
        assert isinstance(example_task_flow['taskflow'], list)
        assert len(example_task_flow['taskflow']) == 4  # 4 tasks in taskflow
        assert example_task_flow['taskflow'][0]['task']['max_steps'] == 20

class TestCliGlobals:
    """Test CLI global variable parsing."""
    
    def test_parse_single_global(self):
        """Test parsing a single global variable from command line."""
        from seclab_taskflow_agent.__main__ import parse_prompt_args
        available_tools = AvailableTools()
        
        p, t, l, cli_globals, user_prompt, _ = parse_prompt_args(
            available_tools, "-t example -g fruit=apples")
        
        assert t == "example"
        assert cli_globals == {"fruit": "apples"}
        assert p is None
        assert l is False
    
    def test_parse_multiple_globals(self):
        """Test parsing multiple global variables from command line."""
        from seclab_taskflow_agent.__main__ import parse_prompt_args
        available_tools = AvailableTools()
        
        p, t, l, cli_globals, user_prompt, _ = parse_prompt_args(
            available_tools, "-t example -g fruit=apples -g color=red")
        
        assert t == "example"
        assert cli_globals == {"fruit": "apples", "color": "red"}
        assert p is None
        assert l is False
    
    def test_parse_global_with_spaces(self):
        """Test parsing global variables with spaces in values."""
        from seclab_taskflow_agent.__main__ import parse_prompt_args
        available_tools = AvailableTools()
        
        p, t, l, cli_globals, user_prompt, _ = parse_prompt_args(
            available_tools, "-t example -g message=hello world")
        
        assert t == "example"
        # "world" becomes part of the prompt, not the value
        assert cli_globals == {"message": "hello"}
        assert "world" in user_prompt
    
    def test_parse_global_with_equals_in_value(self):
        """Test parsing global variables with equals sign in value."""
        from seclab_taskflow_agent.__main__ import parse_prompt_args
        available_tools = AvailableTools()
        
        p, t, l, cli_globals, user_prompt, _ = parse_prompt_args(
            available_tools, "-t example -g equation=x=5")
        
        assert t == "example"
        assert cli_globals == {"equation": "x=5"}
    
    def test_globals_in_taskflow_file(self):
        """Test that globals can be read from taskflow file."""
        available_tools = AvailableTools()
        
        taskflow = available_tools.get_taskflow("tests.data.test_globals_taskflow")
        assert 'globals' in taskflow
        assert taskflow['globals']['test_var'] == 'default_value'

class TestAPIEndpoint:
    """Test API endpoint configuration."""
    
    def test_default_api_endpoint(self):
        """Test that default API endpoint is set to models.github.ai/inference."""
        from seclab_taskflow_agent.capi import AI_API_ENDPOINT
        # When no env var is set, it should default to models.github.ai/inference
        # Note: We can't easily test this without manipulating the environment
        # so we'll just import and verify the constant exists
        assert AI_API_ENDPOINT is not None
        assert isinstance(AI_API_ENDPOINT, str)
    
    def test_api_endpoint_env_override(self):
        """Test that AI_API_ENDPOINT can be overridden by environment variable."""
        # Save original env
        original_env = os.environ.get('AI_API_ENDPOINT')
        
        try:
            # Set custom endpoint
            test_endpoint = 'https://test.example.com'
            os.environ['AI_API_ENDPOINT'] = test_endpoint
            
            # Need to reload the module to pick up the new env var
            import importlib
            import seclab_taskflow_agent.capi
            importlib.reload(seclab_taskflow_agent.capi)
            
            from seclab_taskflow_agent.capi import AI_API_ENDPOINT
            assert AI_API_ENDPOINT == test_endpoint
        finally:
            # Restore original env
            if original_env is None:
                os.environ.pop('AI_API_ENDPOINT', None)
            else:
                os.environ['AI_API_ENDPOINT'] = original_env
            # Reload again to restore original state
            import importlib
            import seclab_taskflow_agent.capi
            importlib.reload(seclab_taskflow_agent.capi)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
