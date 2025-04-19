# AWS 語音聊天機器人

這個專案是一個基於AWS服務的語音聊天機器人，能夠將語音轉換成文字(STT)，使用大型語言模型(LLM)生成回應，並將回應轉換成語音(TTS)。

## 功能特點

- 語音輸入轉文字 (使用Amazon Transcribe)
- 文字處理與生成回應 (使用Amazon Bedrock LLM)
- 文字轉語音輸出 (使用Amazon Polly)
- 即時對話式互動

## 環境需求

- Python 3.8 或更高版本
- 有效的AWS帳號與認證
- 麥克風和喇叭

## 設定步驟

### 使用uv設定專案（推薦）

[uv](https://github.com/astral-sh/uv) 是一個快速的Python套件安裝和虛擬環境管理工具。

```bash
# 安裝uv (如果尚未安裝)
pip install uv

# 創建並啟動虛擬環境
uv venv

# 啟動虛擬環境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安裝依賴套件
uv pip install -r requirements.txt
```

### 使用傳統的venv設定專案

```bash
# 創建虛擬環境
python3 -m venv venv

# 啟動虛擬環境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. 安裝依賴套件

```bash
uv pip install -r requirements.txt
```

### 3. AWS設定

1. 確保您有AWS帳號並已創建具有適當權限的IAM用戶
    - 需要的AWS服務權限：
        - Amazon Transcribe
        - Amazon Bedrock
        - Amazon Polly

2. 配置AWS認證資訊，在項目根目錄創建`.env`文件，填入以下內容：

```
AWS_ACCESS_KEY_ID=您的AWS訪問密鑰ID
AWS_SECRET_ACCESS_KEY=您的AWS秘密訪問密鑰
AWS_REGION=您的AWS區域（例如：us-west-2）
AWS_BEDROCK_MODEL=您選擇的Bedrock模型（例如：us.amazon.nova-pro-v1:0）
```

### 4. 運行應用程式

```bash
python3 main.py
```

啟動後，語音助手會問候您，然後可以開始對話。

## 使用方法

1. 運行程式後，您會聽到歡迎訊息
2. 對著麥克風說話，系統會自動開始錄製
3. 說完話後稍等片刻，系統會處理您的語音並通過大型語言模型生成回應
4. 系統會用語音讀出回應內容
5. 您可以繼續對話，保持互動
6. 使用`Ctrl+C`終止程式

## 系統架構

- `main.py`: 主程式，整合所有組件
- `stt.py`: 語音轉文字模組，使用Amazon Transcribe
- `llm.py`: 大型語言模型模組，使用Amazon Bedrock
- `tts2.py`: 文字轉語音模組，使用Amazon Polly

## 常見問題

- **麥克風無法正常工作？**: 確保系統已正確設置音訊輸入設備，並授予應用程式訪問麥克風的權限。
- **AWS認證錯誤？**: 確認您的AWS認證信息正確，且IAM用戶具有適當的服務訪問權限。
- **依賴項安裝失敗？**: 嘗試逐個安裝依賴項，特別是PyAudio可能需要額外的系統庫支持。

## 使用uv進行套件管理

如果您想使用uv進行其他套件管理操作：

```bash
# 安裝單一套件
uv pip install 套件名稱

# 更新套件
uv pip install --upgrade 套件名稱

# 導出當前環境的依賴
uv pip freeze > requirements.txt
```

