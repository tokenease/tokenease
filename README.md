# TokenEase — Unified AI API Gateway

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![OpenAI Compatible](https://img.shields.io/badge/OpenAI-Compatible-brightgreen.svg)](https://platform.openai.com/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Server-yellow.svg)](https://modelcontextprotocol.io/)

**One API Key. Multiple AI Models. OpenAI-Compatible Format.**

[English](README.md) · [中文](README_CN.md) · [Русский](README_RU.md) · [العربية](README_AR.md)

**[tokenease.io](https://tokenease.io)** · **[Get API Key](https://tokenease.io/register.html)** · **[Documentation](https://tokenease.io/docs.html)**

---

## Why TokenEase?

> **Stop managing multiple API keys. Start building.**

Every AI model has its own API. DeepSeek. GLM. Qwen. Doubao. Kaiwu. All different keys, different endpoints, different rate limits. TokenEase solves this — **one API key, one endpoint, all models**.

| Without TokenEase | With TokenEase |
|---|---|
| 5+ API keys to manage | 1 API key |
| 5+ different base URLs | `https://tokenease.io/v1` |
| 5+ SDKs to integrate | Standard OpenAI SDK |
| 5+ dashboards to check | 1 unified dashboard |

---

## 🤖 Supported Models

| Model | Provider | Best For | Context | Price |
|-------|----------|----------|---------|-------|
| **DeepSeek V4 Flash** | DeepSeek | Chat, content, fast tasks | 128K | $0.5/1M tokens |
| **DeepSeek V4 Pro** | DeepSeek | Complex reasoning, code | 128K | $8/1M tokens |
| **GLM-5.1** | ZhipuAI | Chinese language, RAG | 128K | $8/1M tokens |
| **Qwen-Plus** | Alibaba | Creative, multilingual | 131K | $3/1M tokens |
| **Doubao Pro** | ByteDance | Conversational AI | 256K | $1/1M tokens |

---

## 🚀 Quick Start

### 1. Get Your API Key

👉 **[Sign up free at tokenease.io](https://tokenease.io/register.html)** — API key ready in 30 seconds

### 2. Install OpenAI SDK


bash
pip install openai

### 3. Make Your First Request


python
from openai import OpenAI

client = OpenAI(
api_key="YOUR_TOKENEASE_KEY",
base_url="https://tokenease.io/v1%22
)
Call DeepSeek

response = client.chat.completions.create(
model="deepseek-chat",
messages=[{"role": "user", "content": "Explain quantum computing in simple terms"}]
)
print(response.choices[0].message.content)

### 4. cURL



bash
curl https://tokenease.io/v1/chat/completions 
-H "Authorization: Bearer YOUR_API_KEY" 
-H "Content-Type: application/json" 
-d '{"model": "deepseek-chat", "messages": [{"role": "user", "content": "Hello!"}]}'

---

## 🧩 AI Agent Integration

### MCP Server (Model Context Protocol)

Add TokenEase to your AI agent:


bash
Claude Desktop

claude mcp add tokenease -y -- npx -y @modelcontextprotocol/server-tokenease
export TOKENEASE_API_KEY="your-tokenease-key"


### For LangChain / LangGraph



python
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(
model="deepseek-chat",
openai_api_key=os.environ["TOKENEASE_API_KEY"],
openai_api_base="https://tokenease.io/v1%22
)


---

## 📊 Use Cases

| Use Case | Recommended Model | Why |
|----------|-------------------|-----|
| Customer service chatbot | DeepSeek Flash | Fast, affordable |
| Chinese content generation | GLM-5.1 | Best Chinese understanding |
| Code generation | DeepSeek Pro | Strong reasoning |
| Long document analysis | Doubao Pro | 256K context window |

---

## 💳 Pricing

| Plan | Monthly | Tokens | Models |
|------|---------|--------|--------|
| **Starter** | ¥9.9 (~$1.4) | 1M tokens/mo | DeepSeek Flash, GLM |
| **Pro** | ¥29.9 (~$4) | 5M tokens/mo | All models |
| **Enterprise** | ¥399.9 (~$55) | 20M tokens/mo | All + SLA |

**Payment Methods:** Payoneer, PayPal, bank transfer (USD/CNY/RUB)

---

## 🌐 Target Markets

| Region | Priority |
|--------|----------|
| 🇨🇳 China | P0 |
| 🇷🇺 Russia & CIS | P0 |
| 🇺🇸 USA & Europe | P1 |
| 🇸🇬 Southeast Asia | P1 |

---

## 🔒 Security

- API keys with granular permissions
- Usage rate limiting per key
- Real-time usage monitoring
- HTTPS/TLS encryption

---

## 📚 Documentation

- **[API Docs](https://tokenease.io/docs.html)** — Full API reference
- **[Get Started](https://tokenease.io/register.html)** — Sign up in 30 seconds
- **[Examples](https://github.com/tokenease/tokenease/tree/main/examples)** — Python, JavaScript examples

---

## 📞 Contact

- 🌐 **Website:** [tokenease.io](https://tokenease.io)
- 💬 **Support:** support@tokenease.io
- 🐛 **Issues:** [GitHub Issues](https://github.com/tokenease/tokenease/issues)

---

<div align="center">

**One API. Infinite Models. Zero Complexity.**

*Built for developers, by developers.*

</div>






