from langchain_mcp_adapters.client import MultiServerMCPClient 

async def get_mcp_client():

    client=MultiServerMCPClient(
        {
            "medical": {
                "transport": "streamable_http",
                "url": "https://medicalresearch-mcp-server.onrender.com/mcp",
            }         
        }
    )

    return client