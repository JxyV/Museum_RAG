#!/usr/bin/env python3
"""
测试音频播放功能
"""
import os
import tempfile
import subprocess
import wave
import io

def test_audio_playback():
    """测试音频播放"""
    print("🔧 测试音频播放功能...")
    
    # 设置API Key
    os.environ["DASHSCOPE_API_KEY"] = "sk-8fae5f3d1cdd4e2dbabce5b6340a05c8"
    
    try:
        from voice_interface import Qwen3TTSRealtime
        
        print("✅ 初始化TTS...")
        tts = Qwen3TTSRealtime()
        
        print("🔄 合成测试音频...")
        test_text = "你好，这是音频播放测试。"
        audio_data = tts.synthesize(test_text, voice="Cherry")
        
        if audio_data:
            print(f"✅ 合成成功，音频大小: {len(audio_data)} 字节")
            
            # 测试系统播放器
            print("🔊 使用aplay播放...")
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                subprocess.run(["aplay", temp_file_path], check=True)
                print("✅ 播放成功！")
            except subprocess.CalledProcessError as e:
                print(f"❌ aplay播放失败: {e}")
            except FileNotFoundError:
                print("❌ aplay未找到，请安装: sudo apt-get install alsa-utils")
            finally:
                # 清理临时文件
                os.unlink(temp_file_path)
        else:
            print("❌ 音频合成失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_audio_playback()
