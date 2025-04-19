import os
import sys
import asyncio
import aiofile
from dotenv import load_dotenv
import pyaudio
import time

from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

load_dotenv()
aws_region = os.getenv("AWS_REGION")

class TranscriptHandler(TranscriptResultStreamHandler):
    def __init__(self, output_stream, transcript_callback=None):
        super().__init__(output_stream)
        self.transcript_callback = transcript_callback
    
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        try:
            results = transcript_event.transcript.results
            for result in results:
                if not result.is_partial:
                    for alt in result.alternatives:
                        transcript = alt.transcript
                        if transcript.strip():
                            print(f"\n使用者: {transcript}")
                            if self.transcript_callback:
                                try:
                                    await self.transcript_callback(transcript)
                                except Exception as e:
                                    print(f"Callback Error: {e}")
        except Exception as e:
            print(f"Transcribe Error: {e}")
                            
class TranscribeClient:
    def __init__(self, region=None, language_code="zh-TW", sample_rate_hz=16_000, media_encoding="pcm"):
        self.region = region or os.getenv("AWS_REGION")
        self.language_code = language_code
        self.sample_rate_hz = sample_rate_hz
        self.media_encoding = media_encoding
        self.p = None
        self.stream = None
        
                
    def get_default_input_device(self):
        self.p = pyaudio.PyAudio()
        try:
            default_device_index = self.p.get_default_input_device_info()['index']
            device_info = self.p.get_device_info_by_index(default_device_index)
            print(f"\n使用預設麥克風: {device_info['name']}")
            return default_device_index
        except Exception as e:
            print(f"無法獲取預設麥克風: {str(e)}")
            sys.exit(1)
            

    async def mic_stream(self):
        chunk = 1_024
        sample_format = pyaudio.paInt16
        fs = self.sample_rate_hz
        
        if not self.p:
            self.p = pyaudio.PyAudio()
        
        device_index = self.get_default_input_device()
        self.stream = self.p.open(format=sample_format,
                        channels=1,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input_device_index=device_index,
                        input=True)
        
        print("開始錄音... (按Ctrl+C停止)")
        
        try:
            while True:
                try:
                    data = self.stream.read(chunk, exception_on_overflow=False)
                    yield data
                except OSError as e:
                    print(f"警告: 音頻輸入問題 ({e})，繼續處理...")
                    await asyncio.sleep(0.1)  # 短暫暫停，讓緩衝區恢復
        
        except KeyboardInterrupt:
            print("\n錄音停止")
        finally:
            self.close_stream()
    
    def close_stream(self):
        try:
            if hasattr(self, 'stream') and self.stream and self.stream.is_active():
                self.stream.stop_stream()
                self.stream.close()
        except Exception as e:
            print(f"關閉流時出錯: {e}")
        
        try:
            if hasattr(self, 'p') and self.p:
                self.p.terminate()
                self.p = None
        except Exception as e:
            print(f"終止 PyAudio 時出錯: {e}")
    
    async def write_chunks(self, stream):
        async for chunk in self.mic_stream():
            await stream.input_stream.send_audio_event(audio_chunk=chunk)
        await stream.input_stream.end_stream()
        
    async def start_transcription(self, transcript_callback=None):
        client = TranscribeStreamingClient(region=self.region)
        stream = await client.start_stream_transcription(
            language_code=self.language_code,
            media_sample_rate_hz=self.sample_rate_hz,
            media_encoding=self.media_encoding,
            # identify_multiple_languages=True,
            # language_options=["zh-TW", "en-US"],
        )
        
        handler = TranscriptHandler(stream.output_stream, transcript_callback)
        await asyncio.gather(self.write_chunks(stream), handler.handle_events())
                
if __name__ == "__main__":
    async def main():
        transcribe_client = TranscribeClient()
        await transcribe_client.start_transcription()
    
    asyncio.run(TranscribeClient().start_transcription())