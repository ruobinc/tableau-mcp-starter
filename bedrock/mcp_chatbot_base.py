"""
汎用MCP ChatBot基底クラス

任意のMCPサーバーと連携できるChatBotの基底実装。
トランスポート層はサブクラスで実装する。
"""

from abc import ABC, abstractmethod
from typing import Any

import boto3
from mcp import ClientSession

from config.config import BedrockConfig


class BaseMCPChatBot(ABC):
    """Bedrock Claude-4を使用した汎用MCP ChatBot基底クラス"""

    def __init__(self, bedrock_config: BedrockConfig):
        """
        Args:
            bedrock_config: Bedrock設定
        """
        self.bedrock_config = bedrock_config

        # Bedrock クライアントの初期化
        # boto3は環境変数AWS_BEARER_TOKEN_BEDROCKから自動的に認証情報を取得
        self.bedrock_client = boto3.client(
            "bedrock-runtime",
            region_name=bedrock_config.bedrock_region,
        )

        self.conversation_history = []
        self.mcp_session: ClientSession | None = None
        self.available_tools = []

    @abstractmethod
    async def connect_to_mcp_server(self, callback):
        """
        MCPサーバーに接続してコールバックを実行

        サブクラスで実装必須。トランスポート固有の接続処理を実装する。

        Args:
            callback: 接続後に実行するコールバック関数
        """
        pass

    def format_tools_for_bedrock(self) -> list[dict[str, Any]]:
        """MCPツールをBedrock形式に変換"""
        bedrock_tools = []
        for tool in self.available_tools:
            bedrock_tool = {
                "toolSpec": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "inputSchema": {"json": tool.inputSchema},
                }
            }
            bedrock_tools.append(bedrock_tool)
        return bedrock_tools

    async def call_mcp_tool(self, tool_name: str, arguments: dict) -> Any:
        """MCPツールを呼び出し"""
        if not self.mcp_session:
            raise RuntimeError("MCP session not initialized")

        result = await self.mcp_session.call_tool(tool_name, arguments)
        return result

    async def chat(self, user_message: str) -> str:
        """ユーザーメッセージを処理してレスポンスを返す"""
        try:
            # 最初のメッセージのみ会話履歴に追加（ツール呼び出し後の再帰では追加しない）
            if user_message:
                self.conversation_history.append(
                    {"role": "user", "content": [{"text": user_message}]}
                )

            # Bedrock Converse APIを呼び出し
            response = self.bedrock_client.converse(
                modelId=self.bedrock_config.model_id,
                messages=self.conversation_history,
                toolConfig={"tools": self.format_tools_for_bedrock()}
                if self.available_tools
                else None,
            )

            # レスポンスを処理
            assistant_message = response["output"]["message"]
            self.conversation_history.append(assistant_message)

            # ツール使用の処理
            if assistant_message.get("content"):
                # すべてのtoolUseを収集
                tool_results_content = []
                has_tool_use = False

                for content in assistant_message["content"]:
                    if "toolUse" in content:
                        has_tool_use = True
                        tool_use = content["toolUse"]
                        tool_name = tool_use["name"]
                        tool_input = tool_use["input"]

                        print(f"   → Calling MCP tool: {tool_name}")

                        # MCPツールを呼び出し
                        tool_result = await self.call_mcp_tool(tool_name, tool_input)

                        # MCPのContentBlockリストをBedrock形式に変換
                        bedrock_content = []
                        for block in tool_result.content:
                            if block.type == "text":
                                bedrock_content.append({"text": block.text})
                            elif block.type == "image":
                                # Bedrockのtool resultはイメージを直接サポートしないため、説明文として扱う
                                bedrock_content.append(
                                    {"text": f"[Image: {block.mimeType}]"}
                                )
                            else:
                                # その他のタイプは文字列化
                                bedrock_content.append({"text": str(block)})

                        # ツール結果ブロックを作成
                        tool_result_block = {
                            "toolResult": {
                                "toolUseId": tool_use["toolUseId"],
                                "content": bedrock_content,
                            }
                        }

                        if tool_result.isError:
                            tool_result_block["toolResult"]["status"] = "error"

                        # ツール結果をリストに追加
                        tool_results_content.append(tool_result_block)

                # すべてのツール結果を一度に会話履歴に追加
                if has_tool_use:
                    self.conversation_history.append(
                        {
                            "role": "user",
                            "content": tool_results_content,
                        }
                    )

                    # ツール結果を元に再度Bedrockを呼び出し（空文字列で再帰）
                    return await self.chat("")

            # テキストレスポンスを抽出
            for content in assistant_message.get("content", []):
                if "text" in content:
                    return content["text"]

            return "No response generated"

        except Exception as e:
            # エラーログを出力
            error_msg = f"Error during chat: {type(e).__name__}: {str(e)}"
            print(f"   ✗ {error_msg}")
            return f"申し訳ございません。エラーが発生しました: {str(e)}"
