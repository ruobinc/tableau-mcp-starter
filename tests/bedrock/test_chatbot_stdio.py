"""
Tableau MCP ChatBot（stdio transport）の簡易テストスクリプト
"""

import asyncio

from dotenv import load_dotenv

from bedrock.mcp_chatbot_stdio import MCPChatBotStdio
from config.config import BedrockConfig, TableauMCPStdioConfig

# .envファイルから環境変数を読み込む
load_dotenv()


async def test_chatbot():
    """ChatBotの基本機能をテスト"""
    print("=== Tableau MCP ChatBot Test (stdio transport) ===\n")

    # 環境変数から設定を読み込む
    try:
        bedrock_config = BedrockConfig.from_env()
        tableau_config = TableauMCPStdioConfig.from_env()
    except ValueError as e:
        print(f"Error: {e}")
        return

    # ChatBotを初期化
    chatbot = MCPChatBotStdio(bedrock_config, tableau_config)

    async def run_tests():
        """テストを実行"""
        print("   ✓ Connected successfully!")
        print(f"   ✓ Available tools: {len(chatbot.available_tools)}\n")

        # 利用可能なツールを表示
        print("2. Available MCP Tools:")
        for i, tool in enumerate(chatbot.available_tools[:5], 1):
            print(f"   {i}. {tool.name}: {tool.description}")
        if len(chatbot.available_tools) > 5:
            print(f"   ... and {len(chatbot.available_tools) - 5} more tools\n")

        # 簡単な会話をテスト
        print("3. Testing conversation with Bedrock Claude:")
        test_message = "私が見れるTableauのデータソース一覧を教えてください"
        print(f"   User: {test_message}")

        try:
            response = await chatbot.chat(test_message)
            print(f"   Bot: {response}\n")
            print("   ✓ Conversation test successful!")
        except Exception as e:
            print(f"   ✗ Error during conversation: {e}")
            import traceback

            traceback.print_exc()

        print("\n=== Test Complete ===")

    # Tableau MCP Serverに接続してテストを実行
    print("1. Connecting to Tableau MCP Server (stdio)...")
    await chatbot.connect_to_mcp_server(run_tests)


if __name__ == "__main__":
    asyncio.run(test_chatbot())
