# -*- coding: utf-8 -*-

import ssl,websockets
import wave
import asyncio
import json
from io import BytesIO

import requests

from app.celery_config import celery_app
from app.config import *


r = REDIS_CLIENT

async def asr_client(task_id,wav_url):
    # url = "ws://127.0.0.1:20002"
    url = "wss://{}:{}".format(ASR_HOST, ASR_PORT)
    ssl_context = ssl.SSLContext()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with websockets.connect(url, subprotocols=["binary"], ping_interval=None,ssl=ssl_context) as websocket:
        # 根据url地址下载音频文件
        try:

            file_type = wav_url.split('.')[-1]
            wav_path = None
            if wav_url.startswith('http://') or wav_url.startswith('https://'):
                response = requests.get(wav_url)
                response.raise_for_status()
                wav_data = BytesIO(response.content)
                if not response.content.startswith(b'RIFF'):
                    # 将音频文件保存到本地
                    wav_path = f'{task_id}.mp3'

                    with open(wav_path, 'wb') as f:
                        f.write(response.content)
                else:
                    # 将音频文件保存到本地
                    wav_path = f'{task_id}.wav'

                    with open(wav_path, 'wb') as f:
                        f.write(response.content)
            else:
                r.set(task_id, "任务失败,格式错误", ex=3600)  # 键在 1 小时后自动过期
                raise ValueError("文件不是有效的WAV格式")

            sample_rate = 16000
            if file_type == 'wav':
                wav_format = "wav"
                with wave.open(wav_path, "rb") as wav_file:
                    sample_rate = wav_file.getframerate()
                    frames = wav_file.readframes(wav_file.getnframes())
                    audio_bytes = bytes(frames)
            else:
                wav_format = "others"

                with open(wav_path, "rb") as f:
                    audio_bytes = f.read()

            message = json.dumps ({"mode": "offline", "chunk_size": [5, 10, 5], "chunk_interval": 0,  "wav_format": wav_format, "audio_fs": sample_rate, "wav_name": "demo", "is_speaking": True, "hotwords": "", "itn": True})
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
            r.set(task_id, response, ex=3600)  # 键在 1 小时后自动过期
        except:
            r.set(task_id, "任务失败", ex=3600)
        finally:
            if wav_path and os.path.exists(wav_path):
                os.remove(wav_path)




@celery_app.task(name='app.asr_client.voice2text')
def voice2text(task_id, wav):
    asyncio.run(asr_client(task_id, wav))


