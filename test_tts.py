#!/usr/bin/env python3
"""
测试Qwen3-TTS Realtime WebSocket连接
"""
import os
import sys
from dotenv import load_dotenv
from voice_interface import Qwen3TTSRealtime

def test_tts():
    """测试TTS功能"""
    load_dotenv()
    
    # 检查API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 请设置DASHSCOPE_API_KEY环境变量")
        return
    
    print("🔧 初始化Qwen3-TTS Realtime...")
    try:
        tts = Qwen3TTSRealtime(api_key=api_key)
        print("✅ TTS初始化成功")
        
        # 测试文本
        test_text = "你好，我是通义千问的语音合成系统。"
        print(f"📝 测试文本: {test_text}")
        
        print("🔄 开始语音合成...")
        audio_data = tts.synthesize(test_text, voice="Cherry")
        
        if audio_data:
            print(f"✅ 合成成功，音频大小: {len(audio_data)} 字节")
            
            # 保存音频文件
            with open("test_output.wav", "wb") as f:
                f.write(audio_data)
            print("💾 音频已保存为 test_output.wav")
        else:
            print("❌ 合成失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tts()
