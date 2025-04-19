import asyncio
from dotenv import load_dotenv
from stt import TranscribeClient
from llm import BedrockLlmClient
from tts2 import PollyClient


load_dotenv()

async def main():
    llm_client = BedrockLlmClient(
        system_prompt="你是一個友善的助手，請用簡潔明瞭的方式回答問題。如果我中途打斷你，請停止回答並聆聽我的新問題。"
    )
    
    tts_client = PollyClient()
    
    # 創建語音轉文字客戶端
    transcribe_client = TranscribeClient()
    
    async def llm_response_handler(transcript):
        # 在處理新的請求前，重置語音檢測狀態
        transcribe_client.reset_speech_detection()
        
        # 使用可中斷的方法生成回應
        response = await llm_client.generate_content_interruptible(
            transcript, 
            interrupt_check=transcribe_client.speech_detected_event
        )
        
        # 如果生成過程被中斷，不需要播放TTS
        if transcribe_client.is_speaking:
            print("\n檢測到用戶插話，停止生成回應")
            return response
            
        print(f"\nAI: {response}")
        
        # 以非阻塞方式播放TTS回應，同時監控用戶插話
        try:
            await tts_client.synthesize_speech(
                response,
                stop_check=transcribe_client.speech_detected_event
            )
        except Exception as e:
            print(f"TTS Error: {e}")
        
        return response

    print("語音聊天助手已啟動，請開始說話...")
    try:
        welcome_message = "嗨您好，我是您的語音助手，有什麼我可以幫助您的嗎？如果您想打斷我，隨時可以開始說話。"
        await tts_client.synthesize_speech(welcome_message)
        
        # 開始聽取用戶輸入
        await transcribe_client.start_transcription(llm_response_handler)
    except KeyboardInterrupt:
        print("\n程式已結束")
    finally:
        # 確保清理所有資源
        transcribe_client.close_stream()
        tts_client.stop_playback()
        
if __name__ == "__main__":
    asyncio.run(main())