#!/usr/bin/env python3
"""
RAG性能基准测试脚本
测试不同配置下的延迟表现
"""
import os
import time
import sys
from dotenv import load_dotenv
from rag_chain import build_chain

def test_retrieval_speed():
    """测试检索速度"""
    print("=== 检索性能测试 ===")
    load_dotenv()
    
    chain, retriever = build_chain()
    test_questions = [
        "武汉大学简介",
        "湖北省博物馆镇馆之宝",
        "武汉美食推荐"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n测试 {i}: {question}")
        
        # 测试检索
        t_start = time.perf_counter()
        docs = retriever.invoke(question)
        t_end = time.perf_counter()
        
        retrieval_ms = (t_end - t_start) * 1000.0
        print(f"检索耗时: {retrieval_ms:.1f} ms")
        print(f"检索到 {len(docs)} 个文档")
        
        # 测试完整生成
        print("开始生成测试...")
        t_gen_start = time.perf_counter()
        try:
            result = chain.invoke({"question": question, "chat_history": ""})
            t_gen_end = time.perf_counter()
            gen_ms = (t_gen_end - t_gen_start) * 1000.0
            print(f"生成耗时: {gen_ms:.1f} ms")
            print(f"回答长度: {len(result)} 字符")
        except Exception as e:
            print(f"生成失败: {e}")

def test_model_warmup():
    """测试模型预热效果"""
    print("\n=== 模型预热测试 ===")
    
    # 第一次调用（冷启动）
    print("第一次调用（冷启动）...")
    t1_start = time.perf_counter()
    chain, retriever = build_chain()
    result1 = chain.invoke({"question": "测试问题", "chat_history": ""})
    t1_end = time.perf_counter()
    cold_ms = (t1_end - t1_start) * 1000.0
    print(f"冷启动耗时: {cold_ms:.1f} ms")
    
    # 第二次调用（热启动）
    print("第二次调用（热启动）...")
    t2_start = time.perf_counter()
    result2 = chain.invoke({"question": "另一个测试问题", "chat_history": ""})
    t2_end = time.perf_counter()
    hot_ms = (t2_end - t2_start) * 1000.0
    print(f"热启动耗时: {hot_ms:.1f} ms")
    
    print(f"预热效果: {cold_ms/hot_ms:.1f}x 加速")

if __name__ == "__main__":
    print("RAG性能基准测试")
    print("=" * 50)
    
    try:
        test_retrieval_speed()
        test_model_warmup()
    except KeyboardInterrupt:
        print("\n测试中断")
        sys.exit(0)
    except Exception as e:
        print(f"测试失败: {e}")
        sys.exit(1)
