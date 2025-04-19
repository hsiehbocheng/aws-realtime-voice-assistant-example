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
        response = await self.chain.ainvoke({"input": user_message})
        return response['chat_history'][-1].content
    
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