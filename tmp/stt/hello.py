import os
import json
import sys
import asyncio
import time
import whisper
import pyttsx3
import pyaudio
import wave
from google import genai
from google.genai import types

from collections.abc import Sequence
from contextlib import AsyncExitStack
from anthropic import Anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, stdio_client
from openai import OpenAI

load_dotenv()

MODEL_NAME = "gemini-2.0-flash"
MAX_TOKENS = 1000

class MCPClient:
    def __init__(self):
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.openai = OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/",
        )

    async def connect_to_server(self, server_script_path: str):
        if not server_script_path.endswith(".py"):
            raise ValueError("Server script must be a .py file.")

        command = "python"
        server_params = StdioServerParameters(
            command=command, args=[server_script_path], env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()

        response = await self.session.list_tools()
        self.available_tools = response.tools
        print()
        print(
            "Connection to server with tools:",
            [tool.name for tool in self.available_tools],
        )

    async def process_query(self, query: str) -> str:
        messages = [{"role": "user", "content": query}]
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for tool in self.available_tools
        ]

        response = self.openai.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=MAX_TOKENS,
            messages=messages,
            tools=available_tools,
        )

        message = response.choices[0].message
        if not message.tool_calls:
            return message.content

        final_text = []
        messages.append(message)
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_call_id = tool_call.id

            tool_args = json.loads(tool_call.function.arguments)
            tool_result = await self.session.call_tool(tool_name, tool_args)
            tool_result_contents = [
                content.model_dump() for content in tool_result.content
            ]
            final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": tool_name,
                    "content": tool_result_contents,
                }
            )

            response = self.openai.chat.completions.create(
                model=MODEL_NAME,
                max_tokens=MAX_TOKENS,
                messages=messages,
                tools=available_tools,
            )
            final_text.append(response.choices[0].message.content)

        return "\n".join(final_text)

    async def cleanup(self):
        await self.exit_stack.aclose()


def record_audio(sample_format: int = pyaudio.paInt16, channels: int = 1) -> str:
    """Record audio from the microphone and save it to a WAV file
    """
    RATE = 44100
    CHUNK = 1024
    TIME = 5

    p = pyaudio.PyAudio()

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

    print("[INFO] start recording")

    frames = []

    # 録音データを集める
    for i in range(0, int(RATE / CHUNK * TIME)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("[INFO] stop recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    datetime = time.strftime("%Y%m%d_%H%M%S")
    filename = f"record_{datetime}.wav"

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print("[INFO] recording finished: " + filename)

    return filename


def read_text(text: str, rate: int = 200, volume: float = 1.0):
    """Read text using pyttsx3
    """
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)
    engine.say(text)
    engine.runAndWait()
    engine.stop()


def gemini_llm(text: str, token: str) -> str:
    """Generate content using Gemini LLM
    """
    if not token:
        raise ValueError("API key is required")
    if not text:
        raise ValueError("Text is required")

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model='gemini-2.0-flash-001', contents=text
    )
    return response.text


async def main(args: Sequence[str]):
    input_file = None
    try:
        # Load the Whisper model
        model = whisper.load_model("medium")

        # Record audio
        input_file = record_audio()
        start_time = time.time()
        result = model.transcribe(input_file, fp16=False)
        end_time = time.time()
        print(f'[INFO] input {result["text"]}')
        print(f'[INFO] exec: {end_time - start_time} seconds')

        # Read the transcribed text
        read_text(result["text"])

        # Generate content using Gemini LLM
        # res = gemini_llm(result["text"], api_key=os.getenv("GEMINI_API_KEY"))

        try:
            client = MCPClient()
            print("[INFO] connect to server")
            await client.connect_to_server(sys.argv[1])
            print("[INFO] process query")
            response = await client.process_query(result["text"])
            print(response)
            read_text(response)
        finally:
            await client.cleanup()
    finally:
        if input_file and os.path.exists(input_file):
            print("[INFO] delete file")
            os.remove(input_file)
        else:
            print("[INFO] no file to delete")


if __name__ == "__main__":
    print("[INFO] start script")
    asyncio.run(main(sys.argv))
    print("[INFO] end script")
