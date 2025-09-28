"""
语音模型选择示例 - 展示程序员如何自由选择STT和TTS模型
"""
import os
from dotenv import load_dotenv
from voice_interface import (
    VoiceInterface, 
    WhisperSTT, 
    GummySTT, 
    SpeechRecognitionSTT,
    EdgeTTS, 
    Pyttsx3TTS
)

def example_1_whisper_edge():
    """示例1: Whisper STT + Edge TTS"""
    print("=== 示例1: Whisper STT + Edge TTS ===")
    
    # 程序员选择模型
    stt = WhisperSTT(model_size="base")  # 选择Whisper base模型
    tts = EdgeTTS(voice="zh-CN-XiaoxiaoNeural")  # 选择Edge TTS中文语音
    
    # 创建语音接口
    voice = VoiceInterface(stt_model=stt, tts_model=tts)
    
    # 测试语音转文本
    print("测试语音转文本...")
    text = voice.voice_to_text(duration=3)
    print(f"识别结果: {text}")
    
    # 测试文本转语音
    if text.strip():
        print("测试文本转语音...")
        voice.text_to_voice(text)
    
    voice.cleanup()


def example_2_gummy_pyttsx3():
    """示例2: 阿里云Gummy STT + Pyttsx3 TTS"""
    print("\n=== 示例2: 阿里云Gummy STT + Pyttsx3 TTS ===")
    
    # 需要设置API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("请设置DASHSCOPE_API_KEY环境变量")
        return
    
    # 程序员选择模型
    stt = GummySTT(api_key=api_key, model="gummy-chat-v1")
    tts = Pyttsx3TTS(rate=200, volume=0.9)
    
    # 创建语音接口
    voice = VoiceInterface(stt_model=stt, tts_model=tts)
    
    # 测试语音转文本
    print("测试语音转文本...")
    text = voice.voice_to_text(duration=3)
    print(f"识别结果: {text}")
    
    # 测试文本转语音
    if text.strip():
        print("测试文本转语音...")
        voice.text_to_voice(text)
    
    voice.cleanup()


def example_3_speech_recognition_edge():
    """示例3: SpeechRecognition STT + Edge TTS"""
    print("\n=== 示例3: SpeechRecognition STT + Edge TTS ===")
    
    # 程序员选择模型
    stt = SpeechRecognitionSTT(engine="google")
    tts = EdgeTTS(voice="zh-CN-YunxiNeural")  # 选择不同的中文语音
    
    # 创建语音接口
    voice = VoiceInterface(stt_model=stt, tts_model=tts)
    
    # 测试语音转文本
    print("测试语音转文本...")
    text = voice.voice_to_text(duration=3)
    print(f"识别结果: {text}")
    
    # 测试文本转语音
    if text.strip():
        print("测试文本转语音...")
        voice.text_to_voice(text)
    
    voice.cleanup()


def example_4_custom_config():
    """示例4: 自定义配置的模型选择"""
    print("\n=== 示例4: 自定义配置 ===")
    
    # 程序员可以根据需求选择不同的模型组合
    
    # 高质量识别 + 高质量语音合成
    print("高质量组合: Gummy STT + Edge TTS")
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if api_key:
        stt_high = GummySTT(api_key=api_key)
        tts_high = EdgeTTS(voice="zh-CN-XiaoxiaoNeural")
        voice_high = VoiceInterface(stt_model=stt_high, tts_model=tts_high)
        print("高质量模型已配置")
        voice_high.cleanup()
    
    # 本地处理 + 系统TTS
    print("本地处理组合: Whisper STT + Pyttsx3 TTS")
    stt_local = WhisperSTT(model_size="tiny")  # 使用更小的模型
    tts_local = Pyttsx3TTS(rate=150, volume=0.8)
    voice_local = VoiceInterface(stt_model=stt_local, tts_model=tts_local)
    print("本地处理模型已配置")
    voice_local.cleanup()
    
    # 快速原型组合
    print("快速原型组合: SpeechRecognition STT + Edge TTS")
    stt_fast = SpeechRecognitionSTT(engine="google")
    tts_fast = EdgeTTS(voice="zh-CN-XiaoxiaoNeural")
    voice_fast = VoiceInterface(stt_model=stt_fast, tts_model=tts_fast)
    print("快速原型模型已配置")
    voice_fast.cleanup()


def example_5_rag_integration():
    """示例5: 与RAG系统集成"""
    print("\n=== 示例5: 与RAG系统集成 ===")
    
    # 程序员为RAG系统选择最适合的语音模型
    # 推荐组合：高质量识别 + 自然语音合成
    
    # 选择模型
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if api_key:
        stt = GummySTT(api_key=api_key)  # 高质量中文识别
        tts = EdgeTTS(voice="zh-CN-XiaoxiaoNeural")  # 自然中文语音
    else:
        stt = WhisperSTT(model_size="base")  # 备选方案
        tts = EdgeTTS(voice="zh-CN-XiaoxiaoNeural")
    
    # 创建语音接口
    voice = VoiceInterface(stt_model=stt, tts_model=tts)
    
    print("RAG语音接口已配置:")
    print(f"STT模型: {type(stt).__name__}")
    print(f"TTS模型: {type(tts).__name__}")
    
    # 这里可以集成到RAG系统中
    # from multimodal_rag import MultimodalRAG
    # rag = MultimodalRAG()
    # rag.voice = voice  # 使用自定义的语音接口
    
    voice.cleanup()


def main():
    """运行所有示例"""
    load_dotenv()
    
    print("🎙️ 语音模型选择示例")
    print("=" * 50)
    print("这些示例展示程序员如何自由选择STT和TTS模型")
    print("=" * 50)
    
    try:
        # 运行示例
        example_1_whisper_edge()
        example_2_gummy_pyttsx3()
        example_3_speech_recognition_edge()
        example_4_custom_config()
        example_5_rag_integration()
        
        print("\n✅ 所有示例运行完成！")
        print("\n💡 程序员可以根据需求选择不同的模型组合:")
        print("- 高质量: Gummy STT + Edge TTS")
        print("- 本地处理: Whisper STT + Pyttsx3 TTS")
        print("- 快速原型: SpeechRecognition STT + Edge TTS")
        
    except Exception as e:
        print(f"❌ 示例运行失败: {e}")
        print("请确保已安装所需的依赖包")


if __name__ == "__main__":
    main()
