import os
import json
import sys
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

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

load_dotenv()

MODEL_NAME = "gemini-2.0-flash"
MAX_TOKENS = 1000
SLOTS_FILE = "./slots.json"


def log_json(level: str, message: str, **kwargs):
    """Outputs logs in JSON format"""
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "level": level,
        "message": message,
    }
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
            log_json(
                "ERROR",
                f"Required environment variable {var} is not set",
                variable=var,
                description=description,
            )

    if missing_vars:
        log_json(
            "CRITICAL",
            "Missing required environment variables",
            missing_variables=missing_vars,
        )
        log_json(
            "INFO",
            "Environment variables should be set in a .env file or as system environment variables.",
        )
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
        log_json(
            "INFO",
            "Connection established",
            tools=[tool.name for tool in self.available_tools],
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
        stream = p.open(
            format=sample_format,
            channels=channels,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
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
    response = client.models.generate_content(
        model="gemini-2.0-flash-001", contents=text
    )
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


@dataclass
class SlotDefinition:
    name: str
    prompt: str
    required: bool


class SlotFillingSession:
    def __init__(
        self,
        intent_name: str,
        slot_definitions_dict: List[Dict[str, Any]],
        confirmation_template: str,
    ):
        self.intent_name = intent_name
        self.slot_definitions = [SlotDefinition(**sd) for sd in slot_definitions_dict]
        self.confirmation_template = confirmation_template
        self.filled_values: Dict[str, Any] = {}
        self.current_target_slot: Optional[SlotDefinition] = None
        log_json("INFO", f"SlotFillingSession initialized for intent: {intent_name}")

    def get_next_slot_to_fill(self) -> Optional[SlotDefinition]:
        # 必須スロットを優先して探す
        for slot_def in self.slot_definitions:
            if slot_def.required and slot_def.name not in self.filled_values:
                self.current_target_slot = slot_def
                log_json("DEBUG", f"Next slot to fill (required): {slot_def.name}")
                return slot_def

        # 次に任意スロットを探す
        for slot_def in self.slot_definitions:
            if not slot_def.required and slot_def.name not in self.filled_values:
                self.current_target_slot = slot_def
                log_json("DEBUG", f"Next slot to fill (optional): {slot_def.name}")
                return slot_def

        self.current_target_slot = None
        log_json("DEBUG", "No more slots to fill.")
        return None

    def attempt_fill_current_slot(self, user_response: str) -> bool:
        if self.current_target_slot:
            slot_name = self.current_target_slot.name
            # 簡単な「なし」の処理（任意スロット用）
            if not self.current_target_slot.required and user_response.strip() in [
                "なし",
                "特にない",
                "いらない",
                "不要",
            ]:
                self.filled_values[slot_name] = (
                    None  # 明示的にNoneをセットするか、キー自体を入れないか。ここではNone
                )
                log_json("INFO", f"Optional slot '{slot_name}' skipped by user.")
            else:
                self.filled_values[slot_name] = user_response
                log_json(
                    "INFO", f"Slot '{slot_name}' filled with value: '{user_response}'"
                )

            # 埋めたのでリセット
            # self.current_target_slot = None # ここでリセットすると、is_all_slots_filled_or_attempted のロジックに影響する可能性
            return True
        log_json(
            "WARNING", "Attempted to fill slot, but no current_target_slot was set."
        )
        return False

    def is_all_slots_filled_or_attempted(self) -> bool:
        """全ての定義されたスロットが埋まっているか、試みられた（current_target_slotがNoneになった）かを確認"""
        # 全ての required スロットが埋まっていることを確認
        for slot_def in self.slot_definitions:
            if slot_def.required and slot_def.name not in self.filled_values:
                return False
        # この時点で必須スロットは全て埋まっている
        # 次にget_next_slot_to_fillを呼んだ結果がNoneなら、任意スロットも全て確認済み
        return self.get_next_slot_to_fill() is None

    def get_formatted_confirmation(self) -> str:
        message = self.confirmation_template
        # プレースホルダーの置換と、値がない場合の処理
        for slot_def in self.slot_definitions:
            placeholder = f"{{{slot_def.name}}}"
            value = self.filled_values.get(slot_def.name)
            if value is not None:
                message = message.replace(placeholder, str(value))
            else:
                # 値がNoneまたは存在しない場合、プレースホルダを空文字にするか、文脈に応じた文字列に。
                # 例えば「{duration}の」のような部分が「の」だけ残らないように注意が必要。
                # 簡単のため、ここでは値がない場合は「(指定なし)」とするか、プレースホルダ自体を削除。
                # 今回は、slot値がNoneなら「(指定なし)」に。
                message = message.replace(placeholder, "(指定なし)")
        return message


def load_slot_definitions(file_path: str) -> Dict[str, Dict[str, Any]]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            definitions = json.load(f)
            log_json(
                "INFO", "Slot definitions loaded successfully.", file_path=file_path
            )
            return definitions
    except FileNotFoundError:
        log_json("ERROR", "Slot definitions file not found.", file_path=file_path)
        return {}
    except json.JSONDecodeError as e:
        log_json(
            "ERROR",
            "Failed to decode slot definitions JSON.",
            file_path=file_path,
            error=str(e),
        )
        return {}
    except Exception as e:
        log_json(
            "ERROR",
            "An unexpected error occurred while loading slot definitions.",
            file_path=file_path,
            error=str(e),
        )
        return {}


class GeminiLLM:
    def __init__(self, token: str):
        if not token:
            raise ValueError("API key is required")
        self.token = token
        self.client = genai.Client(api_key=self.token)
        self.context = ""

    def generate_content(self, text: str) -> str:
        """Generate content using Gemini LLM while maintaining conversation context."""
        if not text:
            raise ValueError("Text is required")

        # Add the new user input to the context
        self.context += f"User: {text}\n"

        print("Current context:", self.context)

        # Generate response based on the updated context
        response = self.client.models.generate_content(
            model="gemini-2.0-flash-001", contents=self.context
        )

        # Get the response and add it to the context
        response_text = response.text
        self.context += f"AI: {response_text}\n"

        return response_text


async def llm_loop():
    """Main loop for LLM interaction"""
    model = whisper.load_model("medium")
    gemini = GeminiLLM(token=os.getenv("GEMINI_API_KEY"))
    first_time = True
    while True:
        input_file = None
        try:
            if first_time:
                first_time = False
                read_text("音声を入力してください", rate=180, volume=0.9)

            play_audio("data/piron.mp3", "mp3")

            input_file = record_audio()
            if input_file is None:
                log_json("ERROR", "Audio recording failed. Skipping this iteration.")
                read_text(
                    "録音に失敗しました。もう一度お試しください。", rate=180, volume=0.9
                )
                continue

            start_time = time.time()
            result = model.transcribe(input_file, fp16=False)
            end_time = time.time()
            transcribed_text = result["text"].strip()
            log_json(
                "INFO",
                "Transcription completed",
                text=transcribed_text,
                execution_time=end_time - start_time,
            )
            response = gemini.generate_content(transcribed_text)
            read_text(response)
            print(f"AI: {response}")
        except KeyboardInterrupt:
            print("\nExiting LLM loop.")
            break
        except Exception as e:
            log_json("ERROR", "An error occurred in the LLM loop", error=str(e))
            print("An error occurred. Please try again.")


async def main(args: Sequence[str]):
    # Check environment variables at the start
    if not check_environment_variables():
        log_json("CRITICAL", "Exiting due to missing required environment variables.")
        sys.exit(1)

    # Load slot definitions
    slot_definitions_by_intent = load_slot_definitions(SLOTS_FILE)
    if not slot_definitions_by_intent:
        log_json(
            "WARNING", "No slot definitions loaded. Slot filling will be unavailable."
        )

    # Load the Whisper model
    model = whisper.load_model("medium")
    client = MCPClient()

    active_slot_filling_session: Optional[SlotFillingSession] = None

    try:
        if len(args) < 2:
            await llm_loop()
            return

        log_json("INFO", "Connecting to server")
        await client.connect_to_server(sys.argv[1])

        first_time = True
        while True:
            input_file = None
            try:
                if first_time:
                    first_time = False
                    read_text("音声を入力してください", rate=180, volume=0.9)

                play_audio("data/piron.mp3", "mp3")

                input_file = record_audio()
                if input_file is None:
                    log_json(
                        "ERROR", "Audio recording failed. Skipping this iteration."
                    )
                    read_text(
                        "録音に失敗しました。もう一度お試しください。",
                        rate=180,
                        volume=0.9,
                    )
                    continue

                start_time = time.time()
                result = model.transcribe(input_file, fp16=False)
                end_time = time.time()
                transcribed_text = result["text"].strip()
                log_json(
                    "INFO",
                    "Transcription completed",
                    text=transcribed_text,
                    execution_time=end_time - start_time,
                )
                read_text(transcribed_text)

                end_words = ["終了", "おわり", "お疲れ様でした"]
                if transcribed_text in end_words:
                    log_json("INFO", "Exit command detected.")
                    read_text("終了します。")
                    break

                # --- Slot Filling Logic --- START ---
                if active_slot_filling_session:
                    # スロットフィリングセッションがアクティブな場合
                    if active_slot_filling_session.current_target_slot:
                        active_slot_filling_session.attempt_fill_current_slot(
                            transcribed_text
                        )
                        # current_target_slot は attempt_fill_current_slot の中で None にはしない。
                        # 次の質問は get_next_slot_to_fill で決定する。
                    else:
                        # 通常ここには来ないはず。来た場合は警告ログ。
                        log_json(
                            "WARNING",
                            "active_slot_filling_session is active, but current_target_slot is None before getting next slot.",
                        )

                    next_slot_def = active_slot_filling_session.get_next_slot_to_fill()
                    if next_slot_def:
                        # 次に埋めるべきスロットがある場合
                        read_text(next_slot_def.prompt)
                    else:
                        # 全てのスロットが埋まった（または試みられた）場合
                        confirmation_message = (
                            active_slot_filling_session.get_formatted_confirmation()
                        )
                        read_text(confirmation_message)
                        log_json(
                            "INFO",
                            "Slot filling completed.",
                            intent=active_slot_filling_session.intent_name,
                            slots=active_slot_filling_session.filled_values,
                        )

                        # MCPに送信するペイロードを作成
                        payload = {
                            "intent": active_slot_filling_session.intent_name,
                            "slots": active_slot_filling_session.filled_values,
                        }
                        # process_queryは文字列を期待するのでjson.dumpsする
                        response_from_mcp = await client.process_query(
                            json.dumps(payload, ensure_ascii=False)
                        )
                        log_json(
                            "INFO",
                            "Response from MCP after slot filling",
                            response=response_from_mcp,
                        )
                        read_text(response_from_mcp)
                        active_slot_filling_session = None  # セッション終了

                else:
                    # スロットフィリングセッションがアクティブでない場合、インテントを判定
                    # (簡易的なキーワードベースのインテント判定)
                    intent_to_start = None
                    if (
                        "旅行" in transcribed_text
                        and (
                            "予約" in transcribed_text or "行きたい" in transcribed_text
                        )
                        and "travel_booking" in slot_definitions_by_intent
                    ):
                        intent_to_start = "travel_booking"
                    elif (
                        ("レストラン" in transcribed_text or "食事" in transcribed_text)
                        and "予約" in transcribed_text
                        and "restaurant_booking" in slot_definitions_by_intent
                    ):
                        intent_to_start = "restaurant_booking"
                    # 他のインテント判定を追加可能

                    if intent_to_start and slot_definitions_by_intent.get(
                        intent_to_start
                    ):
                        intent_config = slot_definitions_by_intent[intent_to_start]
                        active_slot_filling_session = SlotFillingSession(
                            intent_name=intent_to_start,
                            slot_definitions_dict=intent_config["slots"],
                            confirmation_template=intent_config["confirmation_message"],
                        )
                        log_json(
                            "INFO",
                            f"Starting slot filling session for intent: {intent_to_start}",
                        )
                        first_slot_to_fill = (
                            active_slot_filling_session.get_next_slot_to_fill()
                        )
                        if first_slot_to_fill:
                            read_text(first_slot_to_fill.prompt)
                        else:
                            log_json(
                                "WARNING",
                                f"No slots to fill for intent '{intent_to_start}', though session started.",
                            )
                            read_text(
                                "情報を伺いたいのですが、うまく始められませんでした。"
                            )
                            active_slot_filling_session = None  # 開始失敗
                    else:
                        # スロットフィリングを開始しない通常の会話
                        log_json(
                            "INFO",
                            "No slot filling intent detected, processing as normal query.",
                        )
                        response = await client.process_query(transcribed_text)
                        log_json(
                            "INFO",
                            "Response received (normal query)",
                            response=response,
                        )
                        read_text(response)
                # --- Slot Filling Logic --- END ---

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
