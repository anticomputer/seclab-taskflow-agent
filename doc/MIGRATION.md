# Jinja2 Templating Migration Guide

This guide explains how to migrate taskflow YAML files from version 1 (custom template syntax) to version 2 (Jinja2 templating).

## Overview

Version 2 replaces the custom regex-based template processing with Jinja2, providing:
- More powerful templating features (filters, conditionals, loops)
- Better error messages with clear variable undefined errors
- Industry-standard syntax familiar to many developers
- Extensibility for future template features

## Syntax Changes

### 1. Global Variables

**Version 1:**
```yaml
globals:
  fruit: apples
taskflow:
  - task:
      user_prompt: |
        Tell me about {{ GLOBALS_fruit }}.
```

**Version 2:**
```yaml
globals:
  fruit: apples
taskflow:
  - task:
      user_prompt: |
        Tell me about {{ globals.fruit }}.
```

**Nested structures:**
```yaml
globals:
  config:
    model: gpt-4
    temperature: 0.7
taskflow:
  - task:
      user_prompt: |
        Using {{ globals.config.model }} with temp {{ globals.config.temperature }}
```

### 2. Input Variables

**Version 1:**
```yaml
user_prompt: |
  Color: {{ INPUTS_color }}
```

**Version 2:**
```yaml
user_prompt: |
  Color: {{ inputs.color }}
```

### 3. Result Variables

**Version 1 (primitives):**
```yaml
repeat_prompt: true
user_prompt: |
  Process {{ RESULT }}
```

**Version 0.1.0:**
```yaml
repeat_prompt: true
user_prompt: |
  Process {{ result }}
```

**Version 1 (dictionary keys):**
```yaml
user_prompt: |
  Function {{ RESULT_name }} has body {{ RESULT_body }}
```

**Version 0.1.0:**
```yaml
user_prompt: |
  Function {{ result.name }} has body {{ result.body }}
```

### 4. Environment Variables

**Version 0.0.x:**
```yaml
env:
  DATABASE: "{{ env DATABASE_URL }}"
```

**Version 0.1.0:**
```yaml
env:
  DATABASE: "{{ env('DATABASE_URL') }}"
```

**With defaults (new feature):**
```yaml
env:
  DATABASE: "{{ env('DATABASE_URL', 'localhost:5432') }}"
```

### 5. Reusable Prompts

**Version 0.0.x:**
```yaml
user_prompt: |
  Main task.
  {{ PROMPTS_examples.prompts.shared }}
```

**Version 0.1.0:**
```yaml
user_prompt: |
  Main task.
  {% include 'examples.prompts.shared' %}
```

## New Jinja2 Features

### Filters

Transform values with filters:

```yaml
user_prompt: |
  Uppercase: {{ globals.name | upper }}
  Lowercase: {{ globals.name | lower }}
  Default: {{ globals.optional | default('N/A') }}
  List length: {{ globals.items | length }}
```

### Conditionals

Add conditional logic:

```yaml
user_prompt: |
  {% if globals.debug_mode %}
  Running in debug mode
  {% else %}
  Running in production mode
  {% endif %}

  {% if result.score > 0.8 %}
  High confidence result
  {% endif %}
```

### Loops

Iterate over collections:

```yaml
user_prompt: |
  Analyze these functions:
  {% for func in result.functions %}
  - {{ func.name }}: {{ func.complexity }}
  {% endfor %}
```

### Math Operations

Perform calculations:

```yaml
user_prompt: |
  Sum: {{ result.a + result.b }}
  Product: {{ result.count * 2 }}
  Comparison: {% if result.score > 0.5 %}Pass{% else %}Fail{% endif %}
```

## Automated Migration

Use the provided migration script:

```bash
# Migrate all YAML files in directory
python scripts/migrate_to_jinja2.py /path/to/taskflows

# Preview changes without writing
python scripts/migrate_to_jinja2.py --dry-run /path/to/taskflows

# Migrate specific file
python scripts/migrate_to_jinja2.py myflow.yaml
```

## Manual Migration Checklist

1. Update YAML version from `1` to `2`
2. Replace `{{ GLOBALS_` with `{{ globals.`
3. Replace `{{ INPUTS_` with `{{ inputs.`
4. Replace `{{ RESULT_` with `{{ result.`
5. Replace `{{ RESULT }}` with `{{ result }}`
6. Replace `{{ env VAR }}` with `{{ env('VAR') }}`
7. Replace `{{ PROMPTS_` with `{% include '` and add closing `' %}`
8. Test taskflow execution

## Testing Your Migration

```bash
# Run specific taskflow
python -m seclab_taskflow_agent -t your.taskflow.name

# Run with globals
python -m seclab_taskflow_agent -t your.taskflow.name -g key=value
```

## Common Issues

### Issue: `UndefinedError: 'globals' is undefined`

**Cause:** Using `{{ globals.key }}` when no globals are defined

**Fix:** Either define globals in taskflow or use Jinja2's get method:
```yaml
{{ globals.get('key', 'default') }}
```

### Issue: `TemplateNotFound: examples.prompts.mypromp`

**Cause:** Typo in include path

**Fix:** Verify path matches file location exactly

### Issue: Environment variable errors

**Cause:** Required env var not set

**Fix:** Set env var or make it optional:
```yaml
{{ env('VAR', 'default') }}
```

## Backwards Compatibility

Version 0.0.x syntax is no longer supported. Attempting to load a v0.1.0 file will fail with:

```
VersionException: YAML file uses unsupported version 1 template syntax.
Version 2 (Jinja2) is required.
Migrate using: python scripts/migrate_to_jinja2.py <file>
```

All v0.0.x files must be migrated to v0.1.0 before use.

## Additional Resources

- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Jinja2 Template Designer Documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/)
- Example taskflows in `examples/taskflows/`
