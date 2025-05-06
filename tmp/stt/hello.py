import time
import whisper
import pyttsx3
import pyaudio
import wave


def record_audio(sample_format: int = pyaudio.paInt16, channels: int = 1) -> str:
    RATE = 44100
    CHUNK = 1024
    TIME = 5

    p = pyaudio.PyAudio()

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=RATE,
                    input=True,
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
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)
    engine.say(text)
    engine.runAndWait()


def main():
    model = whisper.load_model("medium")
    input_file = record_audio()
    
    start_time = time.time()
    result = model.transcribe(input_file, fp16=False)
    end_time = time.time()
    print(result["text"])
    print(f'exec: {end_time - start_time} seconds')
    read_text(result["text"])


if __name__ == "__main__":
    print("[INFO] start script")
    main()
    print("[INFO] end script")
