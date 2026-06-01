# TokenEase - Multi-Model AI API Gateway



<div align="center">



**One API, Access to Global Top AI Models**



[English](README.md) | [中文](README_CN.md) | [Русский](README_RU.md) | [العربية](README_AR.md)



</div>



---



## 🚀 Features



- **🔥 Unified API** - One endpoint to access multiple AI models

- **💰 Pay-as-you-go** - No monthly fees, pay only what you use

- **⚡ Millisecond Response** - Optimized routing for fastest response

- **🌍 Global Access** - Works worldwide with consistent quality

- **🔒 Secure** - API keys with usage limits and monitoring



## 🤖 Supported Models



| Model | Provider | Status |

|-------|----------|--------|

| DeepSeek V4 Flash | DeepSeek | ✅ Available |

| DeepSeek V4 Pro | DeepSeek | ✅ Available |

| GLM-5.1 | ZhipuAI | ✅ Available |

| Qwen-Plus | Alibaba | ✅ Available |

| Doubao Pro | ByteDance | ✅ Available |

| Kimi | Moonshot | ✅ Available |



## 📦 Quick Start



### 1. Get Your API Key



Sign up at [tokenease.io](https://tokenease.io) to get your free API key.



### 2. Install Dependencies



bash
pip install openai requests

### 3. Make Your First Request


python
import openai

client = openai.OpenAI(
api_key="your-api-key",
base_url="https://tokenease.io/v1%22
)

response = client.chat.completions.create(
model="deepseek-chat",
messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)

## 💳 Pricing

| Plan | Price | Features |
|------|-------|----------|
| Starter | ¥9.9/mo | 1M tokens, DeepSeek V4 Flash |
| Pro | ¥29.9/mo | 10M tokens, All models |
| Enterprise | ¥399.9/mo | Unlimited, Priority support |

## 🌐 Target Markets

- **Primary**: Russia & CIS countries
- **Secondary**: Middle East (UAE, Saudi Arabia)
- **Tertiary**: Japan, Australia, Southeast Asia

## 📞 Contact

- Website: [tokenease.io](https://tokenease.io)
- Email: support@tokenease.io

---

*One API, Infinite Possibilities.*




