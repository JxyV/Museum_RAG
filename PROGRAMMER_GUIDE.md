# 程序员语音模型选择指南

## 🎯 概述

本指南展示程序员如何在代码中自由选择STT（语音转文本）和TTS（文本转语音）模型，而不是通过配置文件让用户选择。

## 🔧 模型选择方式

### 1. 直接实例化模型

```python
from voice_interface import WhisperSTT, GummySTT, EdgeTTS, Pyttsx3TTS

# 选择STT模型
stt = WhisperSTT(model_size="base")  # 或 GummySTT, SpeechRecognitionSTT

# 选择TTS模型  
tts = EdgeTTS(voice="zh-CN-XiaoxiaoNeural")  # 或 Pyttsx3TTS

# 创建语音接口
voice = VoiceInterface(stt_model=stt, tts_model=tts)
```

### 2. 在RAG系统中选择模型

```python
# 在 multimodal_rag.py 的 _create_voice_interface 方法中
def _create_voice_interface(self) -> VoiceInterface:
    # 方案1: 高质量组合 (生产环境)
    stt = GummySTT(api_key=os.getenv("DASHSCOPE_API_KEY"))
    tts = EdgeTTS(voice="zh-CN-XiaoxiaoNeural")
    return VoiceInterface(stt_model=stt, tts_model=tts)
    
    # 方案2: 本地处理组合 (隐私敏感)
    # stt = WhisperSTT(model_size="base")
    # tts = Pyttsx3TTS(rate=200, volume=0.9)
    # return VoiceInterface(stt_model=stt, tts_model=tts)
```

## 📊 模型组合推荐

### 🏆 高质量组合 (生产环境)
```python
# 最佳识别质量 + 最佳语音合成
stt = GummySTT(api_key="your-api-key")  # 阿里云高质量识别
tts = EdgeTTS(voice="zh-CN-XiaoxiaoNeural")  # 微软自然语音
```
**优势**: 识别准确率高，语音自然流畅  
**适用**: 生产环境、商业应用

### 🔒 本地处理组合 (隐私敏感)
```python
# 完全本地处理，数据不上传
stt = WhisperSTT(model_size="base")  # 本地Whisper
tts = Pyttsx3TTS(rate=200, volume=0.9)  # 系统TTS
```
**优势**: 数据隐私安全，离线可用  
**适用**: 企业内部、隐私敏感场景

### ⚡ 快速原型组合 (开发测试)
```python
# 快速部署，易于调试
stt = SpeechRecognitionSTT(engine="google")  # 简单易用
tts = EdgeTTS(voice="zh-CN-XiaoxiaoNeural")  # 云端TTS
```
**优势**: 部署简单，调试方便  
**适用**: 原型开发、快速测试

## 🎛️ 详细配置选项

### STT模型配置

#### Whisper STT
```python
# 模型大小选择
stt = WhisperSTT(model_size="tiny")    # 最快，精度较低
stt = WhisperSTT(model_size="base")    # 平衡
stt = WhisperSTT(model_size="small")   # 较好精度
stt = WhisperSTT(model_size="medium")  # 高精度
stt = WhisperSTT(model_size="large")   # 最高精度，最慢
```

#### 阿里云Gummy STT
```python
# 需要API Key
stt = GummySTT(
    api_key="your-dashscope-api-key",
    model="gummy-chat-v1"
)
```

#### SpeechRecognition STT
```python
# 引擎选择
stt = SpeechRecognitionSTT(engine="google")  # Google识别
stt = SpeechRecognitionSTT(engine="sphinx")   # 本地Sphinx
```

### TTS模型配置

#### Edge TTS
```python
# 中文语音选择
tts = EdgeTTS(voice="zh-CN-XiaoxiaoNeural")  # 女声，温柔
tts = EdgeTTS(voice="zh-CN-YunxiNeural")    # 男声，沉稳
tts = EdgeTTS(voice="zh-CN-YunyangNeural")  # 男声，专业
```

#### Pyttsx3 TTS
```python
# 系统内置TTS
tts = Pyttsx3TTS(
    rate=200,      # 语速 (50-300)
    volume=0.9     # 音量 (0.0-1.0)
)
```

## 🚀 实际使用示例

### 示例1: 生产环境配置
```python
# 在 multimodal_rag.py 中
def _create_voice_interface(self) -> VoiceInterface:
    # 生产环境：高质量识别 + 自然语音
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if api_key:
        stt = GummySTT(api_key=api_key)
        tts = EdgeTTS(voice="zh-CN-XiaoxiaoNeural")
    else:
        # 备选方案
        stt = WhisperSTT(model_size="base")
        tts = EdgeTTS(voice="zh-CN-XiaoxiaoNeural")
    
    return VoiceInterface(stt_model=stt, tts_model=tts)
```

### 示例2: 开发环境配置
```python
# 开发环境：快速部署
def _create_voice_interface(self) -> VoiceInterface:
    stt = SpeechRecognitionSTT(engine="google")
    tts = EdgeTTS(voice="zh-CN-XiaoxiaoNeural")
    return VoiceInterface(stt_model=stt, tts_model=tts)
```

### 示例3: 隐私敏感配置
```python
# 隐私敏感：完全本地处理
def _create_voice_interface(self) -> VoiceInterface:
    stt = WhisperSTT(model_size="base")
    tts = Pyttsx3TTS(rate=200, volume=0.9)
    return VoiceInterface(stt_model=stt, tts_model=tts)
```

## 🔄 动态模型切换

```python
# 根据条件动态选择模型
def create_voice_interface(environment="production"):
    if environment == "production":
        stt = GummySTT(api_key=os.getenv("DASHSCOPE_API_KEY"))
        tts = EdgeTTS(voice="zh-CN-XiaoxiaoNeural")
    elif environment == "development":
        stt = SpeechRecognitionSTT(engine="google")
        tts = EdgeTTS(voice="zh-CN-XiaoxiaoNeural")
    else:  # local
        stt = WhisperSTT(model_size="base")
        tts = Pyttsx3TTS(rate=200, volume=0.9)
    
    return VoiceInterface(stt_model=stt, tts_model=tts)
```

## 📝 最佳实践

1. **生产环境**: 使用Gummy STT + Edge TTS
2. **开发环境**: 使用SpeechRecognition STT + Edge TTS  
3. **隐私敏感**: 使用Whisper STT + Pyttsx3 TTS
4. **性能优先**: 使用Whisper tiny + Pyttsx3 TTS
5. **质量优先**: 使用Gummy STT + Edge TTS

## 🛠️ 运行示例

```bash
# 运行语音模型选择示例
python voice_examples.py

# 运行多模态RAG（使用程序员选择的模型）
python multimodal_rag.py
```

## 💡 总结

程序员可以通过以下方式选择语音模型：

1. **直接实例化**: `VoiceInterface(stt_model=stt, tts_model=tts)`
2. **修改代码**: 在 `_create_voice_interface()` 方法中选择
3. **动态选择**: 根据环境或条件动态选择模型
4. **组合使用**: 不同场景使用不同的模型组合

这样程序员可以完全控制语音模型的选择，而不需要用户通过配置文件来选择。
