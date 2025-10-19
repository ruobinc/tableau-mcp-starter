"""
MCP ChatBot - stdioトランスポート実装

stdioトランスポートを使用してMCPサーバーに接続する。
"""

import asyncio
import logging

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config.config import BedrockConfig, TableauMCPStdioConfig
from bedrock.mcp_chatbot_base import BaseMCPChatBot

# MCPライブラリのWARNINGログを抑制
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger().setLevel(logging.ERROR)


class MCPChatBotStdio(BaseMCPChatBot):
    """stdioトランスポートを使用したMCP ChatBot"""

    def __init__(
        self, bedrock_config: BedrockConfig, mcp_server_config: TableauMCPStdioConfig
    ):
        """
        Args:
            bedrock_config: Bedrock設定
            mcp_server_config: MCPサーバー設定（stdio）
        """
        super().__init__(bedrock_config)
        self.mcp_server_config = mcp_server_config

    async def connect_to_mcp_server(self, callback):
        """stdioトランスポートでMCPサーバーに接続"""
        # stdio server parametersを設定
        server_params = StdioServerParameters(
            command=self.mcp_server_config.tableau_server_command,
            args=self.mcp_server_config.tableau_server_args,
            env=self.mcp_server_config.get_server_env(),
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.mcp_session = session
                await session.initialize()

                # 利用可能なツールを取得
                tools_result = await session.list_tools()
                self.available_tools = tools_result.tools
                print(
                    f"Connected to MCP Server (stdio). Available tools: {len(self.available_tools)}"
                )

                # コールバック関数を実行
                await callback()


async def main():
    """メイン関数"""
    # 環境変数から設定を読み込む
    bedrock_config = BedrockConfig.from_env()
    mcp_server_config = TableauMCPStdioConfig.from_env()

    # ChatBotを初期化
    chatbot = MCPChatBotStdio(bedrock_config, mcp_server_config)

    async def chat_loop():
        """対話ループ"""
        print("\nMCP ChatBot Ready! (stdio transport)")
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
    print("Connecting to MCP Server (stdio)...")
    await chatbot.connect_to_mcp_server(chat_loop)


if __name__ == "__main__":
    asyncio.run(main())
