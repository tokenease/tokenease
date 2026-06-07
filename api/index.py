#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TokenEase API - Vercel Serverless Version
AI API Gateway for DeepSeek, GLM, Qwen, Doubao
"""

import os
import re
import json
import time
import random
import hashlib
import sqlite3
import smtplib
import secrets
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email import ssl as email_ssl

# ==================== 配置 ====================

# AI API Keys (from environment)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
ZHIPU_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "")
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

# Paddle 支付配置
PADDLE_WEBHOOK_SECRET = os.getenv("PADDLE_WEBHOOK_SECRET", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "734003639@qq.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465

# ==================== 数据库 (SQLite for dev, 可升级为 Turso) ====================

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "tokens.db")


def get_db_path():
    """获取数据库路径"""
    # Vercel serverless 环境使用 /tmp
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA"):
        return "/tmp/tokens.db"
    return DB_PATH


def get_db():
    """获取数据库连接"""
    path = get_db_path()
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_key TEXT UNIQUE,
            email TEXT,
            plan TEXT,
            quota INTEGER,
            paid_amount REAL,
            days_allowed INTEGER,
            payment_method TEXT,
            payment_id TEXT,
            created_at TEXT,
            expires_at TEXT,
            status TEXT DEFAULT 'active'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS webhook_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE,
            event_type TEXT,
            payment_id TEXT,
            processed_at TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_key TEXT,
            model TEXT,
            input_tokens INTEGER,
            output_tokens INTEGER,
            cost REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()


# ==================== 模型路由 ====================

MODEL_CONFIG = {
    "deepseek-chat": {"provider": "deepseek", "model": "deepseek-chat"},
    "deepseek": {"provider": "deepseek", "model": "deepseek-chat"},
    "deepseek-v4-flash": {"provider": "deepseek", "model": "deepseek-chat"},
    "deepseek-pro": {"provider": "deepseek", "model": "deepseek-pro"},
    "glm-4": {"provider": "zhipu", "model": "glm-4"},
    "glm-5.1": {"provider": "zhipu", "model": "glm-4"},
    "qwen-plus": {"provider": "qwen", "model": "qwen-plus"},
    "qwen": {"provider": "qwen", "model": "qwen-plus"},
    "doubao-pro": {"provider": "doubao", "model": "doubao-pro-32k"},
    "doubao": {"provider": "doubao", "model": "doubao-pro-32k"},
}

PROVIDER_API_KEYS = {
    "deepseek": lambda: DEEPSEEK_API_KEY,
    "zhipu": lambda: ZHIPU_API_KEY,
    "qwen": lambda: QWEN_API_KEY,
    "doubao": lambda: DOUBAO_API_KEY,
}

PROVIDER_URLS = {
    "deepseek": DEEPSEEK_API_URL,
    "zhipu": ZHIPU_API_URL,
    "qwen": QWEN_API_URL,
    "doubao": DOUBAO_API_URL,
}

PRICE_PER_1K = {
    "deepseek-chat": 0.0005,
    "deepseek-pro": 0.008,
    "glm-4": 0.008,
    "qwen-plus": 0.003,
    "doubao-pro-32k": 0.001,
}

# ==================== API Key 验证 ====================

def verify_api_key(api_key: str) -> dict:
    """验证 API Key 并返回用户信息"""
    if not api_key:
        return None
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT api_key, email, plan, quota, expires_at, status
        FROM api_keys
        WHERE api_key = ? AND status = 'active'
    ''', (api_key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        expires = datetime.fromisoformat(row["expires_at"])
        if expires > datetime.now():
            return dict(row)
    return None


def log_usage(api_key: str, model: str, input_tokens: int, output_tokens: int):
    """记录用量"""
    cost = (input_tokens + output_tokens) / 1000 * PRICE_PER_1K.get(model, 0.001)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO usage_logs (api_key, model, input_tokens, output_tokens, cost, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (api_key, model, input_tokens, output_tokens, cost, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def deduct_quota(api_key: str, tokens: int):
    """扣减配额"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE api_keys
        SET quota = quota - ?
        WHERE api_key = ?
    ''', (tokens, api_key))
    conn.commit()
    conn.close()


# ==================== AI API 代理 ====================

def route_to_provider(provider: str, model: str, messages: list, stream: bool = False,
                      temperature: float = 0.7, max_tokens: int = 2048, **kwargs):
    """路由到对应的 AI 提供商"""
    api_key = PROVIDER_API_KEYS.get(provider, lambda: "")()
    if not api_key:
        return {"error": f"Provider {provider} not configured"}

    url = PROVIDER_URLS.get(provider, "")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    # 移除 None 值
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        import urllib.request
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers=headers, method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


# ==================== Vercel Handler ====================

def handler(event, context):
    """Vercel Python handler"""
    path = event.get("path", "/")
    method = event.get("httpMethod", "GET")
    headers = event.get("headers", {})
    body_raw = event.get("body", "")

    # CORS headers
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Authorization, Content-Type, X-API-Key",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    }

    # 初始化数据库
    init_db()

    # OPTIONS 预检
    if method == "OPTIONS":
        return {"statusCode": 200, "headers": cors_headers, "body": ""}

    # 路由
    if path == "/v1/chat/completions" and method == "POST":
        return handle_chat_completions(event, cors_headers)
    elif path == "/v1/models" and method == "GET":
        return handle_models(event, cors_headers)
    elif path == "/health" and method == "GET":
        return handle_health(event, cors_headers)
    elif path == "/plans" and method == "GET":
        return handle_plans(event, cors_headers)
    elif path == "/paddle-webhook" and method == "POST":
        return handle_paddle_webhook(event, cors_headers)
    elif path == "/register" and method == "POST":
        return handle_register(event, cors_headers)
    else:
        return {
            "statusCode": 404,
            "headers": cors_headers,
            "body": json.dumps({"error": "Not found"}),
        }


# ==================== 路由处理函数 ====================

def handle_chat_completions(event, headers):
    """处理 OpenAI 格式的 chat completions"""
    try:
        body = json.loads(event.get("body", "{}"))
    except:
        return {"statusCode": 400, "headers": headers, "body": json.dumps({"error": "Invalid JSON"})}

    # 获取 API Key
    auth = event.get("headers", {}).get("authorization", "")
    api_key = auth.replace("Bearer ", "") if auth.startswith("Bearer ") else ""

    # 也支持 X-API-Key
    if not api_key:
        api_key = event.get("headers", {}).get("x-api-key", "")

    user = verify_api_key(api_key)
    if not user:
        return {"statusCode": 401, "headers": headers, "body": json.dumps({"error": "Invalid API key"})}

    model_input = body.get("model", "deepseek-chat")
    messages = body.get("messages", [])
    stream = body.get("stream", False)
    temperature = body.get("temperature", 0.7)
    max_tokens = body.get("max_tokens", 2048)

    # 路由
    config = MODEL_CONFIG.get(model_input, {"provider": "deepseek", "model": "deepseek-chat"})
    provider = config["provider"]
    model = config["model"]

    result = route_to_provider(provider, model, messages, stream, temperature, max_tokens)

    if "error" in result:
        return {"statusCode": 500, "headers": headers, "body": json.dumps(result)}

    # 记录用量（估算）
    usage = result.get("usage", {})
    input_t = usage.get("prompt_tokens", 0)
    output_t = usage.get("completion_tokens", 0)
    if input_t or output_t:
        log_usage(api_key, model, input_t, output_t)

    return {"statusCode": 200, "headers": headers, "body": json.dumps(result)}


def handle_models(event, headers):
    """返回模型列表"""
    models = [
        {"id": "deepseek-chat", "object": "model", "created": 1700000000, "owned_by": "deepseek"},
        {"id": "deepseek-pro", "object": "model", "created": 1700000000, "owned_by": "deepseek"},
        {"id": "glm-4", "object": "model", "created": 1700000000, "owned_by": "zhipu"},
        {"id": "qwen-plus", "object": "model", "created": 1700000000, "owned_by": "alibaba"},
        {"id": "doubao-pro-32k", "object": "model", "created": 1700000000, "owned_by": "bytedance"},
    ]
    return {"statusCode": 200, "headers": headers, "body": json.dumps({"object": "list", "data": models})}


def handle_health(event, headers):
    """健康检查"""
    return {"statusCode": 200, "headers": headers, "body": json.dumps({"status": "ok", "service": "TokenEase"})}


def handle_plans(event, headers):
    """返回套餐信息"""
    plans = [
        {"id": "starter", "name": "Starter", "price": 9.9, "currency": "CNY",
         "quota": 30000, "period": "month", "features": ["DeepSeek V4 Flash", "GLM-4", "Qwen-Plus", "Doubao Pro"]},
        {"id": "pro", "name": "Pro", "price": 29.9, "currency": "CNY",
         "quota": 100000, "period": "month", "features": ["All models", "Priority support", "99.9% uptime"]},
        {"id": "enterprise", "name": "Enterprise", "price": 99.9, "currency": "CNY",
         "quota": 500000, "period": "month", "features": ["All models", "Dedicated support", "Custom limits"]},
    ]
    return {"statusCode": 200, "headers": headers, "body": json.dumps(plans)}


def handle_register(event, headers):
    """免费注册 - 发放 1M tokens"""
    try:
        body = json.loads(event.get("body", "{}"))
    except:
        return {"statusCode": 400, "headers": headers, "body": json.dumps({"error": "Invalid JSON"})}

    email = body.get("email", "").strip()
    if not email or "@" not in email:
        return {"statusCode": 400, "headers": headers, "body": json.dumps({"error": "Invalid email"})}

    api_key = f"tk_{secrets.token_urlsafe(32)}"
    expires = datetime.now() + timedelta(days=365)  # 1年有效期

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO api_keys
        (api_key, email, plan, quota, paid_amount, days_allowed, payment_method, payment_id, created_at, expires_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (api_key, email, "free", 1000000, 0, 365, "bonus", "free_register",
          datetime.now().isoformat(), expires.isoformat(), "active"))
    conn.commit()
    conn.close()

    return {"statusCode": 200, "headers": headers,
            "body": json.dumps({"api_key": api_key, "quota": 1000000, "expires_at": expires.isoformat()})}


def handle_paddle_webhook(event, headers):
    """处理 Paddle 支付回调"""
    try:
        body = event.get("body", "")
        signature = event.get("headers", {}).get("paddle-signature", "")

        import hmac
        expected = hmac.new(
            PADDLE_WEBHOOK_SECRET.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()
        actual_sig = signature.split(",")[0] if "," in signature else signature

        if not hmac.compare_digest(actual_sig, f"v1={expected}"):
            return {"statusCode": 403, "headers": headers, "body": json.dumps({"error": "Invalid signature"})}

        data = json.loads(body)
        event_type = data.get("event_type", "")
        payload = data.get("data", {}).get("attributes", {})
        email = payload.get("custom_data", {}).get("email", "")
        plan = payload.get("custom_data", {}).get("plan", "starter")

        # 生成 API Key
        api_key = f"tk_{secrets.token_urlsafe(32)}"
        amount = float(payload.get("amount", 0))
        days = int(amount / 1)  # 1元=1天
        expires = datetime.now() + timedelta(days=max(days, 30))
        quota_map = {"starter": 30000, "pro": 100000, "enterprise": 500000}
        quota = quota_map.get(plan, 30000)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO api_keys
            (api_key, email, plan, quota, paid_amount, days_allowed, payment_method, payment_id, created_at, expires_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (api_key, email, plan, quota, amount, days, "paddle", payload.get("id", ""),
              datetime.now().isoformat(), expires.isoformat(), "active"))
        conn.commit()
        conn.close()

        # 发送邮件
        send_api_key_email(email, api_key, plan, days, expires, amount)

        return {"statusCode": 200, "headers": headers, "body": json.dumps({"success": True})}

    except Exception as e:
        return {"statusCode": 500, "headers": headers, "body": json.dumps({"error": str(e)})}


def send_api_key_email(to_email, api_key, plan, days, expires, amount):
    """发送 API Key 邮件"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header('🎉 您的 TokenEase API Key 已开通！', 'utf-8')
        msg['From'] = f'TokenEase <{SENDER_EMAIL}>'
        msg['To'] = to_email

        text = f"""您好！

感谢您的付款！您的 API Key 已成功开通！

📧 邮箱: {to_email}
🔑 API Key: {api_key}
📦 套餐: {plan.capitalize()}
💰 付款金额: ${amount:.2f}
📅 使用期限: {days} 天
⏰ 过期时间: {expires.strftime('%Y-%m-%d')}

👉 开始使用: https://tokenease.io/api-docs

- TokenEase 团队
"""
        msg.attach(MIMEText(text, 'plain', 'utf-8'))

        context = email_ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
    except Exception as e:
        print(f"Email error: {e}")
