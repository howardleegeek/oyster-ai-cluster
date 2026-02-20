# OSS Scan Report: ai-powered-web-crawling-for-co

- 扫描时间: 2026-02-18T21:31:05.551298
- 方向: AI-powered web crawling for content generation
- 决策: **fork**
- 原因: High score (90), safe license, active — direct fork

## 候选项目

| Repo | Stars | License | Updated | Description |
|------|-------|---------|---------|-------------|
| dzhng/deep-research | 18,457 | mit | 2025-09-08 | An AI-powered research assistant that performs iterative, de |
| nanobrowser/nanobrowser | 12,251 | apache-2.0 | 2025-11-24 | Open-Source Chrome extension for AI-powered web automation.  |
| apurvsinghgautam/robin | 4,232 | mit | 2026-02-17 | AI-Powered Dark Web OSINT Tool |
| photoprism/photoprism | 39,288 | other | 2026-02-18 | AI-Powered Photos App for the Decentralized Web 🌈💎✨ |
| pluja/whishper | 2,917 | agpl-3.0 | 2025-08-15 | Transcribe any audio to text, translate and edit subtitles 1 |

## 选中

- Repo: dzhng/deep-research
- URL: https://github.com/dzhng/deep-research
- Stars: 18,457
- License: mit

## 代码结构分析
- 语言: JavaScript/TypeScript
- 入口文件: package.json
- 测试目录: 
- 关键文件: src/api.ts, src/deep-research.ts, src/feedback.ts, src/prompt.ts, src/run.ts

### 目录树 (depth 2)
```
.
./LICENSE
./report.md
./Dockerfile
./.prettierignore
./README.md
./prettier.config.mjs
./.gitignore
./package-lock.json
./package.json
./.nvmrc
./tsconfig.json
./docker-compose.yml
./.env.example
./.git
./src
./src/prompt.ts
./src/api.ts
./src/ai
./src/feedback.ts
./src/deep-research.ts
./src/run.ts
```

### README 摘要
```
# Open Deep Research

An AI-powered research assistant that performs iterative, deep research on any topic by combining search engines, web scraping, and large language models.

The goal of this repo is to provide the simplest implementation of a deep research agent - e.g. an agent that can refine its research direction over time and deep dive into a topic. Goal is to keep the repo size at <500 LoC so it is easy to understand and build on top of.

If you like this project, please consider starring it and giving me a follow on [X/Twitter](https://x.com/dzhng). This project is sponsored by [Aomni](https://aomni.com).

## How It Works

```mermaid
flowchart TB
    subgraph Input
        Q[User Query]
        B[Breadth Parameter]
        D[Depth Parameter]
    end

    DR[Deep Research] -->
    SQ[SERP Queries] -->
```

