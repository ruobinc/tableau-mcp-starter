"""
ChatBot設定管理モジュール

このモジュールは、Bedrock設定とTableau MCP Server設定を管理します。
環境変数から設定を読み込み、バリデーションを行います。
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class BedrockConfig:
    """AWS Bedrock設定"""

    bedrock_region: str = "us-east-1"
    model_id: str = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

    @classmethod
    def from_env(cls) -> "BedrockConfig":
        """環境変数から設定を読み込む"""
        if not os.environ.get("AWS_BEARER_TOKEN_BEDROCK"):
            raise ValueError(
                "AWS_BEARER_TOKEN_BEDROCK environment variable is required"
            )

        return cls(
            bedrock_region=os.environ.get("BEDROCK_REGION", "us-east-1"),
            model_id=os.environ.get(
                "BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
            ),
        )


@dataclass
class TableauMCPHttpConfig:
    """Tableau MCP Server設定（Streamable HTTP transport用）"""

    tableau_mcp_url: str

    @classmethod
    def from_env(cls) -> "TableauMCPHttpConfig":
        """環境変数から設定を読み込む"""
        tableau_mcp_url = os.environ.get("TABLEAU_MCP_URL")
        if not tableau_mcp_url:
            raise ValueError("TABLEAU_MCP_URL environment variable is required")

        return cls(tableau_mcp_url=tableau_mcp_url)


@dataclass
class TableauMCPStdioConfig:
    """Tableau MCP Server設定（stdio transport用）"""

    tableau_server_command: str
    tableau_server_args: list[str]
    tableau_server: str
    tableau_site_name: str
    tableau_auth: str
    tableau_pat_name: str
    tableau_pat_value: str
    tableau_jwt_sub_claim: str
    tableau_connected_app_client_id: str
    tableau_connected_app_secret_id: str
    tableau_connected_app_secret_value: str

    @classmethod
    def from_env(cls) -> "TableauMCPStdioConfig":
        """環境変数から設定を読み込む"""
        tableau_server = os.environ.get("TABLEAU_SERVER")
        tableau_site_name = os.environ.get("TABLEAU_SITE_NAME")
        tableau_auth = os.environ.get("TABLEAU_AUTH")
        tableau_pat_name = os.environ.get("TABLEAU_PAT_NAME")
        tableau_pat_value = os.environ.get("TABLEAU_PAT_VALUE")
        tableau_jwt_sub_claim = os.environ.get("TABLEAU_JWT_SUB_CLAIM")
        tableau_connected_app_client_id = os.environ.get(
            "TABLEAU_CONNECTED_APP_CLIENT_ID"
        )
        tableau_connected_app_secret_id = os.environ.get(
            "TABLEAU_CONNECTED_APP_SECRET_ID"
        )
        tableau_connected_app_secret_value = os.environ.get(
            "TABLEAU_CONNECTED_APP_SECRET_VALUE"
        )
        tableau_server_command = "npx"
        tableau_server_args_str = "-y @tableau/mcp-server@latest"

        return cls(
            tableau_server_command=tableau_server_command,
            tableau_server_args=tableau_server_args_str.split(),
            tableau_server=tableau_server,
            tableau_site_name=tableau_site_name,
            tableau_auth=tableau_auth,
            tableau_pat_name=tableau_pat_name,
            tableau_pat_value=tableau_pat_value,
            tableau_jwt_sub_claim=tableau_jwt_sub_claim,
            tableau_connected_app_client_id=tableau_connected_app_client_id,
            tableau_connected_app_secret_id=tableau_connected_app_secret_id,
            tableau_connected_app_secret_value=tableau_connected_app_secret_value,
        )

    def get_server_env(self) -> dict[str, str]:
        """Tableau MCP Server用の環境変数辞書を返す"""
        return {
            "TRANSPORT": "stdio",
            "SERVER": self.tableau_server,
            "SITE_NAME": self.tableau_site_name,
            "AUTH": self.tableau_auth,
            "PAT_NAME": self.tableau_pat_name,
            "PAT_VALUE": self.tableau_pat_value,
            "JWT_SUB_CLAIM": self.tableau_jwt_sub_claim,
            "CONNECTED_APP_CLIENT_ID": self.tableau_connected_app_client_id,
            "CONNECTED_APP_SECRET_ID": self.tableau_connected_app_secret_id,
            "CONNECTED_APP_SECRET_VALUE": self.tableau_connected_app_secret_value,
            "EXCLUDE_TOOLS": "",
        }
