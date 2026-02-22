# Task D2: 后端依赖补齐

## 目标
修复 requirements.txt 中缺失的依赖。

## 文件
- `backend/requirements.txt`

## 具体改动

在 requirements.txt 末尾添加:
```
slowapi
```

`slowapi` 在 `backend/app/app.py` 中被 import 使用（用于 rate limiting），但未列在 requirements.txt 中。

## 验证
1. `grep slowapi backend/requirements.txt` — 确认存在
2. `cd backend && pip install slowapi` — 确认可安装
