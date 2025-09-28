## Quick Start

1) Create venv and activate
- macOS/Linux:
```bash
python -m venv .venv && source .venv/bin/activate
```
- Windows (PowerShell):
```powershell
python -m venv .venv; .\\.venv\\Scripts\\Activate.ps1
```

2) Install dependencies
```bash
pip install -r requirements.txt
```

3) Configure environment
```bash
cp .env.example .env
# edit .env if needed
```

4) Put your documents into `docs/` (PDF/Markdown/TXT). Sample files included.

5) Build the vector store
```bash
python ingest.py
```

6) Ask via CLI
```bash
python cli.py "什么是示例项目？"
```

7) Or run the API server (optional)
```bash
uvicorn server:app --reload
# POST /ask { "question": "..." }
```

8) Or use multimodal RAG (语音+文本)
```bash
python multimodal_rag.py
# 支持语音输入和语音输出，完整的RAG流程
```

---

## Overview
A minimal RAG starter using LangChain + Chroma. It reads local documents from `docs/`, splits them, creates embeddings, stores them in Chroma (`.chroma/`), and provides a simple CLI and optional FastAPI endpoint for question answering with citations.

### Features
- Load PDF/Markdown/TXT from `docs/`
- Split with `RecursiveCharacterTextSplitter` (configurable via `.env`)
- Embeddings: sentence-transformers (default) or Ollama Embeddings
- Vector DB: Chroma (persisted in `.chroma/`)
- LLM: local Ollama (default) or OpenAI (via `OPENAI_API_KEY`)
- Retrieval-augmented generation with top-k contexts and source citations
- **Multimodal Support**: Voice input/output with STT/TTS models
- **Multiple STT**: Whisper, SpeechRecognition
- **Multiple TTS**: Edge TTS, Coqui TTS, Pyttsx3

### Models
- Embeddings (choose via `.env`):
  - sentence-transformers: e.g., `BAAI/bge-small-en-v1.5` (English) / `BAAI/bge-m3` (multilingual/Chinese)
  - Ollama Embeddings: set `EMBEDDING_BACKEND=ollama` and optionally `EMBEDDING_MODEL=bge-m3`
- LLM Backends:
  - Ollama: set `LLM_BACKEND=ollama` and `OLLAMA_MODEL` (e.g., `qwen2.5:7b`, `llama3.1:8b-instruct`)
  - OpenAI: set `LLM_BACKEND=openai` and `OPENAI_API_KEY`
- STT Models:
  - Whisper: `STT_BACKEND=whisper`, `STT_MODEL=base`
  - SpeechRecognition: `STT_BACKEND=speech_recognition`, `STT_ENGINE=google`
  - **阿里云Gummy**: `STT_BACKEND=gummy`, `DASHSCOPE_API_KEY=your-key`

### Ollama Notes
- Install Ollama: see `https://ollama.ai/`
- Pull models, e.g.:
```bash
ollama pull qwen2.5:7b
ollama pull llama3.1:8b-instruct
ollama pull bge-m3
```
- Ensure the service is running at `http://localhost:11434` (default). If not, set `OLLAMA_BASE_URL` in `.env`.

### Environment Variables (.env)
- EMBEDDING_BACKEND: `sentence-transformers` | `ollama`
- EMBEDDING_MODEL: model name, e.g. `BAAI/bge-small-en-v1.5` or `BAAI/bge-m3`
- LLM_BACKEND: `ollama` | `openai`
- OLLAMA_MODEL: e.g., `qwen2.5:7b`
- OPENAI_API_KEY: your key if using OpenAI
- CHUNK_SIZE: default 800
- CHUNK_OVERLAP: default 120
- TOP_K: default 4
- DOCS_DIR: default `docs`
- CHROMA_PERSIST_DIR: default `.chroma`
- **CHROMA_COLLECTION_NAME**: default `rag_docs` (自定义数据库名称)

### Workflow
1. `ingest.py` loads files, chunks, embeds, and writes to Chroma
2. `rag_chain.py` builds the retriever and LCEL RAG chain
3. `cli.py` and `server.py` call the chain to answer questions and return citations

### FAQ
- No results found?
  - You will get a polite message indicating uncertainty if retrieval returns nothing.
- Switching backends?
  - Modify `.env` only; code reads configuration dynamically.
- PDF page numbers?
  - Citations include `filename` and `page` when available; otherwise the `chunk_id`.

### 阿里云Gummy STT配置

1. **获取API Key**：
   - 访问[阿里云百炼平台](https://help.aliyun.com/zh/model-studio/sentence-python-sdk)
   - 开通服务并获取API Key

2. **配置环境变量**：
```bash
# 在 .env 文件中添加
STT_BACKEND=gummy
DASHSCOPE_API_KEY=your-dashscope-api-key-here
STT_MODEL=gummy-chat-v1
```

3. **安装依赖**：
```bash
pip install dashscope>=1.14.0
```

4. **使用Gummy STT**：
```bash
python multimodal_rag.py
# 选择语音输入，将使用阿里云Gummy进行识别
```

### 自定义Chroma数据库名称

**问题**: Chroma数据库名称显示为乱码或默认名称  
**解决**: 通过环境变量自定义数据库名称

1. **在 `.env` 文件中设置**：
```bash
# 自定义数据库名称
CHROMA_COLLECTION_NAME=my_knowledge_base
CHROMA_PERSIST_DIR=.chroma
```

2. **重新构建向量库**：
```bash
python ingest.py
```

3. **验证数据库名称**：
```bash
# 查看 .chroma 目录下的文件
ls -la .chroma/
```

**支持的名称格式**：
- 英文: `my_knowledge_base`
- 中文: `我的知识库` 
- 数字: `knowledge_base_2024`
- 下划线: `museum_docs`

### Development
- Python 3.10+
- Keep docs small for quick local testing.
