# SPDX-FileCopyrightText: 2025 GitHub
# SPDX-License-Identifier: MIT

# CAPI specific interactions
import httpx
import json
import logging
import os
from urllib.parse import urlparse

# you can also set https://models.github.ai/inference if you prefer
# but beware that your taskflows need to reference the correct model id
# since the Modeld API uses it's own id schema, use -l with your desired
# endpoint to retrieve the correct id names to use for your taskflow
COPILOT_API_ENDPOINT = os.getenv('COPILOT_API_ENDPOINT', default='https://api.githubcopilot.com')
COPILOT_INTEGRATION_ID = 'vscode-chat'

# assume we are >= python 3.9 for our type hints
def list_capi_models(token: str) -> dict[str, dict]:
    """Retrieve a dictionary of available CAPI models"""
    models = {}
    try:
        match urlparse(COPILOT_API_ENDPOINT).netloc:
            case 'api.githubcopilot.com':
                models_catalog = 'models'
            case 'models.github.ai':
                models_catalog = 'catalog/models'
            case _:
                raise ValueError(f"Unsupported Model Endpoint: {COPILOT_API_ENDPOINT}")
        r = httpx.get(httpx.URL(COPILOT_API_ENDPOINT).join(models_catalog),
                      headers={
                          'Accept': 'application/json',
                          'Authorization': f'Bearer {token}',
                          'Copilot-Integration-Id': COPILOT_INTEGRATION_ID
                      })
        r.raise_for_status()
        # CAPI vs Models API
        match urlparse(COPILOT_API_ENDPOINT).netloc:
            case 'api.githubcopilot.com':
                models_list = r.json().get('data', [])
            case 'models.github.ai':
                models_list = r.json()
        for model in models_list:
            models[model.get('id')] = dict(model)
    except httpx.RequestError as e:
        logging.error(f"Request error: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"JSON error: {e}")
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error: {e}")
    return models

def supports_tool_calls(model: str, models: dict) -> bool:
    match urlparse(COPILOT_API_ENDPOINT).netloc:
        case 'api.githubcopilot.com':
            return models.get(model, {}).\
                get('capabilities', {}).\
                get('supports', {}).\
                get('tool_calls', False)
        case 'models.github.ai':
            return 'tool-calling' in models.get(model, {}).\
                get('capabilities', [])
        case _:
            raise ValueError(f"Unsupported Model Endpoint: {COPILOT_API_ENDPOINT}")

def list_tool_call_models(token: str) -> dict[str, dict]:
    models = list_capi_models(token)
    tool_models = {}
    for model in models:
        if supports_tool_calls(model, models) is True:
            tool_models[model] = models[model]
    return tool_models
