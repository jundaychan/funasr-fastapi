import ssl,websockets
import uuid
import wave
import asyncio
import json

from config import *


r = REDIS_CLIENT

async def asr_client(task_id,wav):
    # url = "ws://127.0.0.1:20002"
    url = "wss://{}:{}".format(ASR_HOST, ASR_PORT)
    ssl_context = ssl.SSLContext()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with websockets.connect(url, subprotocols=["binary"], ping_interval=None,ssl=ssl_context) as websocket:
        wav_path = wav
        with wave.open(wav_path, "rb") as wav_file:
            params = wav_file.getparams()
            sample_rate = wav_file.getframerate()
            frames = wav_file.readframes(wav_file.getnframes())
            audio_bytes = bytes(frames)

        message = json.dumps ({"mode": "offline", "chunk_size": [5, 10, 5], "chunk_interval": 0, "audio_fs": sample_rate, "wav_name": "demo", "is_speaking": True, "hotwords": "", "itn": True})
        await websocket.send(message)
        # 分包发送
        chunk_interval = 10
        chunk_size = 10
        stride = int(60 * chunk_size / chunk_interval / 1000 * 16000 * 2)
        chunk_num = (len(audio_bytes) - 1) // stride + 1
        print("chunk_num :{}".format(chunk_num))
        print("stride :{}".format(stride))
        for i in range(chunk_num):
            beg = i * stride
            data = audio_bytes[beg:beg + stride]
            message = data
            await websocket.send(message)
            # 传输结束
            if i == chunk_num - 1:
                is_speaking = False
                message = json.dumps({"is_speaking": is_speaking})
                await websocket.send(message)
            await asyncio.sleep(0.001)
        response = await websocket.recv()
        print(f"Received: {response}")
        r.set(task_id, response, ex=3600)  # 键在 1 小时后自动过期




def voice2text(task_id,wav):
    asyncio.get_event_loop().run_until_complete(asr_client(task_id, wav))
    return {"task_id": task_id, "audio_url": wav}



if __name__ == '__main__':
    import time
    task_id = str(uuid.uuid4())
    r.set(task_id, "正在处理中")  # 设置任务状态

    time_start=time.time()
    paths = ["7326135214235798284.mp3","vad_example.wav"]
    z = voice2text(wav=paths[-1],task_id=task_id)
    print(z)
    text = r.get(z['task_id'])
    print(text)
    # voice2text(wavs=paths)
    time_end=time.time()

    print('time cost',time_end-time_start,'s')
