import asyncio
import sys
import hello


if __name__ == "__main__":
    try:
        hello.log_json("INFO", "Starting script")
        asyncio.run(hello.main(sys.argv))
    except Exception as e:
        # Catch any unexpected errors during script execution not caught in main
        hello.log_json(
            "CRITICAL", "Unhandled exception occurred at top level", error=str(e)
        )
    finally:
        hello.log_json("INFO", "Script finished")
