"""
MCP ChatBot - HTTPトランスポート実装

Streamable HTTPトランスポートを使用してMCPサーバーに接続する。
"""

import asyncio
import logging

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from config.config import BedrockConfig, TableauMCPHttpConfig
from bedrock.mcp_chatbot_base import BaseMCPChatBot

# MCPライブラリのWARNINGログを抑制
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger().setLevel(logging.ERROR)


class MCPChatBotHTTP(BaseMCPChatBot):
    """HTTPトランスポートを使用したMCP ChatBot"""

    def __init__(
        self, bedrock_config: BedrockConfig, mcp_server_config: TableauMCPHttpConfig
    ):
        """
        Args:
            bedrock_config: Bedrock設定
            mcp_server_config: MCPサーバー設定（HTTP）
        """
        super().__init__(bedrock_config)
        self.mcp_server_config = mcp_server_config

    async def connect_to_mcp_server(self, callback):
        """HTTPトランスポートでMCPサーバーに接続"""
        async with streamablehttp_client(self.mcp_server_config.tableau_mcp_url) as (
            read,
            write,
            _,
        ):
            async with ClientSession(read, write) as session:
                self.mcp_session = session
                await session.initialize()

                # 利用可能なツールを取得
                tools_result = await session.list_tools()
                self.available_tools = tools_result.tools
                print(
                    f"Connected to MCP Server. Available tools: {len(self.available_tools)}"
                )

                # コールバック関数を実行
                await callback()


async def main():
    """メイン関数"""
    # 環境変数から設定を読み込む
    bedrock_config = BedrockConfig.from_env()
    mcp_server_config = TableauMCPHttpConfig.from_env()

    # ChatBotを初期化
    chatbot = MCPChatBotHTTP(bedrock_config, mcp_server_config)

    async def chat_loop():
        """対話ループ"""
        print("\nMCP ChatBot Ready! (HTTP transport)")
        print("Type 'quit' to exit\n")

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ["quit", "exit"]:
                break

            if not user_input:
                continue

            response = await chatbot.chat(user_input)
            print(f"Bot: {response}\n")

    # MCP Serverに接続して対話を開始
    print("Connecting to MCP Server (HTTP)...")
    await chatbot.connect_to_mcp_server(chat_loop)


if __name__ == "__main__":
    asyncio.run(main())
