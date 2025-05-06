import httpx
import os
import asyncio
import pytest


class Mackerel:
    endpoint = "https://api.mackerelio.com/api/v0"

    def __init__(self, token: str):
        self.token = token

    async def get_hosts(self):
        url = f"{self.endpoint}/hosts"
        headers = {
            "X-Api-Key": self.token,
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
        return response.json()

    @staticmethod
    def print_json(data):
        import json
        print(json.dumps(data, indent=2))


async def main():
    token = os.getenv("MACKEREL_API_KEY")
    if not token:
        raise ValueError("MACKEREL_API_KEY environment variable is not set")
    mackerel = Mackerel(token)
    hosts = await mackerel.get_hosts()
    Mackerel.print_json(hosts)

def yield_hello():
    yield


if __name__ == "__main__":
    asyncio.run(main())


