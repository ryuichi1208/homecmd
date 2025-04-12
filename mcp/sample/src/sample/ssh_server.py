from typing import Any, Dict, Optional
import asyncio
import subprocess
from mcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("ssh")


async def run_command(command: str) -> Dict[str, Any]:
    """コマンドを実行し、結果を返します"""
    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    return {
        "returncode": process.returncode,
        "stdout": stdout.decode("utf-8", errors="replace").strip(),
        "stderr": stderr.decode("utf-8", errors="replace").strip(),
    }


@mcp.tool()
async def ssh_execute(host: str, command: str, user: Optional[str] = None, port: int = 22) -> str:
    """リモートホストでSSHコマンドを実行します。

    Args:
        host: 接続先ホスト名またはIPアドレス
        command: 実行するコマンド
        user: ユーザー名（指定しない場合は現在のユーザー）
        port: SSHポート番号（デフォルト: 22）
    """
    ssh_command = ["ssh"]

    if user:
        ssh_command.append(f"{user}@{host}")
    else:
        ssh_command.append(f"{host}")

    if port != 22:
        ssh_command.extend(["-p", str(port)])

    ssh_command.extend(["-o", "BatchMode=yes"])  # パスワード入力を回避
    ssh_command.extend(["-o", "ConnectTimeout=10"])  # 接続タイムアウト設定
    ssh_command.append(command)

    full_command = " ".join(ssh_command)
    result = await run_command(full_command)

    if result["returncode"] != 0:
        return f"Error executing SSH command: {result['stderr']}"

    return result["stdout"]


@mcp.tool()
async def scp_upload(local_path: str, host: str, remote_path: str, user: Optional[str] = None, port: int = 22) -> str:
    """ローカルファイルをリモートホストにアップロードします。

    Args:
        local_path: アップロードするローカルファイルのパス
        host: 接続先ホスト名またはIPアドレス
        remote_path: リモートホスト上の保存先パス
        user: ユーザー名（指定しない場合は現在のユーザー）
        port: SSHポート番号（デフォルト: 22）
    """
    scp_command = ["scp"]

    if port != 22:
        scp_command.extend(["-P", str(port)])

    scp_command.extend(["-o", "BatchMode=yes"])  # パスワード入力を回避
    scp_command.extend(["-o", "ConnectTimeout=10"])  # 接続タイムアウト設定

    scp_command.append(local_path)

    if user:
        scp_command.append(f"{user}@{host}:{remote_path}")
    else:
        scp_command.append(f"{host}:{remote_path}")

    full_command = " ".join(scp_command)
    result = await run_command(full_command)

    if result["returncode"] != 0:
        return f"Error uploading file: {result['stderr']}"

    return f"Successfully uploaded {local_path} to {host}:{remote_path}"


@mcp.tool()
async def scp_download(host: str, remote_path: str, local_path: str, user: Optional[str] = None, port: int = 22) -> str:
    """リモートホストからファイルをダウンロードします。

    Args:
        host: 接続先ホスト名またはIPアドレス
        remote_path: リモートホスト上のファイルパス
        local_path: ローカルの保存先パス
        user: ユーザー名（指定しない場合は現在のユーザー）
        port: SSHポート番号（デフォルト: 22）
    """
    scp_command = ["scp"]

    if port != 22:
        scp_command.extend(["-P", str(port)])

    scp_command.extend(["-o", "BatchMode=yes"])  # パスワード入力を回避
    scp_command.extend(["-o", "ConnectTimeout=10"])  # 接続タイムアウト設定

    if user:
        scp_command.append(f"{user}@{host}:{remote_path}")
    else:
        scp_command.append(f"{host}:{remote_path}")

    scp_command.append(local_path)

    full_command = " ".join(scp_command)
    result = await run_command(full_command)

    if result["returncode"] != 0:
        return f"Error downloading file: {result['stderr']}"

    return f"Successfully downloaded {host}:{remote_path} to {local_path}"


@mcp.tool()
async def ssh_list_hosts() -> str:
    """~/.ssh/configから設定済みのSSHホストを一覧表示します。"""
    result = await run_command("grep '^Host ' ~/.ssh/config | sed 's/Host //'")

    if result["returncode"] != 0 or not result["stdout"]:
        return "No hosts found in SSH config or SSH config does not exist."

    hosts = result["stdout"].split("\n")
    return "\n".join(hosts)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
