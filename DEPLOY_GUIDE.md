# TokenEase Vercel 部署指南

## 准备工作

1. **GitHub 账号**（已有：tokenease/tokenease）
2. **Vercel 账号**（免费注册：vercel.com）

---

## 第一步：推送代码到 GitHub

```bash
# 克隆现有仓库
git clone https://github.com/tokenease/tokenease.git
cd tokenease

# 创建 vercel 分支
git checkout -b vercel-deploy

# 将本文件夹内容复制进去
# （api/index.py, vercel.json, requirements.txt, index.html）

git add .
git commit -m "Add Vercel deployment config"
git push origin vercel-deploy
```

---

## 第二步：Vercel 导入项目

1. 打开 👉 https://vercel.com/new
2. 点 **"Import Git Repository"**
3. 选择 `tokenease/tokenease` 仓库
4. 分支选 `vercel-deploy`

---

## 第三步：配置环境变量

在 Vercel 项目设置中添加以下 **Environment Variables**：

| 变量名 | 值 |
|--------|-----|
| `DEEPSEEK_API_KEY` | `sk-746e113c61084e2b...` |
| `ZHIPU_API_KEY` | `381aa73d07414922...` |
| `QWEN_API_KEY` | `sk-07b0dc15e26949...` |
| `DOUBAO_API_KEY` | `ark-3fcd230b-2ff8...` |
| `PADDLE_WEBHOOK_SECRET` | `live_84daca0134a4b7...` |
| `SENDER_EMAIL` | `734003639@qq.com` |
| `SENDER_PASSWORD` | `QQ邮箱授权码` |

> 💡 所有密钥已保存在 `memory/tokenease/api_credentials.md`

---

## 第四步：部署

1. Framework Preset 选 **Other**
2. 点击 **Deploy**
3. 等待 1-2 分钟

---

## 第五步：配置自定义域名（可选）

1. Vercel 项目 → Settings → Domains
2. 添加 `api.tokenease.io`（可选）
3. DNS 解析指过去

---

## API 端点

部署后 API 地址为：
```
https://tokenease.vercel.app/v1/chat/completions
```

---

## 支付集成注意事项

⚠️ **Paddle Webhook** 在 Vercel Serverless 需要配置：
- Paddle 后台 → Webhooks → 添加 `https://your-domain.vercel.app/paddle-webhook`
- Vercel 免费版有 10 秒超时，Paddle webhook 需快速响应

---

## 当前服务器 vs Vercel 对比

| 对比项 | 腾讯云服务器 | Vercel |
|--------|------------|--------|
| 费用 | ¥68/月 | **免费** |
| 信用卡 | 已绑 | 无需 |
| 支付 webhook | ✅ 原生支持 | ✅ 支持 |
| 数据库 | SQLite 文件 | SQLite（/tmp）|
| 邮件发送 | ✅ 原生支持 | ✅ 支持 |
| 冷启动 | 无 | 可能有几秒 |
| 中国访问 | 有限制 | **流畅** |
| 适合规模 | 中大型 | 小中型 |

---

## 建议

**短期**：先用 Vercel 跑起来，把营销铺开
**长期**：等 Yandex 问题解决或换成 Railway/Render，再迁移回来
