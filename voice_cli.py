"""
语音版RAG CLI - 支持语音输入和语音输出
"""
import os
import sys
import time
import logging
from typing import List

from dotenv import load_dotenv
from rag_chain import build_chain
from voice_interface import VoiceInterface


class VoiceRAGCLI:
    """语音版RAG CLI"""
    
    def __init__(self):
        load_dotenv()
        self.setup_logging()
        
        # 初始化RAG系统
        print("正在初始化RAG系统...")
        self.chain, self.retriever = build_chain()
        print("RAG系统初始化完成！")
        
        # 初始化语音系统
        print("正在初始化语音系统...")
        self.voice = VoiceInterface()
        print("语音系统初始化完成！")
        
        # 交互模式设置
        self.voice_mode = os.getenv("VOICE_MODE", "hybrid").lower()
        self.auto_tts = os.getenv("AUTO_TTS", "true").lower() == "true"
        self.record_duration = int(os.getenv("RECORD_DURATION", "5"))
        
        self.chat_history: List[str] = []
    
    def setup_logging(self):
        level = os.getenv("LOG_LEVEL", "INFO").upper()
        logging.basicConfig(level=level, format="%(asctime)s | %(levelname)s | %(message)s")
    
    def get_user_input(self) -> str:
        """获取用户输入（文本或语音）"""
        if self.voice_mode == "voice":
            # 纯语音模式
            print("🎤 请说话...")
            return self.voice.voice_to_text(duration=self.record_duration)
        
        elif self.voice_mode == "text":
            # 纯文本模式
            return input("你：").strip()
        
        else:  # hybrid 混合模式
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
    
    def display_response(self, answer: str, sources: List[dict], performance_stats: dict):
        """显示回答和统计信息"""
        print(f"\n助手：{answer}")
        
        # 显示性能统计
        print("")
        print("--- 性能统计 ---")
        print(f"检索耗时：{performance_stats['retrieval_ms']:.1f} ms")
        if performance_stats['first_token_ms'] is not None:
            print(f"首个 token 延迟：{performance_stats['first_token_ms']:.1f} ms")
        else:
            print("首个 token 延迟：不可用")
        print(f"生成耗时：{performance_stats['generation_ms']:.1f} ms")
        print(f"总耗时：{performance_stats['total_ms']:.1f} ms")
        print(f"中文字符数：{performance_stats['chinese_count']}")
        
        # 显示引用
        if sources:
            print("\n--- 引用 ---")
            for i, s in enumerate(sources, 1):
                print(f"{i}. {s['source']} ({s['locator']})")
        
        # 自动语音输出
        if self.auto_tts and answer.strip():
            print("\n🔊 正在播放回答...")
            self.voice.text_to_voice(answer)
    
    def process_question(self, question: str):
        """处理单个问题"""
        if not question:
            return
        
        if question in {":q", "exit", "quit"}:
            return "exit"
        
        # 分步计时
        t_retrieval_start = time.perf_counter()
        docs = self.retriever.invoke(question)
        t_retrieval_end = time.perf_counter()
        
        if not docs:
            print("助手：抱歉，我不确定，可能未在知识库中找到相关内容。")
            return
        
        # 生成回答
        print("🔄 正在生成回答...")
        t_generation_start = time.perf_counter()
        
        # 使用非流式调用获取完整回答
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
        performance_stats = {
            "retrieval_ms": (t_retrieval_end - t_retrieval_start) * 1000.0,
            "generation_ms": (t_generation_end - t_generation_start) * 1000.0,
            "first_token_ms": None,  # 非流式模式无法获取
            "total_ms": (t_retrieval_end - t_retrieval_start + t_generation_end - t_generation_start) * 1000.0,
            "chinese_count": chinese_count
        }
        
        # 显示回答
        self.display_response(answer, sources, performance_stats)
        
        # 更新聊天历史
        self.chat_history.append(f"用户: {question}")
        self.chat_history.append("助手: [上一轮回答略]")
    
    def run(self):
        """运行语音RAG CLI"""
        print("🎙️ 语音RAG对话系统")
        print("=" * 50)
        print(f"语音模式: {self.voice_mode}")
        print(f"自动语音输出: {'开启' if self.auto_tts else '关闭'}")
        print("=" * 50)
        
        while True:
            try:
                question = self.get_user_input()
                
                if question == "exit":
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
        cli = VoiceRAGCLI()
        cli.process_question(question)
        cli.voice.cleanup()
    else:
        # 交互模式
        cli = VoiceRAGCLI()
        cli.run()


if __name__ == "__main__":
    main()
