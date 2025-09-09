import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logs/mcp_echo.log',
    filemode='a'
)
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Echo")

@mcp.resource("echo://1/{message}")
def echo_resource1(message: str) -> str:
    """Echo a message as a resource"""
    return f"Resource 1 echo: {message}"

@mcp.resource("echo://2/{message}")
def echo_resource2(message: str) -> str:
    """Echo a message as a resource"""
    return f"Resource 2 echo: {message}"

@mcp.tool()
def echo_tool(message: str) -> str:
    """Echo a message as a tool"""
    return f"Tool echo: {message}"

@mcp.prompt()
def echo_prompt(message: str) -> str:
    """Create an echo prompt"""
    return f"Please process this message: {message}"

if __name__ == "__main__":
    mcp.run()
