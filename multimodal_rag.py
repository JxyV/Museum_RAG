"""
多模态RAG系统 - 支持语音和文本输入，完整的RAG流程
"""
import os
import sys
import time
import logging
from typing import List, Dict

from dotenv import load_dotenv
from rag_chain import build_chain
from voice_interface import VoiceInterface


class MultimodalRAG:
    """多模态RAG系统"""
    
    def __init__(self):
        load_dotenv()
        self.setup_logging()
        
        # 初始化RAG系统
        print("🔄 正在初始化RAG系统...")
        self.chain, self.retriever = build_chain()
        print("✅ RAG系统初始化完成！")
        
        # 初始化语音系统
        print("🔄 正在初始化语音系统...")
        self.voice = VoiceInterface()
        print("✅ 语音系统初始化完成！")
        
        # 配置
        self.auto_tts = os.getenv("AUTO_TTS", "true").lower() == "true"
        self.record_duration = int(os.getenv("RECORD_DURATION", "5"))
        self.chat_history: List[str] = []
    
    def setup_logging(self):
        level = os.getenv("LOG_LEVEL", "INFO").upper()
        logging.basicConfig(level=level, format="%(asctime)s | %(levelname)s | %(message)s")
    
    def get_user_input(self) -> str:
        """获取用户输入（支持文本和语音）"""
        print("\n" + "="*50)
        print("选择输入方式:")
        print("1. 文本输入 (t)")
        print("2. 语音输入 (v)")  
        print("3. 退出 (q)")
        
        choice = input("请选择 (t/v/q): ").strip().lower()
        
        if choice == "q":
            return ":q"
        elif choice == "v":
            print("🎤 请说话...")
            return self.voice.voice_to_text(duration=self.record_duration)
        else:  # 默认文本输入
            return input("你：").strip()
    
    def rag_process(self, question: str) -> Dict:
        """完整的RAG处理流程"""
        print(f"\n📝 问题: {question}")
        print("🔄 正在检索相关知识...")
        
        # 第一步：向量检索
        t_retrieval_start = time.perf_counter()
        docs = self.retriever.invoke(question)
        t_retrieval_end = time.perf_counter()
        
        if not docs:
            return {
                "answer": "抱歉，我不确定，可能未在知识库中找到相关内容。",
                "sources": [],
                "performance": {
                    "retrieval_ms": (t_retrieval_end - t_retrieval_start) * 1000.0,
                    "generation_ms": 0,
                    "total_ms": (t_retrieval_end - t_retrieval_start) * 1000.0,
                    "chinese_count": 0
                }
            }
        
        print(f"✅ 检索到 {len(docs)} 个相关文档片段")
        print("🔄 正在生成回答...")
        
        # 第二步：LLM生成回答
        t_generation_start = time.perf_counter()
        answer = self.chain.invoke({
            "question": question, 
            "chat_history": "\n".join(self.chat_history)
        })
        t_generation_end = time.perf_counter()
        
        # 统计中文字符
        chinese_count = sum(1 for ch in answer if "\u4e00" <= ch <= "\u9fff")
        
        # 准备引用信息
        sources = []
        for d in docs:
            source = d.metadata.get("source", "unknown")
            page = d.metadata.get("page")
            chunk_id = d.metadata.get("chunk_id")
            locator = f"page {page}" if page is not None else f"chunk {chunk_id}"
            sources.append({"source": source, "locator": locator})
        
        # 性能统计
        performance = {
            "retrieval_ms": (t_retrieval_end - t_retrieval_start) * 1000.0,
            "generation_ms": (t_generation_end - t_generation_start) * 1000.0,
            "total_ms": (t_retrieval_end - t_retrieval_start + t_generation_end - t_generation_start) * 1000.0,
            "chinese_count": chinese_count
        }
        
        return {
            "answer": answer,
            "sources": sources,
            "performance": performance
        }
    
    def display_result(self, result: Dict):
        """显示RAG结果"""
        answer = result["answer"]
        sources = result["sources"]
        perf = result["performance"]
        
        print(f"\n🤖 助手：{answer}")
        
        # 性能统计
        print("\n--- 性能统计 ---")
        print(f"检索耗时：{perf['retrieval_ms']:.1f} ms")
        print(f"生成耗时：{perf['generation_ms']:.1f} ms")
        print(f"总耗时：{perf['total_ms']:.1f} ms")
        print(f"中文字符数：{perf['chinese_count']}")
        
        # 引用信息
        if sources:
            print("\n--- 引用 ---")
            for i, s in enumerate(sources, 1):
                print(f"{i}. {s['source']} ({s['locator']})")
        
        # 语音输出
        if self.auto_tts and answer.strip():
            print("\n🔊 正在播放回答...")
            self.voice.text_to_voice(answer)
    
    def process_question(self, question: str):
        """处理单个问题"""
        if not question:
            return
        
        if question in {":q", "exit", "quit"}:
            return "exit"
        
        # 执行RAG流程
        result = self.rag_process(question)
        
        # 显示结果
        self.display_result(result)
        
        # 更新聊天历史
        self.chat_history.append(f"用户: {question}")
        self.chat_history.append("助手: [上一轮回答略]")
    
    def run(self):
        """运行多模态RAG系统"""
        print("🎙️ 多模态RAG对话系统")
        print("=" * 50)
        print("支持功能:")
        print("- 文本输入 → RAG检索 → 文本/语音输出")
        print("- 语音输入 → RAG检索 → 文本/语音输出")
        print("- 完整的知识库检索和引用")
        print("=" * 50)
        
        while True:
            try:
                question = self.get_user_input()
                
                if question == ":q":
                    break
                
                if not question:
                    continue
                
                result = self.process_question(question)
                if result == "exit":
                    break
                
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                logging.exception("发生错误: %s", e)
                print(f"❌ 发生错误: {e}")
        
        self.voice.cleanup()
        print("✅ 系统已关闭")


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 命令行模式：直接处理问题
        question = " ".join(sys.argv[1:])
        rag = MultimodalRAG()
        rag.process_question(question)
        rag.voice.cleanup()
    else:
        # 交互模式
        rag = MultimodalRAG()
        rag.run()


if __name__ == "__main__":
    main()
