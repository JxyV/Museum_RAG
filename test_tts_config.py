#!/usr/bin/env python3
"""
测试TTS配置和音色功能
"""
import os

def test_tts_config():
    """测试TTS配置"""
    print("🔧 测试TTS配置和音色功能...")
    
    # 设置API Key
    os.environ["DASHSCOPE_API_KEY"] = "sk-8fae5f3d1cdd4e2dbabce5b6340a05c8"
    
    print("✅ API Key已设置")
    
    # 测试音色配置
    voices = {
        "芊悦 (Cherry)": "Cherry",
        "晨煦 (Ethan)": "Ethan", 
        "不吃鱼 (Nofish)": "Nofish",
        "詹妮弗 (Jennifer)": "Jennifer",
        "甜茶 (Ryan)": "Ryan",
        "卡捷琳娜 (Katerina)": "Katerina",
        "墨讲师 (Elias)": "Elias",
        "上海-阿珍 (Jada)": "Jada",
        "北京-晓东 (Dylan)": "Dylan",
        "四川-晴儿 (Sunny)": "Sunny",
        "南京-老李 (Li)": "Li",
        "陕西-秦川 (Marcus)": "Marcus",
        "闽南-阿杰 (Roy)": "Roy",
        "天津-李彼得 (Peter)": "Peter",
        "粤语-阿强 (Rocky)": "Rocky",
        "粤语-阿清 (Kiki)": "Kiki",
        "四川-程川 (Eric)": "Eric"
    }
    
    print(f"📋 可用音色数量: {len(voices)}")
    print("🎵 所有音色列表:")
    for i, (name, code) in enumerate(voices.items(), 1):
        print(f"  {i:2d}. {name} -> {code}")
    
    # 测试WebSocket配置
    print("\n🔗 WebSocket配置:")
    print("  URL: wss://dashscope.aliyuncs.com/api-ws/v1/realtime?model=qwen3-tts-flash-realtime")
    print("  Headers: Authorization: Bearer DASHSCOPE_API_KEY")
    
    # 测试消息格式
    print("\n📤 消息格式:")
    config_msg = {
        "type": "config",
        "voice": "Cherry",
        "format": "wav",
        "sample_rate": 16000,
        "enable_timestamp": False
    }
    print(f"  配置消息: {config_msg}")
    
    text_msg = {
        "type": "text",
        "text": "测试文本"
    }
    print(f"  文本消息: {text_msg}")
    
    end_msg = {
        "type": "end"
    }
    print(f"  结束消息: {end_msg}")
    
    # 测试响应格式
    print("\n📥 响应格式:")
    print("  audio: {type: 'audio', audio: 'base64_encoded_audio'}")
    print("  audio.done: {type: 'audio.done'}")
    print("  done: {type: 'done'}")
    print("  error: {type: 'error', message: 'error_message'}")
    
    print("\n✅ TTS配置测试完成")

if __name__ == "__main__":
    test_tts_config()
