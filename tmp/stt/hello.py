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
import datetime

from collections.abc import Sequence
from contextlib import AsyncExitStack
from anthropic import Anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, stdio_client
from openai import OpenAI

load_dotenv()

MODEL_NAME = "gemini-2.0-flash"
MAX_TOKENS = 1000


def log_json(level: str, message: str, **kwargs):
    """Outputs logs in JSON format"""
    log_entry = {"timestamp": datetime.datetime.now().isoformat(), "level": level, "message": message}
    if kwargs:
        log_entry.update(kwargs)
    print(json.dumps(log_entry, ensure_ascii=False))


def check_environment_variables():
    """Check if required environment variables are set."""
    required_vars = {
        "GEMINI_API_KEY": "API key for Gemini API"
        # Add other required variables here if needed
    }

    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(var)
            log_json("ERROR", f"Required environment variable {var} is not set", variable=var, description=description)

    if missing_vars:
        log_json("CRITICAL", "Missing required environment variables", missing_variables=missing_vars)
        log_json("INFO", "Environment variables should be set in a .env file or as system environment variables.")
        return False

    log_json("INFO", "Environment variable check passed.", status="success")
    return True


class MCPClient:
    def __init__(self, command: str = None):
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.openai = OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/",
        )
        self.command = command

    async def connect_to_server(self, server_script_path: str):
        if not server_script_path.endswith(".py"):
            raise ValueError("Server script must be a .py file.")

        command = self.command or sys.executable
        server_params = StdioServerParameters(command=command, args=[server_script_path], env=None)

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        self.available_tools = response.tools
        log_json("INFO", "Connection established", tools=[tool.name for tool in self.available_tools])

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
            tool_result_contents = [content.model_dump() for content in tool_result.content]
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
    """Record audio from the microphone and save it to a WAV file"""
    RATE = 44100
    CHUNK = 1024
    TIME = 5

    p = None
    stream = None
    frames = []
    filename = None

    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=sample_format, channels=channels, rate=RATE, input=True, frames_per_buffer=CHUNK)
        log_json("INFO", "Start recording")
    except Exception as e:
        log_json("ERROR", "Failed to open audio stream", error=str(e))
        if stream:
            stream.stop_stream()
            stream.close()
        if p:
            p.terminate()
        return None

    frames = []

    # Collect recording data
    for i in range(0, int(RATE / CHUNK * TIME)):
        data = stream.read(CHUNK)
        frames.append(data)

    log_json("INFO", "Stop recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"record_{timestamp}.wav"

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))

    log_json("INFO", "Recording finished", filename=filename)

    return filename


def read_text(text: str, rate: int = 200, volume: float = 1.0):
    """Read text using pyttsx3"""
    if not text:
        log_json("WARNING", "Text to read is empty")
        return

    engine = None
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", rate)
        engine.setProperty("volume", volume)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        log_json("ERROR", "Failed to read text", error=str(e))
    finally:
        if engine:
            try:
                engine.stop()
            except Exception as e:
                log_json("WARNING", "Failed to stop TTS engine", error=str(e))


def gemini_llm(text: str, token: str) -> str:
    """Generate content using Gemini LLM"""
    if not token:
        raise ValueError("API key is required")
    if not text:
        raise ValueError("Text is required")

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(model="gemini-2.0-flash-001", contents=text)
    return response.text


def play_audio(file_path: str, file_type: str = "wav"):
    """Play audio file using pyaudio"""
    if not os.path.exists(file_path):
        log_json("ERROR", "Audio file does not exist", file_path=file_path)
        return

    if file_type not in ["wav", "mp3"]:
        log_json("ERROR", "Unsupported audio file type", file_type=file_type)
        return

    if file_type == "mp3":
        import pydub
        from pydub.playback import play

        audio = pydub.AudioSegment.from_mp3(file_path)
        play(audio)
        log_json("INFO", "Playing audio", file_path=file_path)
        log_json("INFO", "Audio playback finished")
    elif file_type == "wav":
        import wave
        import pyaudio

        chunk = 1024
        wf = wave.open(file_path, "rb")
        p = pyaudio.PyAudio()
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
        )

        data = wf.readframes(chunk)
        while data:
            stream.write(data)
            data = wf.readframes(chunk)

        stream.stop_stream()
        stream.close()
        p.terminate()


async def main(args: Sequence[str]):
    # Check environment variables at the start
    if not check_environment_variables():
        log_json("CRITICAL", "Exiting due to missing required environment variables.")
        sys.exit(1)  # Exit if critical variables are missing

    # Load the Whisper model
    model = whisper.load_model("medium")
    client = MCPClient()  # MCPClientをループの外で初期化

    try:
        if len(args) < 2:
            error_msg = "Server script path is not specified"
            log_json("ERROR", error_msg)
            log_json("INFO", "Usage: python hello.py <server_script.py>")
            return  # Exit gracefully if usage is incorrect

        log_json("INFO", "Connecting to server")
        await client.connect_to_server(sys.argv[1])  # サーバーへの接続もループの外

        while True:  # 会話ループを開始
            input_file = None
            try:
                # Record audio
                read_text("音声を入力してください", rate=180, volume=0.9)
                play_audio("data/piron.mp3", "mp3")
                input_file = record_audio()
                if input_file is None:  # record_audioが失敗した場合
                    log_json("ERROR", "Audio recording failed. Skipping this iteration.")
                    read_text("録音に失敗しました。もう一度お試しください。", rate=180, volume=0.9)
                    continue

                start_time = time.time()
                result = model.transcribe(input_file, fp16=False)
                end_time = time.time()
                transcribed_text = result["text"].strip()
                log_json("INFO", "Transcription completed", text=transcribed_text, execution_time=end_time - start_time)

                # Read the transcribed text
                read_text(transcribed_text)

                end_words = ["終了", "おわり", "お疲れ様でした"]
                if transcribed_text in end_words:
                    log_json("INFO", "Exit command detected.")
                    read_text("終了します。")
                    break  # ループを抜ける

                # if you want to use Gemini LLM, uncomment the following line
                # Generate content using Gemini LLM
                # res = gemini_llm(result["text"], api_key=os.getenv("GEMINI_API_KEY"))

                log_json("INFO", "Processing query")
                response = await client.process_query(transcribed_text)
                log_json("INFO", "Response received", response=response)
                read_text(response)

            except KeyboardInterrupt:
                log_json("INFO", "Keyboard interrupt detected. Exiting loop.")
                read_text("中断しました。")
                break
            except Exception as e:
                log_json("ERROR", "An error occurred in the main loop", error=str(e))
                read_text("エラーが発生しました。処理を続行します。")
            finally:
                if input_file and os.path.exists(input_file):
                    log_json("INFO", "Deleting temporary file", file=input_file)
                    os.remove(input_file)
                # else: # input_fileがNoneの場合や存在しない場合のログは冗長なので削除
                #    log_json("INFO", "No file to delete or already deleted")

    except Exception as e:  # main関数レベルでの予期せぬエラー
        log_json("CRITICAL", "An unhandled exception occurred in main", error=str(e))
        read_text("重大なエラーが発生しました。スクリプトを終了します。")
    finally:
        if client.session:  # client.sessionが存在する場合のみクリーンアップ
            log_json("INFO", "Cleaning up MCP client.")
            await client.cleanup()
        log_json("INFO", "Main function finished.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        log_json("ERROR", "Server script path is not specified")
        log_json("INFO", "Usage: python hello.py <server_script.py>")
        sys.exit(1)

    try:
        log_json("INFO", "Starting script")
        asyncio.run(main(sys.argv))
    except Exception as e:
        # Catch any unexpected errors during script execution not caught in main
        log_json("CRITICAL", "Unhandled exception occurred at top level", error=str(e))
    finally:
        log_json("INFO", "Script finished")
