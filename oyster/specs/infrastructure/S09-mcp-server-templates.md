---
task_id: S09-mcp-server-templates
project: infrastructure
priority: 2
depends_on: ["S07-oyster-mcp-typescript"]
modifies: []
executor: glm
---

## 目标
创建常用 MCP Server 模板 - Resend, Google Docs, etc.

## 约束
- 基于 @oyster-mcp/server
- 保持开源 (MIT)
- 可独立部署

## 具体改动

### 1. 创建 MCP Server 模板
在 `~/Downloads/mcp-servers/` 添加:

```
mcp-servers/
├── templates/
│   ├── resend/              # 邮件发送
│   │   ├── package.json
│   │   ├── src/
│   │   │   └── index.ts
│   │   └── README.md
│   │
│   ├── google-docs/         # Google Docs
│   │   ├── package.json
│   │   ├── src/
│   │   │   └── index.ts
│   │   └── README.md
│   │
│   ├── slack/               # Slack 集成
│   │   ├── package.json
│   │   └── src/
│   │
│   ├── notion/              # Notion 集成
│   │   ├── package.json
│   │   └── src/
│   │
│   └── playwright-browser/  # 浏览器自动化
│       ├── package.json
│       └── src/
│
└── README.md
```

### 2. Resend MCP Server (示例)

```typescript
// resend/src/index.ts
import { createMCPServer } from "@oyster-mcp/server";
import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

const server = createMCPServer("resend-mcp", {
  version: "1.0.0",
  description: "Send emails via Resend",
  env: ["RESEND_API_KEY"],
});

server.tool({
  name: "send_email",
  description: "Send an email",
  schema: z.object({
    from: z.string().email(),
    to: z.string().email(),
    subject: z.string(),
    html: z.string().optional(),
    text: z.string().optional(),
  }),
}, async ({ from, to, subject, html, text }) => {
  const result = await resend.emails.send({
    from, to, subject, html, text,
  });
  return text(JSON.stringify(result));
});

server.listen(3000);
```

### 3. Google Docs MCP Server

```typescript
server.tool({
  name: "list_documents",
  description: "List Google Docs",
}, async () => {
  const docs = await drive.files.list({ q: "mimeType='application/vnd.google-apps.document'" });
  return text(JSON.stringify(docs.data.files));
});

server.tool({
  name: "get_document",
  description: "Get document content",
  schema: z.object({
    fileId: z.string(),
  }),
}, async ({ fileId }) => {
  const doc = await docs.documents.get({ documentId: fileId });
  return text(JSON.stringify(doc.data));
});
```

### 4. Playwright Browser MCP Server

```typescript
server.tool({
  name: "navigate",
  description: "Navigate to URL",
  schema: z.object({
    url: z.string(),
  }),
}, async ({ url }, { browser }) => {
  const page = await browser.newPage();
  await page.goto(url);
  const title = await page.title();
  return text(`Navigated to ${url}, title: ${title}`);
});

server.tool({
  name: "screenshot",
  description: "Take screenshot",
  schema: z.object({
    url: z.string(),
    path: z.string().optional(),
  }),
}, async ({ url, path }, { browser }) => {
  const page = await browser.newPage();
  await page.goto(url);
  const screenshot = await page.screenshot();
  return image(screenshot);
});
```

### 5. 部署配置

```yaml
# docker-compose.yml
services:
  resend-mcp:
    build: ./templates/resend
    ports:
      - "3001:3000"
    environment:
      - RESEND_API_KEY=${RESEND_API_KEY}
    volumes:
      - /tmp/mcp-resend:/data

  google-docs-mcp:
    build: ./templates/google-docs
    ports:
      - "3002:3000"
    environment:
      - GOOGLE_SERVICE_ACCOUNT_JSON=${GOOGLE_SERVICE_ACCOUNT_JSON}
```

## 验收标准
- [ ] Resend server 可发送邮件
- [ ] Google Docs server 可读写文档
- [ ] Playwright server 可浏览器自动化
- [ ] Docker 部署成功

## 验证命令
```bash
cd ~/Downloads/mcp-servers/templates/resend
cp .env.example .env
npm install
npm run dev
# 测试: curl -X POST http://localhost:3000/tools/send_email
```

## 不要做
- 不提交 API keys
- 不修改现有 mcp-servers 结构
