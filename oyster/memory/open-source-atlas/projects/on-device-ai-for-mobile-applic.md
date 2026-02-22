# OSS Scan Report: on-device-ai-for-mobile-applic

- 扫描时间: 2026-02-18T21:30:50.451421
- 方向: On-device AI for mobile applications
- 决策: **fork**
- 原因: High score (80), safe license, active — direct fork

## 候选项目

| Repo | Stars | License | Updated | Description |
|------|-------|---------|---------|-------------|
| yichuan-w/LEANN | 9,990 | mit | 2026-02-18 | RAG on Everything with LEANN. Enjoy 97% storage savings whil |
| tmoroney/auto-subs | 2,839 | mit | 2026-02-17 | Instantly generate AI-powered subtitles on your device. Work |
| jomjol/AI-on-the-edge-device | 8,081 | other | 2026-01-30 | Easy to use device for connecting "old" measuring units (wat |
| pytorch/executorch | 4,279 | other | 2026-02-18 | On-device AI across mobile, embedded and edge for PyTorch |
| adamcohenhillel/ADeus | 3,396 | other | 2024-04-22 | An open source AI wearable device that captures what you say |

## 选中

- Repo: yichuan-w/LEANN
- URL: https://github.com/yichuan-w/LEANN
- Stars: 9,990
- License: mit

## 代码结构分析
- 语言: Python
- 入口文件: pyproject.toml
- 测试目录: tests
- 关键文件: N/A

### 目录树 (depth 2)
```
.
./llms.txt
./sky
./sky/leann-build.yaml
./LICENSE
./uv.lock
./.pre-commit-config.yaml
./demo.ipynb
./pyproject.toml
./tests
./tests/test_document_rag.py
./tests/test_cli_ask.py
./tests/test_embedding_server_manager.py
./tests/test_basic.py
./tests/test_hybrid_search.py
./tests/test_prompt_template_persistence.py
./tests/test_embedding_prompt_template.py
./tests/test_sync.py
./tests/test_mcp_integration.py
./tests/test_readme_examples.py
./tests/test_metadata_filtering.py
./tests/test_mcp_standalone.py
./tests/README.md
./tests/test_cli_verbosity.py
./tests/test_cli_prompt_template.py
./tests/test_token_truncation.py
./tests/test_cpu_only_install.py
./tests/test_ci_minimal.py
./tests/test_astchunk_integration.py
./tests/test_prompt_template_e2e.py
./tests/test_diskann_partition.py
./tests/test_lmstudio_bridge.py
./docs
./docs/COLQWEN_GUIDE.md
./docs/metadata_filtering.md
./docs/faq.md
./docs/code
./docs/RELEASE.md
./docs/videos
./docs/THINKING_BUDGET_FEATURE.md
./docs/normalized_embeddings.md
./docs/roadmap.md
./docs/slack-setup-guide.md
./docs/CONTRIBUTING.md
./docs/react_agent.md
./docs/configuration-guide.md
./docs/features.md
./docs/grep_search.md
./docs/ast_chunking_guide.md
./.gitmodules
./README.md
./videos
./videos/google_clear.gif
./videos/paper_clear.gif
./videos/wechat_clear.gif
./videos/mail_clear.gif
./.gitignore
./examples
./examples/basic_demo.py
./examples/dynamic_update_no_recompute.py
./examples/__init__.py
./examples/mlx_demo.py
./examples/grep_search_example.py
./examples/mcp_integration_demo.py
./examples/spoiler_free_book_rag.py
./benchmarks
./benchmarks/financebench
./benchmarks/run_evaluation.py
./benchmarks/benchmark_embeddings.py
./benchmarks/update
./benchmarks/laion
./benchmarks/micro_tpt.py
./benchmarks/__init__.py
./benchmarks/compare_faiss_vs_leann.py
./benchmarks/README.md
./benchmarks/llm_utils.py
./benchmarks/issue_159.py
./benchmarks/benchmark_no_recompute.py
./benchmarks/enron_emails
./benchmarks/bm25_diskann_baselines
```

### README 摘要
```
<p align="center">
  <img src="assets/logo-text.png" alt="LEANN Logo" width="400">
</p>

<p align="center">
  <a href="https://trendshift.io/repositories/15049" target="_blank">
    <img src="https://trendshift.io/api/badge/repositories/15049" alt="yichuan-w/LEANN | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/>
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg" alt="Python Versions">
  <img src="https://github.com/yichuan-w/LEANN/actions/workflows/build-and-publish.yml/badge.svg" alt="CI Status">
  <img src="https://img.shields.io/badge/Platform-Ubuntu%20%26%20Arch%20%26%20WSL%20%7C%20macOS%20(ARM64%2FIntel)-lightgrey" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/MCP-Native%20Integration-blue" alt="MCP Integration">
  <a href="https://join.slack.com/t/leann-e2u9779/shared
```

