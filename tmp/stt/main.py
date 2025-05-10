import asyncio
import sys
import hello
from logger import log_json


if __name__ == "__main__":
    try:
        log_json("INFO", "Starting script")
        asyncio.run(hello.main(sys.argv))
    except Exception as e:
        # Catch any unexpected errors during script execution not caught in main
        log_json(
            "CRITICAL", "Unhandled exception occurred at top level", error=str(e)
        )
    finally:
        log_json("INFO", "Script finished")
