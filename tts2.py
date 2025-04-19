from io import BytesIO
import os
import asyncio
import time
import wave
from dotenv import load_dotenv
import pyaudio
import boto3
from botocore.exceptions import ClientError
import tempfile

load_dotenv()

class PollyClient:
    def __init__(self, region=None, voice_id='Zhiyu', output_format='pcm', speech_rate='130%'):
        """
        
        Args:
            region (_type_, optional): _description_. Defaults to None.
            voice_id (str, optional): _description_. Defaults to 'Zhiyu'.
            output_format (str, optional): _description_. Defaults to 'mp3'.
            speech_rate (str, optional): _description_. Defaults to 'medium'. 可為 'x-slow', 'slow', 'medium', 'fast', 'x-fast' 或百分比如 '120%'
        """
        self.region = region or os.getenv("AWS_REGION")
        self.polly_client = boto3.client("polly", region_name=self.region)
        self.output_format = output_format 
        self.voice_id = voice_id
        self.speech_rate = str(speech_rate) if '%' in str(speech_rate) else f"{speech_rate}%"
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.stop_event = asyncio.Event()
        
    async def synthesize_speech(self, text, rate=None, stop_check=None):
        """
        合成並播放語音
        
        Args:
            text: 要播放的文字
            rate: 語音速率
            stop_check: 一個可等待的對象，用於檢查是否需要停止播放
        """
        try:
            # 重置停止事件
            self.stop_event.clear()
            
            speech_rate = rate or self.speech_rate
            
            ssml_text = f"""
            <speak>
                <prosody rate="{speech_rate}">
                    {text}
                </prosody>
            </speak>
            """
            
            response = self.polly_client.synthesize_speech(
                Engine='neural',
                LanguageCode='cmn-CN',
                OutputFormat=self.output_format,
                Text=ssml_text,
                TextType='ssml',
                VoiceId=self.voice_id
            )
            
            if "AudioStream" in response:
                audio_data = response['AudioStream'].read()
                
                # 建立 PyAudio 串流
                self.stream = self.p.open(
                    format=self.p.get_format_from_width(2),  # 16-bit PCM
                    channels=1,
                    rate=16000,  # Amazon Polly 默認採樣率
                    output=True
                )
                
                # 將音訊數據分成多個塊來播放，這樣我們可以檢查是否需要停止
                chunk_size = 4096  # 可以調整塊大小
                for i in range(0, len(audio_data), chunk_size):
                    # 檢查是否設置了停止事件
                    if self.stop_event.is_set():
                        print("\n語音播放被中斷")
                        break
                    
                    # 如果提供了外部停止檢查，也檢查它
                    if stop_check and stop_check.is_set():
                        print("\n檢測到用戶插話，停止播放")
                        break
                        
                    # 播放當前塊
                    chunk = audio_data[i:i+chunk_size]
                    self.stream.write(chunk)
                    
                    # 為其他協程讓出控制權
                    await asyncio.sleep(0)

                # 停止並關閉流
                self.stop_stream()

        except ClientError as e:
            print(f"Error synthesizing speech: {e}")
            return None
    
    def stop_stream(self):
        """停止當前的音訊流"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
    def stop_playback(self):
        """設置停止事件來中斷播放"""
        self.stop_event.set()
        
    def __del__(self):
        if hasattr(self, 'p'):
            self.p.terminate()
        
async def main():
    tts = PollyClient()
    await tts.synthesize_speech("你好，我是 Polly 的語音合成服務。")
    
if __name__ == "__main__":
    asyncio.run(main())