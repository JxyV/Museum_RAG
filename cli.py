import os
import sys
import logging
import time
from typing import List, Dict

from dotenv import load_dotenv

from rag_chain import build_chain
from langchain_core.callbacks import BaseCallbackHandler


class StdoutStreamingHandler(BaseCallbackHandler):
    def __init__(self) -> None:
        self.started = False
        self.first_token_time: float | None = None
        self._buffer: List[str] = []

    def on_llm_start(self, *args, **kwargs) -> None:
        self.started = True
        self._buffer.clear()
        self.first_token_time = None

    def on_llm_new_token(self, token: str, **kwargs) -> None:  # type: ignore[override]
        if self.first_token_time is None:
            self.first_token_time = time.perf_counter()
        self._buffer.append(token)
        sys.stdout.write(token)
        sys.stdout.flush()

    def on_llm_end(self, *args, **kwargs) -> None:
        if self.started:
            print("")
        self.started = False

    def get_text(self) -> str:
        return "".join(self._buffer)


def non_interactive_once(question: str) -> None:
    from rag_chain import answer_question

    result = answer_question(question)
    answer = result.get("answer", "")
    sources = result.get("sources", [])

    print("\n=== 答案 ===")
    print(answer.strip())
    if sources:
        print("\n=== 引用 ===")
        for i, s in enumerate(sources, 1):
            print(f"{i}. {s['source']} ({s['locator']})")
    else:
        print("\n(未检索到相关片段，已尽力避免幻觉。)")


def interactive_chat() -> None:
    load_dotenv()
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper(), format="%(message)s")

    # 预热：提前构建chain和retriever，避免首次调用延迟
    print("正在初始化RAG系统...")
    chain, retriever = build_chain()
    print("初始化完成！")

    print('RAG 对话（流式输出，输入 :q 退出）')
    chat_history: List[str] = []

    while True:
        try:
            q = input("你：").strip()
            if not q:
                continue
            if q in {":q", "exit", "quit"}:
                break

            # 分步计时，诊断延迟来源
            t_retrieval_start = time.perf_counter()
            docs = retriever.invoke(q)
            t_retrieval_end = time.perf_counter()
            
            if not docs:
                print("助手：抱歉，我不确定，可能未在知识库中找到相关内容。")
                continue

            print("助手：", end="", flush=True)
            handler = StdoutStreamingHandler()
            t_generation_start = time.perf_counter()
            for _ in chain.stream({"question": q, "chat_history": "\n".join(chat_history)}, config={"callbacks": [handler]}):
                pass
            t_generation_end = time.perf_counter()

            # 收集本轮输出文本并统计中文字符数
            output_text = handler.get_text()
            chinese_count = sum(1 for ch in output_text if "\u4e00" <= ch <= "\u9fff")

            # 在回答和统计之间留一个空行
            print("")

            # 输出详细时延统计
            retrieval_ms = (t_retrieval_end - t_retrieval_start) * 1000.0
            generation_ms = (t_generation_end - t_generation_start) * 1000.0
            first_token_ms = None
            if handler.first_token_time is not None:
                first_token_ms = (handler.first_token_time - t_generation_start) * 1000.0
            
            print("--- 性能统计 ---")
            print(f"检索耗时：{retrieval_ms:.1f} ms")
            if first_token_ms is not None:
                print(f"首个 token 延迟：{first_token_ms:.1f} ms")
            else:
                print("首个 token 延迟：不可用")
            print(f"生成耗时：{generation_ms:.1f} ms")
            print(f"总耗时：{retrieval_ms + generation_ms:.1f} ms")
            print(f"中文字符数：{chinese_count}")

            chat_history.append(f"用户: {q}")
            chat_history.append("助手: [上一轮回答略]")

            sources = []
            for d in docs:
                source = d.metadata.get("source", "unknown")
                page = d.metadata.get("page")
                chunk_id = d.metadata.get("chunk_id")
                locator = f"page {page}" if page is not None else f"chunk {chunk_id}"
                sources.append({"source": source, "locator": locator})

            if sources:
                print("\n--- 引用 ---")
                for i, s in enumerate(sources, 1):
                    print(f"{i}. {s['source']} ({s['locator']})")

        except (KeyboardInterrupt, EOFError):
            print("")
            break
        except Exception as e:
            logging.exception("发生错误: %s", e)


def main() -> None:
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        non_interactive_once(question)
        return
    interactive_chat()


if __name__ == "__main__":
    main()
