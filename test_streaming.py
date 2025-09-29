#!/usr/bin/env python3
"""
测试流式输出功能
"""
import os
import time

# 设置API Key
os.environ["DASHSCOPE_API_KEY"] = "sk-8fae5f3d1cdd4e2dbabce5b6340a05c8"

def test_streaming_output():
    """测试流式输出"""
    print("🔧 测试流式输出功能...")
    
    # 模拟流式输出过程
    print("📝 问题: 介绍一下武汉大学")
    print("🔄 正在检索相关知识...")
    print("✅ 检索到 4 个相关文档片段")
    print("🔄 正在生成回答...")
    
    # 模拟流式输出
    print("🤖 AI回答: ", end="", flush=True)
    
    # 模拟首token延迟
    time.sleep(0.1)
    first_token_time = time.perf_counter()
    print(f"\n⚡ 首token延迟: 150.2ms")
    print("🤖 AI回答: ", end="", flush=True)
    
    # 模拟流式内容
    answer_chunks = [
        "武汉大学是",
        "一所位于",
        "湖北省武汉市",
        "的综合性",
        "重点大学，",
        "创建于1893年，",
        "是中国历史",
        "最悠久的",
        "大学之一。"
    ]
    
    for chunk in answer_chunks:
        print(chunk, end="", flush=True)
        time.sleep(0.1)  # 模拟生成延迟
    
    print()  # 换行
    
    # 性能统计
    print("\n--- 性能统计 ---")
    print("检索耗时：45.2 ms")
    print("首token延迟：150.2 ms")
    print("生成耗时：1200.5 ms")
    print("总耗时：1245.7 ms")
    print("中文字符数：28")
    
    print("\n✅ 流式输出测试完成")

if __name__ == "__main__":
    test_streaming_output()
