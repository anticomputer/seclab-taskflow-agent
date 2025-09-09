import logging
import asyncio
from threading import Thread
import json

from mcp.types import CallToolResult, TextContent
from agents.mcp import MCPServerStdio

from env_utils import swap_env

DEFAULT_MCP_CLIENT_SESSION_TIMEOUT = 120

# used for debugging asyncio event loop issues in mcp stdio servers
# lifts the asyncio event loop in use to a dedicated threaded loop
class AsyncDebugMCPServerStdio(MCPServerStdio):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        class AsyncLoopThread(Thread):
            def __init__(self):
                super().__init__(daemon=True)
                self.loop = asyncio.new_event_loop()
            def run(self):
                asyncio.set_event_loop(self.loop)
                self.loop.run_forever()
        self.t = AsyncLoopThread()
        self.t.start()
        self.lock = asyncio.Lock()

    async def connect(self, *args, **kwargs):
        return asyncio.run_coroutine_threadsafe(
            super().connect(*args, **kwargs),
            self.t.loop).result()

    async def list_tools(self, *args, **kwargs):
        return asyncio.run_coroutine_threadsafe(
            super().list_tools(*args, **kwargs),
            self.t.loop).result()

    async def call_tool(self, *args, **kwargs):
        async with self.lock:
            return asyncio.run_coroutine_threadsafe(
                super().call_tool(*args, **kwargs),
                self.t.loop).result()

    async def cleanup(self, *args, **kwargs):
        try:
            asyncio.run_coroutine_threadsafe(
                super().cleanup(*args, **kwargs),
                self.t.loop).result()
        except asyncio.CancelledError:
            pass
        finally:
            self.t.loop.stop()
            self.t.join()


# a hack class that works around buggy jsonrpc stdio behavior in FastMCP 1.0
# long running high volume processes tend to get confused and miss i/o
# if you're seeing behavior where your mcp server tool call completes
# but the results never arrive to to the mcp client side, try and set
# reconnecting: true in your toolbox config
class ReconnectingMCPServerStdio(MCPServerStdio):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reconnecting_lock = asyncio.Lock()

    async def connect(self):
        logging.debug("Ignoring mcp connect request on purpose")

    async def cleanup(self):
        logging.debug("Ignoring mcp cleanup request on purpose")

    async def list_tools(self, *args, **kwargs):
        async with self.reconnecting_lock:
            await super().connect()
            try:
                result = await super().list_tools(*args, **kwargs)
            finally:
                await super().cleanup()
            return result

    async def call_tool(self, *args, **kwargs):
        logging.debug("Using reconnecting call_tool for stdio mcp")
        async with self.reconnecting_lock:
            await super().connect()
            try:
                result = await super().call_tool(*args, **kwargs)
            finally:
                await super().cleanup()
            return result

class MCPNamespaceWrap:
    def __init__(self, confirms, obj):
        self.confirms = confirms
        self._obj = obj
        self.namespace = f"{obj.name.upper().replace(' ', '_')}_"

    def __getattr__(self, name):
        attr = getattr(self._obj, name)
        if callable(attr):
            match name:
                case 'call_tool':
                    return self.call_tool
                case 'list_tools':
                    return self.list_tools
                case _:
                    return attr
        return attr

    async def list_tools(self, *args, **kwargs):
        result = await self._obj.list_tools(*args, **kwargs)
        namespaced_tools = []
        for tool in result:
            tool_copy = tool.copy()
            tool_copy.name = f"{self.namespace}{tool.name}"
            namespaced_tools.append(tool_copy)
        return namespaced_tools

    def confirm_tool(self, tool_name, args):
        while True:
            yn = input(f"** 🤖❗ Allow tool call?: {tool_name}({','.join([json.dumps(arg) for arg in args])}) (yes/no): ")
            if yn in ["yes", "y"]:
                return True
            elif yn in ["no", "n"]:
                return False

    async def call_tool(self, *args, **kwargs):
        _args = list(args)
        tool_name = _args[0]
        tool_name = tool_name.removeprefix(self.namespace)
        # to run headless, just make confirms an empty list
        if self.confirms and tool_name in self.confirms:
            if not self.confirm_tool(tool_name, _args[1:]):
                result = CallToolResult(
                    content=[
                        TextContent(
                            type='text',
                            text='Tool call not allowed.',
                            annotations=None,
                            meta=None)]
                )
                return result
        _args[0] = tool_name
        args = tuple(_args)
        result = await self._obj.call_tool(*args, **kwargs)
        return result

def mcp_client_params(available_toolboxes: dict, requested_toolboxes: list):
    """Return all the data needed to initialize an mcp server client"""
    client_params = {}
    for tb in requested_toolboxes:
        if tb not in available_toolboxes:
            e = f"Task requested non-existent toolbox {tb}!"
            logging.critical(e)
            raise ValueError(e)
        else:
            kind = available_toolboxes[tb]['server_params'].get('kind')
            reconnecting = available_toolboxes[tb]['server_params'].get('reconnecting', False)
            server_params = {'kind': kind, 'reconnecting': reconnecting}
            match kind:
                case 'stdio':
                    env = available_toolboxes[tb]['server_params'].get('env')
                    args = available_toolboxes[tb]['server_params'].get('args')
                    logging.debug(f"Initializing toolbox: {tb}\nargs:\n{args }\nenv:\n{env}\n")
                    if env and isinstance(env, dict):
                        for k, v in dict(env).items():
                            try:
                                env[k] = swap_env(v)
                            except LookupError as e:
                                logging.critical(e)
                                logging.info("Assuming toolbox has default configuration available")
                                del env[k]
                                pass
                    logging.debug(f"Tool call environment: {env}")
                    if args and isinstance(args, list):
                        for i, v in enumerate(args):
                            args[i] = swap_env(v)
                    logging.debug(f"Tool call args: {args}")
                    server_params['command'] = available_toolboxes[tb]['server_params'].get('command')
                    server_params['args'] = args
                    server_params['env'] = env
                case 'sse':
                    headers = available_toolboxes[tb]['server_params'].get('headers')
                    # support {{ env SOMETHING }} for header values as well for e.g. tokens
                    if headers and isinstance(headers, dict):
                        for k, v in headers.items():
                            headers[k] = swap_env(v)
                    # if None will default to float(5) in client code
                    timeout = available_toolboxes[tb]['server_params'].get('timeout')
                    server_params['url'] = available_toolboxes[tb]['server_params'].get('url')
                    server_params['headers'] = headers
                    server_params['timeout'] = timeout
                case 'streamable':
                    headers = available_toolboxes[tb]['server_params'].get('headers')
                    # support {{ env SOMETHING }} for header values as well for e.g. tokens
                    if headers and isinstance(headers, dict):
                        for k, v in headers.items():
                            headers[k] = swap_env(v)
                    # if None will default to float(5) in client code
                    timeout = available_toolboxes[tb]['server_params'].get('timeout')
                    server_params['url'] = available_toolboxes[tb]['server_params'].get('url')
                    server_params['headers'] = headers
                    server_params['timeout'] = timeout
                case _:
                    raise ValueError(f"Unsupported MCP transport {kind}")
            confirms = available_toolboxes[tb].get('confirm', [])
            server_prompt = available_toolboxes[tb].get('server_prompt', '')
            client_session_timeout = float(available_toolboxes[tb].get('client_session_timeout', 0))
            client_params[tb] = (server_params, confirms, server_prompt, client_session_timeout)
    return client_params

def mcp_system_prompt(system_prompt: str, task: str,
                      tools: list[str] = [],
                      resources: list[str] = [],
                      resource_templates: list[str] = [],
                      important_guidelines: list[str] = [],
                      server_prompts: list[str] = []):
    """Return a well constructed system prompt"""
    prompt = """
{system_prompt}
""".format(system_prompt=system_prompt)

    if tools:
        prompt += """

# Available Tools

- {tools}
""".format(tools="\n- ".join(tools))

    if resources:
        prompt += """

# Available Resources

- {resources}
""".format(resources="\n- ".join(resources))

    if resource_templates:
        prompt += """

# Available Resource Templates

- {resource_templates}
""".format(resource_templates="\n- ".join(resource_templates))

    if important_guidelines:
        prompt += """

# Important Guidelines

- IMPORTANT: {guidelines}
""".format(guidelines="\n- IMPORTANT: ".join(important_guidelines))

    if server_prompts:
        prompt += """

# Additional Guidelines

{server_prompts}

""".format(server_prompts="\n\n".join(server_prompts))

    if task:
        prompt += """

# Primary Task to Complete

{task}

""".format(task=task)

    return prompt
