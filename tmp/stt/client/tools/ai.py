import asyncio
from pydantic_ai import Agent
from pydantic import BaseModel, field_validator
import os
import httpx
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_vertex import GoogleVertexProvider

import logfire

os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = 'http://localhost:4318'
logfire.configure(send_to_logfire=False, service_name="pydantic-ai-gemini")
logfire.instrument_pydantic_ai()
logfire.instrument_httpx(capture_all=True)


async def chat(msg: str, history) -> str:
    """Chat with the agent"""
    model = GeminiModel(
        'gemini-2.0-flash',
        fallback_on=httpx.ReadTimeout,
    )
    agent = Agent(
        model=model,
        system_prompt=("あなたは平成のギャルです。ギャルのように振る舞ってください"),
    )

    try:
        result = await agent.run(msg, message_history=history, model_settings={'timeout': 0.5})
    except httpx.ReadTimeout as e:
        # タイムアウトエラーが発生した場合、エージェントの応答を取得
        result = await agent.run(msg, message_history=history, model_settings={'timeout': 5})
    return result


async def main() -> None:
    result = None
    while True:
        # 標準入力からメッセージを取得
        msg = input("メッセージを入力してください: ")
        # エージェントとチャット
        result = await chat(msg, history=result.new_messages() if result else None)
        # 結果を表示
        print(f"エージェントの応答: {result.output}")


if __name__ == "__main__":
    asyncio.run(main())

