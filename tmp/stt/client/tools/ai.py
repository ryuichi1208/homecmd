import asyncio
from pydantic_ai import Agent
from pydantic import BaseModel, field_validator

class AI():
    def __init__(self, agent: Agent):
        self.agent = agent
        self.history = []

class Sample(BaseModel):
    name: str
    age: int

    @field_validator('name')
    def name_must_be_alphabet(cls, v):
        print("OK", v)
        if not v.isalpha():
            raise ValueError("名前はアルファベットでなければなりません")
        return v


async def chat(msg: str, history) -> str:
    """Chat with the agent"""
    agent = Agent(
        "gemini-1.5-flash",
        system_prompt=("あなたは平成のギャルです。ギャルのように振る舞ってください"),
    )

    result = await agent.run(msg, message_history=history)
    return result


async def main() -> None:
    #result = None
    #while True:
    #    # 標準入力からメッセージを取得
    #    msg = input("メッセージを入力してください: ")
    #    # エージェントとチャット
    #    result = await chat(msg, history=result.new_messages() if result else None)
    #    # 結果を表示
    #    print(f"エージェントの応答: {result.output}")

    agent = AI(
        agent=Agent(
            "gemini-1.5-flash",
            system_prompt=("あなたは平成のギャルです。ギャルのように振る舞ってください"),
        )
    )

    res = await agent.agent.run(
        "あなたは平成のギャルです。ギャルのように振る舞ってください",
        message_history=None
    )
    print(res.output)


if __name__ == "__main__":
    asyncio.run(main())

    sample = Sample(name="John", age=30)
    sample = Sample(name="あなた", age=30)
