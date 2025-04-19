import asyncio
from dotenv import load_dotenv
from stt import TranscribeClient
from llm import BedrockLlmClient
from tts2 import PollyClient


load_dotenv()

async def main():
    llm_client = BedrockLlmClient(
        system_prompt="你是一個友善的助手，請用簡潔明瞭的方式回答問題。"
    )
    
    tts_client = PollyClient()
    
    async def llm_response_handler(transcript):
        response = await llm_client.generate_content(transcript)
        print(f"\nAI: {response}")
        
        await tts_client.synthesize_speech(response)
        
        return response

    transcribe_client = TranscribeClient()
    
    print("語音聊天助手已啟動，請開始說話...")
    try:
        welcome_message = "嗨您好"
        await tts_client.synthesize_speech(welcome_message)
        
        await transcribe_client.start_transcription(llm_response_handler)
    except KeyboardInterrupt:
        print("\n程式已結束")
    finally:
        transcribe_client.close_stream()
        
if __name__ == "__main__":
    asyncio.run(main())