from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse, Start, Stream

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

    # Media Stream を開始
    start = Start()
    start.stream(
        url=f"wss://fc1f-180-23-8-113.ngrok-free.app/ws",  # WebSocket 先
        track="inbound"                  # 片方向ストリーム（受信のみ）
    )
    resp.append(start)

    # 呼び出し元にガイダンスを流す
    resp.say("こんにちは。ストリーミングを開始しました。お話しください。")
    resp.pause(length=600)

    return str(resp)  # TwiML をそのまま返す


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    """Twilio から接続され、音声フレームを受信する WebSocket"""
    await ws.accept()

    wav = None  # wave.Writer
    stream_sid = None
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
                # base64 → μ‑law バイト列
                ulaw_bytes = base64.b64decode(data["media"]["payload"])
                # μ‑law → 16‑bit リニア PCM
                pcm16 = audioop.ulaw2lin(ulaw_bytes, 2)
                wav.writeframes(pcm16)

                await speak_text(ws, stream_sid, "入力ありがとうございました。")
            elif data.get("event") == "mark" and wav:
                # 再生完了マーク
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


async def speak_text(ws: WebSocket, stream_sid: str, text: str):
    # 1) TTS → WAV (16 kHz / 16‑bit)
    engine = pyttsx3.init()
    buf = io.BytesIO()
    engine.save_to_file(text, buf)
    engine.runAndWait()
    buf.seek(0)
    wav = AudioSegment.from_file(buf, format="wav")

    # 2) 8 kHz mono 16‑bit PCM
    pcm = wav.set_frame_rate(8000).set_sample_width(2).set_channels(1).raw_data

    # 3) 20 ms (=160 samples) ごとに μ‑law 変換して送信
    slice_bytes = 160 * 2
    for i in range(0, len(pcm), slice_bytes):
        chunk16 = pcm[i:i + slice_bytes]
        if len(chunk16) < slice_bytes:
            break
        ulaw = audioop.lin2ulaw(chunk16, 2)
        payload = base64.b64encode(ulaw).decode()
        await ws.send_text(json.dumps({
            "event": "media",
            "streamSid": stream_sid,
            "media": {"payload": payload}
        }))
        await asyncio.sleep(0.02)

    # (任意) 再生完了マーク
    await ws.send_text(json.dumps({
        "event": "mark",
        "streamSid": stream_sid,
        "mark": {"name": "tts_end"}
    }))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
