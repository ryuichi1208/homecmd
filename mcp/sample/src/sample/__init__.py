from . import server
from . import ssh_server
import asyncio


def main():
    """Main entry point for the package."""
    asyncio.run(server.main())


def ssh_main():
    """SSH server entry point for the package."""
    asyncio.run(ssh_server.main())


# Optionally expose other important items at package level
__all__ = ["main", "server", "ssh_main", "ssh_server"]
