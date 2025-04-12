# sample MCP server

A MCP server project

## Components

### Resources

The server implements a simple note storage system with:

- Custom note:// URI scheme for accessing individual notes
- Each note resource has a name, description and text/plain mimetype

### Prompts

The server provides a single prompt:

- summarize-notes: Creates summaries of all stored notes
  - Optional "style" argument to control detail level (brief/detailed)
  - Generates prompt combining all current notes with style preference

### Tools

#### Weather Server

The server implements two tools:

- get_alerts: Get weather alerts for a US state
  - Takes "state" as a required string argument
- get_forecast: Get weather forecast for a location
  - Takes "latitude" and "longitude" as required float arguments

#### SSH Server

The server implements four SSH-related tools:

- ssh_execute: Executes commands on remote hosts via SSH
  - Required: "host" (接続先), "command" (実行コマンド)
  - Optional: "user" (ユーザー名), "port" (ポート番号)
- scp_upload: Uploads files to remote hosts
  - Required: "local_path" (ローカルファイル), "host" (接続先), "remote_path" (リモートパス)
  - Optional: "user" (ユーザー名), "port" (ポート番号)
- scp_download: Downloads files from remote hosts
  - Required: "host" (接続先), "remote_path" (リモートファイル), "local_path" (保存先)
  - Optional: "user" (ユーザー名), "port" (ポート番号)
- ssh_list_hosts: Lists all hosts configured in ~/.ssh/config

## Configuration

[TODO: Add configuration details specific to your implementation]

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "sample": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/ryuichi/ghq/github.com/ryuichi1208/homecmd/mcp/sample",
        "run",
        "sample"
      ]
    },
    "ssh": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/ryuichi/ghq/github.com/ryuichi1208/homecmd/mcp/sample",
        "run",
        "sample-ssh"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```
  "mcpServers": {
    "sample": {
      "command": "uvx",
      "args": [
        "sample"
      ]
    },
    "ssh": {
      "command": "uvx",
      "args": [
        "sample-ssh"
      ]
    }
  }
  ```
</details>

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:

```bash
uv sync
```

2. Build package distributions:

```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:

```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:

- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
# Weather server
npx @modelcontextprotocol/inspector uv --directory /Users/ryuichi/ghq/github.com/ryuichi1208/homecmd/mcp/sample run sample

# SSH server
npx @modelcontextprotocol/inspector uv --directory /Users/ryuichi/ghq/github.com/ryuichi1208/homecmd/mcp/sample run sample-ssh
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.
