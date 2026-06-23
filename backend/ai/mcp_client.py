import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
load_dotenv()

MCP_SERVER_URL = os.environ["MCP_SERVER_URL"]


async def get_mcp_client():

    client = MultiServerMCPClient(
        {
            "medical": {
                "transport": "streamable_http",
                "url": MCP_SERVER_URL,
            }
        }
    )

    return client