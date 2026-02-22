# Task D1: 创建环境配置文件

## 目标
创建前后端 .env 和 .env.example 文件，让开发者能快速启动。

## 文件

### 1. `backend/.env.example`
```env
# GEM Platform Backend Configuration
ENV=DEV

# Database (MySQL)
DB_HOST=localhost
DB_USER=gem
DB_PASSWD=your_password_here
DB_NAME=gem_rwa
DB_POOL_SIZE=10

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT
SECRET=change-this-to-a-random-secret-key
JWT_ALGORITHM=HS256
ID_EXP=86400

# Solana
SOL_KEY=your_solana_private_key
SOL_API_URL=https://api.devnet.solana.com

# NFT Minting
MINT_URL=https://your-mint-api.com
MINT_KEY=your_mint_api_key

# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000

# Email (SendGrid)
SENDGRID_API_KEY=your_sendgrid_key

# Twitter OAuth
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
TWITTER_REDIRECT_URI=http://localhost:3000/auth/twitter/callback

# Telegram Notifications
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Alchemy
ALCHEMY_API_KEY=your_alchemy_key
```

### 2. `backend/.env` (开发环境)
复制 .env.example 内容，SECRET 设为 `dev-secret-key-do-not-use-in-production`

### 3. `lumina/.env.example`
```env
# GEM Platform Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 4. `lumina/.env`
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 5. 确认 .gitignore
检查根目录和 backend/ 和 lumina/ 的 .gitignore 都包含 `.env`（不含 `.env.example`）。如果没有 .gitignore，创建一个。

## 验证
1. `cat backend/.env` 和 `cat lumina/.env` 文件存在
2. `.env` 在 .gitignore 中
