# SPDX-FileCopyrightText: 2025 GitHub
# SPDX-License-Identifier: MIT

"""Tests for Jinja2 template utilities."""

import pytest
import os
import jinja2
from seclab_taskflow_agent.template_utils import (
    env_function,
    create_jinja_environment,
    render_template,
    PromptLoader,
)
from seclab_taskflow_agent.available_tools import AvailableTools


class TestEnvFunction:
    """Test environment variable function."""

    def test_env_existing_var(self):
        """Test accessing existing environment variable."""
        os.environ['TEST_VAR_JINJA'] = 'test_value'
        try:
            assert env_function('TEST_VAR_JINJA') == 'test_value'
        finally:
            del os.environ['TEST_VAR_JINJA']

    def test_env_missing_required(self):
        """Test error on missing required variable."""
        with pytest.raises(LookupError, match="Required environment variable"):
            env_function('NONEXISTENT_VAR_JINJA')

    def test_env_with_default(self):
        """Test default value for missing variable."""
        result = env_function('NONEXISTENT_VAR_JINJA', default='default_value', required=False)
        assert result == 'default_value'

    def test_env_optional_missing(self):
        """Test optional variable returns empty string."""
        result = env_function('NONEXISTENT_VAR_JINJA', required=False)
        assert result == ''

    def test_env_with_default_exists(self):
        """Test that existing var takes precedence over default."""
        os.environ['TEST_VAR_DEFAULT'] = 'actual_value'
        try:
            result = env_function('TEST_VAR_DEFAULT', default='default_value')
            assert result == 'actual_value'
        finally:
            del os.environ['TEST_VAR_DEFAULT']


class TestJinjaEnvironment:
    """Test Jinja2 environment setup."""

    def test_create_environment(self):
        """Test environment creation."""
        available_tools = AvailableTools()
        env = create_jinja_environment(available_tools)
        assert isinstance(env, jinja2.Environment)
        assert 'env' in env.globals

    def test_strict_undefined(self):
        """Test undefined variables raise errors."""
        available_tools = AvailableTools()
        env = create_jinja_environment(available_tools)
        template = env.from_string("{{ undefined_var }}")
        with pytest.raises(jinja2.UndefinedError):
            template.render()

    def test_env_function_in_template(self):
        """Test env function works in template."""
        os.environ['TEST_TEMPLATE_VAR'] = 'template_value'
        try:
            available_tools = AvailableTools()
            env = create_jinja_environment(available_tools)
            template = env.from_string("{{ env('TEST_TEMPLATE_VAR') }}")
            result = template.render()
            assert result == 'template_value'
        finally:
            del os.environ['TEST_TEMPLATE_VAR']


class TestRenderTemplate:
    """Test template rendering."""

    def test_render_globals(self):
        """Test rendering with global variables."""
        available_tools = AvailableTools()
        template_str = "Tell me about {{ globals.fruit }}"
        result = render_template(
            template_str,
            available_tools,
            globals_dict={'fruit': 'apples'}
        )
        assert result == "Tell me about apples"

    def test_render_inputs(self):
        """Test rendering with input variables."""
        available_tools = AvailableTools()
        template_str = "Color: {{ inputs.color }}"
        result = render_template(
            template_str,
            available_tools,
            inputs_dict={'color': 'red'}
        )
        assert result == "Color: red"

    def test_render_result_primitive(self):
        """Test rendering with primitive result value."""
        available_tools = AvailableTools()
        template_str = "Value: {{ result }}"
        result = render_template(
            template_str,
            available_tools,
            result_value=42
        )
        assert result == "Value: 42"

    def test_render_result_dict(self):
        """Test rendering with dictionary result value."""
        available_tools = AvailableTools()
        template_str = "Name: {{ result.name }}, Age: {{ result.age }}"
        result = render_template(
            template_str,
            available_tools,
            result_value={'name': 'Alice', 'age': 30}
        )
        assert result == "Name: Alice, Age: 30"

    def test_render_with_env(self):
        """Test rendering with env function."""
        os.environ['TEST_ENV_VAR'] = 'env_value'
        try:
            available_tools = AvailableTools()
            template_str = "Env: {{ env('TEST_ENV_VAR') }}"
            result = render_template(template_str, available_tools)
            assert result == "Env: env_value"
        finally:
            del os.environ['TEST_ENV_VAR']

    def test_render_complex(self):
        """Test rendering with multiple variable types."""
        os.environ['TEST_MODEL'] = 'gpt-4'
        try:
            available_tools = AvailableTools()
            template_str = """Model: {{ env('TEST_MODEL') }}
Fruit: {{ globals.fruit }}
Color: {{ inputs.color }}
Result: {{ result.value }}"""
            result = render_template(
                template_str,
                available_tools,
                globals_dict={'fruit': 'banana'},
                inputs_dict={'color': 'yellow'},
                result_value={'value': 123}
            )
            assert 'gpt-4' in result
            assert 'banana' in result
            assert 'yellow' in result
            assert '123' in result
        finally:
            del os.environ['TEST_MODEL']

    def test_render_undefined_error(self):
        """Test error on undefined variable."""
        available_tools = AvailableTools()
        template_str = "{{ globals.undefined }}"
        with pytest.raises(jinja2.UndefinedError):
            render_template(template_str, available_tools)

    def test_render_nested_dict(self):
        """Test rendering with nested dictionary access."""
        available_tools = AvailableTools()
        template_str = "Config: {{ globals.config.model }}"
        result = render_template(
            template_str,
            available_tools,
            globals_dict={'config': {'model': 'claude-3'}}
        )
        assert result == "Config: claude-3"

    def test_render_with_filter(self):
        """Test Jinja2 filters work."""
        available_tools = AvailableTools()
        template_str = "{{ globals.name | upper }}"
        result = render_template(
            template_str,
            available_tools,
            globals_dict={'name': 'alice'}
        )
        assert result == "ALICE"

    def test_render_empty_context(self):
        """Test rendering with no context variables."""
        available_tools = AvailableTools()
        template_str = "Static text"
        result = render_template(template_str, available_tools)
        assert result == "Static text"


class TestPromptLoader:
    """Test custom prompt loader."""

    def test_load_existing_prompt(self):
        """Test loading existing prompt."""
        available_tools = AvailableTools()
        loader = PromptLoader(available_tools)
        env = jinja2.Environment(loader=loader)

        # Test with actual example prompt
        template = env.get_template('examples.prompts.example_prompt')
        result = template.render()
        assert 'bananas' in result.lower()

    def test_load_nonexistent_prompt(self):
        """Test error on nonexistent prompt."""
        available_tools = AvailableTools()
        loader = PromptLoader(available_tools)
        env = jinja2.Environment(loader=loader)

        with pytest.raises(jinja2.TemplateNotFound):
            env.get_template('nonexistent.prompt')

    def test_include_prompt(self):
        """Test {% include %} directive."""
        available_tools = AvailableTools()
        env = create_jinja_environment(available_tools)

        template_str = """Main content.
{% include 'examples.prompts.example_prompt' %}"""
        template = env.from_string(template_str)
        result = template.render()
        assert 'Main content' in result
        assert 'bananas' in result.lower()

    def test_include_with_context(self):
        """Test that included templates have access to context."""
        available_tools = AvailableTools()
        env = create_jinja_environment(available_tools)

        # Create a template that uses context
        template_str = """Value: {{ globals.test }}
{% include 'examples.prompts.example_prompt' %}"""
        template = env.from_string(template_str)
        result = template.render(globals={'test': 'context_value'})
        assert 'context_value' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
