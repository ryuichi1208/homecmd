from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

# ローカルMCPサーバーを定義
stdio_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="uv run --directory  /Users/ryuichi/ghq/github.com/ryuichi1208/ranger-mcp-server ranger_fastmcp.py",
        args=[""]
    )
))

# 利用可能なツールを読み込んでエージェントに設定
with stdio_mcp_client:
    agent = Agent(
        tools=stdio_mcp_client.list_tools_sync()
    )
    agent("元気ですか？")
