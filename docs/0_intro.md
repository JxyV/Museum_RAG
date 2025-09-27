# 项目简介

这是一个“最小可用”的 RAG 示例：
- 从 `docs/` 读取 PDF/Markdown/TXT 文档
- 使用 `RecursiveCharacterTextSplitter` 切分为片段
- 通过本地向量库 Chroma 进行检索
- 结合本地 Ollama 或 OpenAI 的大模型生成回答，并给出引用

在 CLI 中，你可以像这样提问：

```bash
python cli.py "这个示例项目做什么？"
```
