import os
import asyncio
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_aws import ChatBedrock
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()
aws_region = os.getenv("AWS_REGION")
llm_model_id = os.getenv("AWS_BEDROCK_MODEL")


class BedrockLlmClient:
    def __init__(self, model_id=None, region=None, model_kwargs=None, system_prompt=None):
        self.region = region or os.getenv("AWS_REGION")
        self.model_id = model_id or os.getenv("AWS_BEDROCK_MODEL", "us.deepseek.r1-v1:0")
        self.model_kwargs = model_kwargs or {"temperature": 0.5}
        self.system_prompt = system_prompt if system_prompt else "你是一隻貓"
        
        self.llm = ChatBedrock(
            model_id=self.model_id,
            region_name=self.region,
            model_kwargs=model_kwargs
        )
        
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}"),
            ("ai", "{chat_history}"),
        ])
    
        self.chain = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=self.prompt_template,
            verbose=False
        )
        
    async def generate_content(self, user_message):
        """生成回應內容"""
        response = await self.chain.ainvoke({"input": user_message})
        return response['chat_history'][-1].content
        
    async def generate_content_interruptible(self, user_message, interrupt_check=None):
        """
        可中斷的生成內容方法
        
        Args:
            user_message: 用戶訊息
            interrupt_check: 一個可等待的對象，用於檢查是否需要中斷生成
            
        Returns:
            生成的回應內容，如果被中斷則可能不完整
        """
        # 設置一個任務來檢查中斷
        interrupt_task = None
        if interrupt_check:
            interrupt_task = asyncio.create_task(interrupt_check.wait())
        
        # 開始生成回應
        content_task = asyncio.create_task(self.generate_content(user_message))
        
        # 等待其中一個任務完成
        done, pending = await asyncio.wait(
            [content_task] + ([interrupt_task] if interrupt_task else []),
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # 如果中斷任務完成，取消內容生成任務並返回部分內容
        if interrupt_task in done:
            content_task.cancel()
            try:
                await content_task
            except asyncio.CancelledError:
                print("\n內容生成被中斷")
                # 返回一個預設的回應，表示我們稍後將繼續
                return "我明白您想插話。請繼續說。"
        else:
            # 如果內容生成完成，取消中斷檢查任務
            if interrupt_task and not interrupt_task.done():
                interrupt_task.cancel()
            
            # 獲取生成的回應
            return await content_task
    
if __name__ == "__main__":
    
    llm = BedrockLlmClient()
    print("請輸入訊息 (輸入 exit、q 或 bye 結束對話):")
    try:
        while True:
            user_input = input("user: ")
            if user_input.lower() in ['exit', 'q', 'bye']:
                print("喵~ 再見！")
                break
            response = asyncio.run(llm.generate_content(user_input))
            print(f"喵星人: {response}")
    except KeyboardInterrupt:
        print("\n喵~ 再見！")