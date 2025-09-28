"""
语音接口模块 - 只支持GummySTT和qwen3-tts-flash
"""
import os
import io
import time
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

import pyaudio
import wave
import numpy as np
from dotenv import load_dotenv

# 阿里云DashScope导入
try:
    import dashscope
    from dashscope.audio.asr import TranslationRecognizerChat, TranslationRecognizerCallback, TranscriptionResult, TranslationResult
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False

# WebSocket导入
try:
    import websocket
    import json
    import threading
    import io
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False


class STTModel(ABC):
    """语音转文本基类"""
    
    @abstractmethod
    def transcribe(self, audio_data: bytes) -> str:
        pass


class GummySTT(STTModel):
    """阿里云Gummy一句话识别STT"""
    
    def __init__(self, api_key: str = None, model: str = "gummy-chat-v1"):
        if not DASHSCOPE_AVAILABLE:
            raise ImportError("dashscope not installed. Run: pip install dashscope")
        
        # 设置API Key
        if api_key:
            dashscope.api_key = api_key
        elif os.getenv("DASHSCOPE_API_KEY"):
            dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
        else:
            raise ValueError("DASHSCOPE_API_KEY not found. Please set it in environment or pass api_key parameter")
        
        self.model = model
        self.recognized_text = ""
        self.recognition_complete = False
        logging.info(f"Gummy STT initialized with model: {model}")
    
    def transcribe(self, audio_data: bytes) -> str:
        """使用Gummy进行语音识别"""
        self.recognized_text = ""
        self.recognition_complete = False
        
        # 创建回调类
        class GummyCallback(TranslationRecognizerCallback):
            def __init__(self, parent):
                self.parent = parent
            
            def on_open(self) -> None:
                logging.info("Gummy STT connection opened")
            
            def on_close(self) -> None:
                logging.info("Gummy STT connection closed")
            
            def on_event(self, request_id, transcription_result: TranscriptionResult, 
                        translation_result: TranslationResult, usage) -> None:
                if transcription_result is not None:
                    self.parent.recognized_text = transcription_result.text
                    if transcription_result.is_sentence_end:
                        self.parent.recognition_complete = True
                        logging.info(f"Gummy STT recognition complete: {self.parent.recognized_text}")
        
        # 创建识别器
        callback = GummyCallback(self)
        recognizer = TranslationRecognizerChat(
            model=self.model,
            format="pcm",
            sample_rate=16000,
            transcription_enabled=True,
            translation_enabled=False,  # 只做识别，不做翻译
            callback=callback,
        )
        
        try:
            # 启动识别
            recognizer.start()
            
            # 分块发送音频数据
            chunk_size = 3200  # 约100ms的音频数据
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                if not recognizer.send_audio_frame(chunk):
                    break
                if self.recognition_complete:
                    break
            
            # 停止识别
            recognizer.stop()
            
            return self.recognized_text.strip()
            
        except Exception as e:
            logging.error(f"Gummy STT recognition failed: {e}")
            return ""


class TTSModel(ABC):
    """文本转语音基类"""
    
    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        pass


class Qwen3TTSRealtime(TTSModel):
    """Qwen3 TTS Realtime模型 - 使用WebSocket连接"""
    
    def __init__(self, api_key: str = None, model: str = "qwen3-tts-flash-realtime"):
        if not WEBSOCKET_AVAILABLE:
            raise ImportError("websocket-client not installed. Run: pip install websocket-client")
        
        # 设置API Key
        if api_key:
            self.api_key = api_key
        elif os.getenv("DASHSCOPE_API_KEY"):
            self.api_key = os.getenv("DASHSCOPE_API_KEY")
        else:
            raise ValueError("DASHSCOPE_API_KEY not found. Please set it in environment or pass api_key parameter")
        
        self.model = model
        self.api_url = f"wss://dashscope.aliyuncs.com/api-ws/v1/realtime?model={model}"
        self.audio_data = b""
        self.synthesis_complete = False
        logging.info(f"Qwen3 TTS Realtime initialized with model: {model}")
    
    def synthesize(self, text: str, voice: str = "Cherry") -> bytes:
        """使用Qwen3 TTS Realtime进行语音合成"""
        try:
            self.audio_data = b""
            self.synthesis_complete = False
            
            # 创建WebSocket连接
            headers = [f"Authorization: Bearer {self.api_key}"]
            
            def on_open(ws):
                logging.info(f"Connected to TTS server: {self.api_url}")
                # 发送配置消息
                config_message = {
                    "type": "config",
                    "voice": voice,
                    "format": "wav",
                    "sample_rate": 16000
                }
                ws.send(json.dumps(config_message))
                
                # 发送文本消息
                text_message = {
                    "type": "text",
                    "text": text
                }
                ws.send(json.dumps(text_message))
                
                # 发送结束消息
                end_message = {
                    "type": "end"
                }
                ws.send(json.dumps(end_message))
            
            def on_message(ws, message):
                try:
                    data = json.loads(message)
                    logging.debug(f"Received message: {data}")
                    
                    if data.get("type") == "audio":
                        # 解码base64音频数据
                        import base64
                        audio_chunk = base64.b64decode(data["audio"])
                        self.audio_data += audio_chunk
                        logging.debug(f"Received audio chunk: {len(audio_chunk)} bytes")
                    
                    elif data.get("type") == "done":
                        self.synthesis_complete = True
                        logging.info("TTS synthesis completed")
                        ws.close()
                        
                except Exception as e:
                    logging.error(f"Error processing TTS message: {e}")
            
            def on_error(ws, error):
                logging.error(f"TTS WebSocket error: {error}")
                self.synthesis_complete = True
            
            def on_close(ws, close_status_code, close_msg):
                logging.info("TTS WebSocket connection closed")
                self.synthesis_complete = True
            
            # 创建WebSocket连接
            ws = websocket.WebSocketApp(
                self.api_url,
                header=headers,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            # 在新线程中运行WebSocket
            def run_websocket():
                ws.run_forever()
            
            thread = threading.Thread(target=run_websocket)
            thread.daemon = True
            thread.start()
            
            # 等待合成完成
            timeout = 30  # 30秒超时
            start_time = time.time()
            while not self.synthesis_complete and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if not self.synthesis_complete:
                logging.warning("TTS synthesis timeout")
                return b""
            
            return self.audio_data
                
        except Exception as e:
            logging.error(f"Qwen3 TTS Realtime synthesis failed: {e}")
            return b""


class VoiceInterface:
    """语音接口主类 - 只支持GummySTT和qwen3-tts-realtime"""
    
    def __init__(self, stt_model: STTModel = None, tts_model: TTSModel = None, voice: str = "Cherry"):
        load_dotenv()
        self.setup_logging()
        
        # 初始化STT和TTS - 程序员可以传入自定义模型
        self.stt = stt_model or self._create_stt()
        self.tts = tts_model or self._create_tts()
        self.voice = voice  # TTS音色
        
        # 音频参数
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.record_seconds = 5  # 默认录音5秒
        
        self.audio = pyaudio.PyAudio()
    
    def setup_logging(self):
        level = os.getenv("LOG_LEVEL", "INFO").upper()
        logging.basicConfig(level=level, format="%(asctime)s | %(levelname)s | %(message)s")
    
    def _create_stt(self) -> STTModel:
        """创建STT模型 - 默认使用GummySTT"""
        api_key = os.getenv("DASHSCOPE_API_KEY")
        model = os.getenv("STT_MODEL", "gummy-chat-v1")
        return GummySTT(api_key=api_key, model=model)
    
    def _create_tts(self) -> TTSModel:
        """创建TTS模型 - 默认使用qwen3-tts-flash-realtime"""
        api_key = os.getenv("DASHSCOPE_API_KEY")
        model = os.getenv("TTS_MODEL", "qwen3-tts-flash-realtime")
        return Qwen3TTSRealtime(api_key=api_key, model=model)
    
    def record_audio(self, duration: Optional[int] = None) -> bytes:
        """录制音频"""
        duration = duration or self.record_seconds
        
        print(f"🎤 开始录音 ({duration}秒)...")
        
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        frames = []
        for _ in range(0, int(self.rate / self.chunk * duration)):
            data = stream.read(self.chunk)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        
        # 将音频数据转换为WAV格式
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
        
        print("✅ 录音完成")
        return wav_buffer.getvalue()
    
    def transcribe_audio(self, audio_data: bytes) -> str:
        """将音频转换为文本"""
        print("🔄 正在识别语音...")
        start_time = time.perf_counter()
        
        text = self.stt.transcribe(audio_data)
        
        end_time = time.perf_counter()
        print(f"✅ 识别完成 ({end_time - start_time:.1f}秒): {text}")
        
        return text
    
    def synthesize_speech(self, text: str) -> bytes:
        """将文本转换为语音"""
        print("🔄 正在合成语音...")
        start_time = time.perf_counter()
        
        audio_data = self.tts.synthesize(text, voice=self.voice)
        
        end_time = time.perf_counter()
        print(f"✅ 合成完成 ({end_time - start_time:.1f}秒)")
        
        return audio_data
    
    def play_audio(self, audio_data: bytes):
        """播放音频"""
        print("🔊 正在播放...")
        
        try:
            # 从WAV数据中提取音频参数
            wav_buffer = io.BytesIO(audio_data)
            with wave.open(wav_buffer, 'rb') as wf:
                # 获取WAV文件的真实参数
                channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                framerate = wf.getframerate()
                n_frames = wf.getnframes()
                
                # 设置PyAudio格式
                if sample_width == 1:
                    format = pyaudio.paUInt8
                elif sample_width == 2:
                    format = pyaudio.paInt16
                elif sample_width == 4:
                    format = pyaudio.paInt32
                else:
                    format = pyaudio.paInt16
                
                # 打开音频流
                stream = self.audio.open(
                    format=format,
                    channels=channels,
                    rate=framerate,
                    output=True
                )
                
                # 播放音频数据
                data = wf.readframes(1024)
                while data:
                    stream.write(data)
                    data = wf.readframes(1024)
                
                stream.stop_stream()
                stream.close()
                print("✅ 播放完成")
                
        except Exception as e:
            logging.error(f"Audio playback failed: {e}")
            print(f"❌ 播放失败: {e}")
            # 尝试使用系统播放器作为备选方案
            self._fallback_play_audio(audio_data)
    
    def _fallback_play_audio(self, audio_data: bytes):
        """备选音频播放方案"""
        try:
            import tempfile
            import subprocess
            
            # 保存音频到临时文件
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # 使用系统播放器播放
            print("🔄 使用系统播放器播放...")
            subprocess.run(["aplay", temp_file_path], check=True)
            
            # 清理临时文件
            os.unlink(temp_file_path)
            print("✅ 播放完成")
            
        except Exception as e:
            logging.error(f"Fallback audio playback failed: {e}")
            print(f"❌ 备选播放也失败了: {e}")
            print("💡 建议：请检查音频设备或安装aplay: sudo apt-get install alsa-utils")
    
    def voice_to_text(self, duration: Optional[int] = None) -> str:
        """完整的语音转文本流程"""
        audio_data = self.record_audio(duration)
        return self.transcribe_audio(audio_data)
    
    def text_to_voice(self, text: str):
        """完整的文本转语音流程"""
        audio_data = self.synthesize_speech(text)
        self.play_audio(audio_data)
    
    def set_voice(self, voice: str):
        """设置TTS音色"""
        self.voice = voice
        logging.info(f"TTS voice changed to: {voice}")
    
    def get_available_voices(self) -> dict:
        """获取可用的音色列表"""
        return {
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
            "南京-老李 (li)": "li",
            "陕西-秦川 (Marcus)": "Marcus",
            "闽南-阿杰 (Roy)": "Roy",
            "天津-李彼得 (Peter)": "Peter",
            "粤语-阿强 (Rocky)": "Rocky",
            "粤语-阿清 (Kiki)": "Kiki",
            "四川-程川 (Eric)": "Eric"
        }
    
    def cleanup(self):
        """清理资源"""
        self.audio.terminate()


def test_voice_interface():
    """测试语音接口"""
    try:
        voice = VoiceInterface()
        
        print("=== 语音接口测试 ===")
        print("1. 测试语音转文本...")
        text = voice.voice_to_text(duration=3)
        print(f"识别结果: {text}")
        
        if text.strip():
            print("\n2. 测试文本转语音...")
            voice.text_to_voice(text)
        
        voice.cleanup()
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        logging.exception("Voice interface test failed")


if __name__ == "__main__":
    test_voice_interface()