# Tableau MCP STARTER

[Tableau MCP](https://github.com/tableau/tableau-mcp)を使用した会話Botのテンプレートです。

## プロジェクト構成

```
tableau-mcp-starter/
├── config/
│   └── config.py                   # Bedrock/Tableau MCP設定
├── bedrock/
│   ├── mcp_chatbot_base.py         # ChatBot基底クラス
│   ├── mcp_chatbot_http.py         # HTTPトランスポート実装
│   └── mcp_chatbot_stdio.py        # stdioトランスポート実装
└── tests/
    └── bedrock/
        ├── test_chatbot.py
        └── test_chatbot_stdio.py
```

## セットアップ

```bash
# 依存関係のインストール
uv sync

# 環境変数の設定
cp .env.example .env
# .envファイルを編集して実際の値を設定
```

## 使用方法

### HTTP Transport（リモート接続）
リモートのTableau MCP ServerにHTTP経由で接続します。

```bash
uv run python bedrock/mcp_chatbot_http.py
```

### stdio Transport（ローカル起動）
ローカルでTableau MCP Serverプロセスを起動します（Claude Desktopと同じ方式）。

```bash
uv run python bedrock/mcp_chatbot_stdio.py
```

**操作方法:**
- プロンプトで質問を入力（例：「私が見れるTableauのワークブックとビューの一覧を教えてください」）
- `quit`または`exit`で終了
