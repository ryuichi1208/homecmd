import asyncio

def hello(name: str) -> str:
    return f"Hello, {name}!"

async def async_hello(name):
    return f"Hello, {name}!"

async def main():
    res1 = hello("World")
    print(res1)
    res2 = await async_hello("World")
    print(res2)
    res3 = async_hello("World")
    print(res3)
    res4 = await res3
    print(res4)

if __name__ == "__main__":
    asyncio.run(main())
