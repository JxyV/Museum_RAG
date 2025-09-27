"""
语音接口模块 - 支持多种STT和TTS模型
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

# STT 模型导入
# try:
#     import whisper
#     WHISPER_AVAILABLE = True
# except ImportError:
#     WHISPER_AVAILABLE = False

# try:
#     from speech_recognition import AudioData, Recognizer, Microphone
#     SPEECH_RECOGNITION_AVAILABLE = True
# except ImportError:
#     SPEECH_RECOGNITION_AVAILABLE = False

# TTS 模型导入
# try:
#     import edge_tts
#     EDGE_TTS_AVAILABLE = True
# except ImportError:
#     EDGE_TTS_AVAILABLE = False

# try:
#     from TTS.api import TTS
#     COQUI_TTS_AVAILABLE = True
# except ImportError:
#     COQUI_TTS_AVAILABLE = False

# try:
#     import pyttsx3
#     PYTTSX3_AVAILABLE = True
# except ImportError:
#     PYTTSX3_AVAILABLE = False


class STTModel(ABC):
    """语音转文本基类"""
    
    @abstractmethod
    def transcribe(self, audio_data: bytes) -> str:
        pass


class WhisperSTT(STTModel):
    """Whisper STT模型"""
    
    def __init__(self, model_size: str = "base"):
        if not WHISPER_AVAILABLE:
            raise ImportError("whisper not installed. Run: pip install openai-whisper")
        
        self.model = whisper.load_model(model_size)
        logging.info(f"Whisper model {model_size} loaded")
    
    def transcribe(self, audio_data: bytes) -> str:
        # 将音频数据保存为临时文件
        temp_file = "temp_audio.wav"
        with open(temp_file, "wb") as f:
            f.write(audio_data)
        
        try:
            result = self.model.transcribe(temp_file, language="zh")
            return result["text"].strip()
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)


class SpeechRecognitionSTT(STTModel):
    """使用speech_recognition库的STT"""
    
    def __init__(self, engine: str = "google"):
        if not SPEECH_RECOGNITION_AVAILABLE:
            raise ImportError("speech_recognition not installed. Run: pip install SpeechRecognition")
        
        self.recognizer = Recognizer()
        self.engine = engine
        logging.info(f"SpeechRecognition STT initialized with {engine}")
    
    def transcribe(self, audio_data: bytes) -> str:
        # 将bytes转换为AudioData对象
        audio = AudioData(audio_data, 16000, 2)  # 假设16kHz, 16bit
        
        try:
            if self.engine == "google":
                text = self.recognizer.recognize_google(audio, language="zh-CN")
            elif self.engine == "sphinx":
                text = self.recognizer.recognize_sphinx(audio)
            else:
                text = self.recognizer.recognize_google(audio, language="zh-CN")
            
            return text.strip()
        except Exception as e:
            logging.error(f"STT recognition failed: {e}")
            return ""


class TTSModel(ABC):
    """文本转语音基类"""
    
    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        pass


class EdgeTTS(TTSModel):
    """Edge TTS模型"""
    
    def __init__(self, voice: str = "zh-CN-XiaoxiaoNeural"):
        if not EDGE_TTS_AVAILABLE:
            raise ImportError("edge-tts not installed. Run: pip install edge-tts")
        
        self.voice = voice
        logging.info(f"Edge TTS initialized with voice: {voice}")
    
    def synthesize(self, text: str) -> bytes:
        import asyncio
        
        async def _synthesize():
            communicate = edge_tts.Communicate(text, self.voice)
            return await communicate.as_bytes()
        
        return asyncio.run(_synthesize())


class CoquiTTS(TTSModel):
    """Coqui TTS模型"""
    
    def __init__(self, model_name: str = "tts_models/zh-CN/baker/tacotron2-DDC-GST"):
        if not COQUI_TTS_AVAILABLE:
            raise ImportError("TTS not installed. Run: pip install TTS")
        
        self.tts = TTS(model_name)
        logging.info(f"Coqui TTS initialized with model: {model_name}")
    
    def synthesize(self, text: str) -> bytes:
        # 生成音频文件
        temp_file = "temp_output.wav"
        self.tts.tts_to_file(text=text, file_path=temp_file)
        
        try:
            with open(temp_file, "rb") as f:
                audio_data = f.read()
            return audio_data
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


class Pyttsx3TTS(TTSModel):
    """Pyttsx3 TTS模型（系统内置）"""
    
    def __init__(self, rate: int = 200, volume: float = 0.9):
        if not PYTTSX3_AVAILABLE:
            raise ImportError("pyttsx3 not installed. Run: pip install pyttsx3")
        
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        
        # 设置中文语音
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'chinese' in voice.name.lower() or 'zh' in voice.id.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        logging.info("Pyttsx3 TTS initialized")
    
    def synthesize(self, text: str) -> bytes:
        # Pyttsx3 不直接返回音频数据，需要特殊处理
        # 这里简化处理，实际使用时可能需要保存到文件
        temp_file = "temp_pyttsx3.wav"
        self.engine.save_to_file(text, temp_file)
        self.engine.runAndWait()
        
        try:
            with open(temp_file, "rb") as f:
                audio_data = f.read()
            return audio_data
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


class VoiceInterface:
    """语音接口主类"""
    
    def __init__(self):
        load_dotenv()
        self.setup_logging()
        
        # 初始化STT和TTS
        self.stt = self._create_stt()
        self.tts = self._create_tts()
        
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
        stt_backend = os.getenv("STT_BACKEND", "whisper").lower()
        stt_model = os.getenv("STT_MODEL", "base")
        
        if stt_backend == "whisper":
            return WhisperSTT(model_size=stt_model)
        elif stt_backend == "speech_recognition":
            engine = os.getenv("STT_ENGINE", "google")
            return SpeechRecognitionSTT(engine=engine)
        else:
            raise ValueError(f"Unsupported STT backend: {stt_backend}")
    
    def _create_tts(self) -> TTSModel:
        tts_backend = os.getenv("TTS_BACKEND", "edge").lower()
        
        if tts_backend == "edge":
            voice = os.getenv("TTS_VOICE", "zh-CN-XiaoxiaoNeural")
            return EdgeTTS(voice=voice)
        elif tts_backend == "coqui":
            model = os.getenv("TTS_MODEL", "tts_models/zh-CN/baker/tacotron2-DDC-GST")
            return CoquiTTS(model_name=model)
        elif tts_backend == "pyttsx3":
            rate = int(os.getenv("TTS_RATE", "200"))
            volume = float(os.getenv("TTS_VOLUME", "0.9"))
            return Pyttsx3TTS(rate=rate, volume=volume)
        else:
            raise ValueError(f"Unsupported TTS backend: {tts_backend}")
    
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
        
        audio_data = self.tts.synthesize(text)
        
        end_time = time.perf_counter()
        print(f"✅ 合成完成 ({end_time - start_time:.1f}秒)")
        
        return audio_data
    
    def play_audio(self, audio_data: bytes):
        """播放音频"""
        print("🔊 正在播放...")
        
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True
        )
        
        # 从WAV数据中提取音频帧
        wav_buffer = io.BytesIO(audio_data)
        with wave.open(wav_buffer, 'rb') as wf:
            data = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)
        
        stream.stop_stream()
        stream.close()
        print("✅ 播放完成")
    
    def voice_to_text(self, duration: Optional[int] = None) -> str:
        """完整的语音转文本流程"""
        audio_data = self.record_audio(duration)
        return self.transcribe_audio(audio_data)
    
    def text_to_voice(self, text: str):
        """完整的文本转语音流程"""
        audio_data = self.synthesize_speech(text)
        self.play_audio(audio_data)
    
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
