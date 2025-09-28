"""
RAG系统配置类
程序员可以在这里自定义所有配置
"""
import os
from pathlib import Path


class RAGConfig:
    """RAG系统配置类"""
    
    def __init__(self):
        # 数据库配置 - 程序员可以在这里修改
        self.config = {
            # 文档相关配置
            "docs_root": "./docs",  # 文档根目录
            "chunk_size": 800,  # 文档切分大小
            "chunk_overlap": 120,  # 文档切分重叠
            
            # 向量库配置
            "store_dir": "./data_db/chroma_db/.hubei_vectdb",  # 向量库存储路径
            "collection_name": "local_knowledge",  # 集合名称
            
            # 检索配置
            "top_k": 4,  # 检索文档数量
            
            # 嵌入模型配置
            "embedding_backend": "sentence-transformers",  # sentence-transformers | ollama
            "embedding_model": "BAAI/bge-small-en-v1.5",  # 嵌入模型名称
            
            # LLM配置
            "llm_backend": "ollama",  # ollama | openai
            "ollama_model": "qwen2.5:7b",  # Ollama模型
            "ollama_base_url": "http://localhost:11434",  # Ollama服务地址
            
            # 语音配置
            "voice_mode": "hybrid",  # voice | text | hybrid
            "auto_tts": True,  # 是否自动播放回答
            "record_duration": 5,  # 录音时长(秒)
            
            # STT配置
            "stt_backend": "whisper",  # whisper | gummy | speech_recognition
            "stt_model": "base",  # STT模型大小
            
            # TTS配置
            "tts_backend": "edge",  # edge | pyttsx3
            "tts_voice": "zh-CN-XiaoxiaoNeural",  # TTS语音
        }
    
    def get_docs_dir(self) -> str:
        """获取文档目录"""
        return self.config["docs_root"]
    
    def get_store_dir(self) -> str:
        """获取向量库存储目录"""
        store_dir = self.config["store_dir"]
        # 确保目录存在
        os.makedirs(store_dir, exist_ok=True)
        return store_dir
    
    def get_collection_name(self) -> str:
        """获取集合名称"""
        return self.config["collection_name"]
    
    def get_chunk_config(self) -> dict:
        """获取文档切分配置"""
        return {
            "chunk_size": self.config["chunk_size"],
            "chunk_overlap": self.config["chunk_overlap"]
        }
    
    def get_retrieval_config(self) -> dict:
        """获取检索配置"""
        return {
            "top_k": self.config["top_k"]
        }
    
    def get_embedding_config(self) -> dict:
        """获取嵌入模型配置"""
        return {
            "backend": self.config["embedding_backend"],
            "model": self.config["embedding_model"]
        }
    
    def get_llm_config(self) -> dict:
        """获取LLM配置"""
        return {
            "backend": self.config["llm_backend"],
            "ollama_model": self.config["ollama_model"],
            "ollama_base_url": self.config["ollama_base_url"]
        }
    
    def get_voice_config(self) -> dict:
        """获取语音配置"""
        return {
            "mode": self.config["voice_mode"],
            "auto_tts": self.config["auto_tts"],
            "record_duration": self.config["record_duration"],
            "stt_backend": self.config["stt_backend"],
            "stt_model": self.config["stt_model"],
            "tts_backend": self.config["tts_backend"],
            "tts_voice": self.config["tts_voice"]
        }
    
    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
            else:
                print(f"警告: 未知配置项 '{key}'")
    
    def print_config(self):
        """打印当前配置"""
        print("🔧 RAG系统配置:")
        print("=" * 50)
        for key, value in self.config.items():
            print(f"{key}: {value}")
        print("=" * 50)


# 全局配置实例
rag_config = RAGConfig()


def get_rag_config() -> RAGConfig:
    """获取RAG配置实例"""
    return rag_config


# 配置示例 - 程序员可以参考这些示例
class ConfigExamples:
    """配置示例类"""
    
    @staticmethod
    def museum_config():
        """博物馆知识库配置"""
        config = RAGConfig()
        config.update_config(
            store_dir="./data_db/museum/chroma_db",
            collection_name="museum_knowledge",
            docs_root="./docs/museum"
        )
        return config
    
    @staticmethod
    def enterprise_config():
        """企业文档库配置"""
        config = RAGConfig()
        config.update_config(
            store_dir="./data_db/enterprise/chroma_db",
            collection_name="enterprise_docs",
            docs_root="./docs/enterprise",
            chunk_size=1000,
            chunk_overlap=150
        )
        return config
    
    @staticmethod
    def personal_config():
        """个人笔记库配置"""
        config = RAGConfig()
        config.update_config(
            store_dir="./data_db/personal/chroma_db",
            collection_name="personal_notes",
            docs_root="./docs/personal",
            chunk_size=600,
            chunk_overlap=80
        )
        return config


if __name__ == "__main__":
    # 测试配置
    config = RAGConfig()
    config.print_config()
    
    print("\n📁 存储目录:", config.get_store_dir())
    print("📚 集合名称:", config.get_collection_name())
    print("📄 文档目录:", config.get_docs_dir())
