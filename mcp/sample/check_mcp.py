#!/usr/bin/env python3

try:
    import mcp

    print(f"MCP module found at: {mcp.__file__}")
    print(f"MCP module contents: {dir(mcp)}")

    # Check for fastmcp directly
    try:
        from mcp import fastmcp

        print(f"FastMCP found directly in mcp: {dir(fastmcp)}")
    except ImportError:
        print("FastMCP not found directly in mcp")

    # Check server module
    try:
        from mcp import server

        print(f"Server module found: {dir(server)}")

        try:
            from mcp.server import fastmcp

            print(f"FastMCP module found in server: {dir(fastmcp)}")
        except ImportError:
            print("FastMCP not found in mcp.server")
    except ImportError:
        print("Server module not found in mcp")

    # Check all submodules
    print("\nAll available submodules:")
    import pkgutil

    for loader, name, is_pkg in pkgutil.iter_modules(mcp.__path__, mcp.__name__ + "."):
        print(name)

except ImportError as e:
    print(f"Error importing MCP: {e}")
