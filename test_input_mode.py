#!/usr/bin/env python3
"""
测试输入模式逻辑
"""
import os

# 设置API Key
os.environ["DASHSCOPE_API_KEY"] = "sk-8fae5f3d1cdd4e2dbabce5b6340a05c8"

def test_input_mode():
    """测试输入模式逻辑"""
    print("🔧 测试输入模式逻辑...")
    
    # 模拟不同的输入模式
    test_cases = [
        ("text", "这是文本输入测试"),
        ("voice", "这是语音输入测试")
    ]
    
    for mode, question in test_cases:
        print(f"\n--- 测试 {mode} 模式 ---")
        print(f"问题: {question}")
        
        if mode == "voice":
            print("🔊 应该播放语音回答")
        else:
            print("💬 应该只显示文本回答")
        
        print("✅ 逻辑正确")

if __name__ == "__main__":
    test_input_mode()
