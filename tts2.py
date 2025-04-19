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
        
    async def synthesize_speech(self, text, rate=None):
        try:
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
                stream = self.p.open(
                    format=self.p.get_format_from_width(2),  # 16-bit PCM
                    channels=1,
                    rate=16000,  # Amazon Polly 默認採樣率
                    output=True
                )
                
                # 播放音訊
                stream.write(audio_data)
                
                # 等待播放完成
                stream.stop_stream()
                stream.close()

        except ClientError as e:
            print(f"Error synthesizing speech: {e}")
            return None
        
    def __del__(self):
        if hasattr(self, 'p'):
            self.p.terminate()
        
async def main():
    tts = PollyClient()
    await tts.synthesize_speech("你好，我是 Polly 的語音合成服務。")
    
if __name__ == "__main__":
    asyncio.run(main())