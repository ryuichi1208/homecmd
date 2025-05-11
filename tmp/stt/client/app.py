from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
# from twilio.twiml.voice_response import VoiceResponse, Start, Stream
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream


import os
import json
import base64
import audioop
import wave
import datetime as dt
import pyttsx3
import io
from pydub import AudioSegment
import asyncio

NGROK_DOMAIN = "YOUR_SUBDOMAIN.ngrok.io"      # 起動後に置換

app = FastAPI()

# ① Twilio が最初に呼び出す HTTP Webhook
@app.post("/", response_class=PlainTextResponse)
async def voice_webhook():
    resp = VoiceResponse()

    start = Start()
    start.stream(
        url=f"wss://7e3b-180-23-8-113.ngrok-free.app/ws",
        track="both",
    )
    resp.append(start)

    resp.say("こんにちは。こんにちは。", voice="alice", language="ja-JP")
    resp.pause(length=600)

    return str(resp)


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    """Twilio から接続され、音声フレームを受信する WebSocket"""
    print("[INFO] WebSocket connected")
    await ws.accept()

    wav = None  # wave.Writer
    stream_sid = None
    responded = False
    try:
        while True:
            msg = await ws.receive_text()
            data = json.loads(msg)

            if data.get("event") == "start":
                print("[INFO] Stream started")
                ts = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                os.makedirs("recordings", exist_ok=True)
                path = f"recordings/call_{ts}.wav"

                wav = wave.open(path, "wb")
                wav.setnchannels(1)      # mono
                wav.setsampwidth(2)      # 16‑bit
                wav.setframerate(8000)   # 8 kHz
                stream_sid = data["streamSid"]
                print(f"[INFO] Recording → {path}")
            elif data.get("event") == "media" and wav:
                print(f"[INFO] Received media: {data['media']['payload'][:10]}...")
                ulaw_bytes = base64.b64decode(data["media"]["payload"])
                pcm16 = audioop.ulaw2lin(ulaw_bytes, 2)
                wav.writeframes(pcm16)

                if not responded and stream_sid:
                    responded = True
                    # ❸ 音声ファイルを再生する
                    print("[INFO] 1")
                    await play_wav(ws, stream_sid, "recordings/call_20250511_013638.wav")
            elif data.get("event") == "mark" and wav:
                if data["mark"]["name"] == "tts_end":
                    print("[INFO] TTS playback finished")
            elif data.get("event") == "dtmf":
                print(f"[INFO] DTMF: {data['dtmf']['digits']}")
            elif data.get("event") == "stop":
                print("[INFO] Stream stopped")
                break
            else :
                print(f"[WARN] Unknown event: {data}")

    except WebSocketDisconnect:
        print("[WARN] WebSocket disconnected unexpectedly")

    finally:
        if wav:
            wav.close()
            print("[INFO] Recording finished")


async def play_wav(ws, stream_sid: str, wav_path: str):
    """
    wav_path の音声を μ‑law 8 kHz に変換し、
    20 ms (=160 samples) ごとに Twilio へ送信する。
    """
    if not os.path.isfile(wav_path):
        raise FileNotFoundError(wav_path)

    seg = AudioSegment.from_file(wav_path)\
                      .set_frame_rate(8000)\
                      .set_sample_width(2)\
                      .set_channels(1)
    pcm = seg.raw_data                        # type: bytes

    frame_bytes = 160 * 2
    for i in range(0, len(pcm), frame_bytes):
        chunk16 = pcm[i:i + frame_bytes]
        if len(chunk16) < frame_bytes:
            break                            # 端数は無視（無音を送っても良い）

        ulaw = audioop.lin2ulaw(chunk16, 2)  # → 160 bytes
        payload = base64.b64encode(ulaw).decode()

        await ws.send_text(json.dumps({
            "event": "media",
            "streamSid": stream_sid,
            "media": {"payload": payload}
        }))
        await asyncio.sleep(0.02)            # 20 ms 間隔で送信

    await ws.send_text(json.dumps({
        "event": "mark",
        "streamSid": stream_sid,
        "mark": {"name": "wav_end"}
    }))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

