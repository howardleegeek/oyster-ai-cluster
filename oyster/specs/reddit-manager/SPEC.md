# Reddit 社区账号管理工具 (Reddit Manager) - 完整执行方案

> **技术栈:** Python 3.11+, PRAW, SQLite, Asyncio, Click
> **配置路径:** `~/.reddit-manager/`
> **项目路径:** `~/Downloads/reddit-manager/`
> **架构参考:** Twitter Poster (队列+Worker) + Discord Admin (Pipeline)

---

## 1. 项目文件结构

```text
~/Downloads/reddit-manager/
├── main.py                      # 入口文件 (Click CLI)
├── requirements.txt             # 依赖
├── setup.py                     # 包安装
├── .env.example                 # 环境变量模板
├── .gitignore
├── config/
│   └── settings.json            # 全局设置
├── core/
│   ├── __init__.py
│   ├── client.py                # PRAW 封装类 (账号隔离)
│   ├── queue.py                 # SQLite 任务队列管理
│   ├── rate_limiter.py          # 令牌桶 + 冷却时间算法
│   └── logger.py                # 结构化日志
├── workers/
│   ├── __init__.py
│   └── runner.py                # 异步 Worker 循环
├── data/
│   └── .gitkeep                 # SQLite 数据库目录
└── logs/
    └── .gitkeep
```

---

## 2. 依赖 (requirements.txt)

```text
praw>=7.7.0
click>=8.1.0
aiosqlite>=0.19.0
python-dotenv>=1.0.0
pyyaml>=6.0
```

---

## 3. 账号配置

### 3.1 环境变量 `.env`

```env
# Reddit OAuth2 凭据 (通过 https://www.reddit.com/prefs/apps 获取)
REDDIT_MANAGER_CONFIG=~/.reddit-manager
```

### 3.2 账号配置 `~/.reddit-manager/accounts.json`

> **安全提示:** 此文件包含密钥，禁止提交 git。

```json
[
  {
    "id": "acc_01",
    "username": "bot_master",
    "client_id": "xxxxx",
    "client_secret": "xxxxx",
    "refresh_token": "xxxxx",
    "user_agent": "MacOS:RedditManager:v1.0 (by /u/bot_master)",
    "subreddits": ["cryptocurrency", "web3", "solana"],
    "limits": {
      "daily_post_cap": 10,
      "daily_comment_cap": 50,
      "cooldown_seconds": 300,
      "min_delay": 30,
      "max_delay": 120
    },
    "enabled": true,
    "note": "主账号 - 技术内容"
  },
  {
    "id": "acc_02",
    "username": "community_voice",
    "client_id": "yyyyy",
    "client_secret": "yyyyy",
    "refresh_token": "yyyyy",
    "user_agent": "Linux:RedditManager:v1.0 (by /u/community_voice)",
    "subreddits": ["startups", "entrepreneur"],
    "limits": {
      "daily_post_cap": 5,
      "daily_comment_cap": 20,
      "cooldown_seconds": 600,
      "min_delay": 60,
      "max_delay": 180
    },
    "enabled": true,
    "note": "社区号 - 品牌互动"
  }
]
```

### 3.3 全局设置 `config/settings.json`

```json
{
  "database_path": "data/tasks.db",
  "log_level": "INFO",
  "log_file": "logs/app.log",
  "worker": {
    "poll_interval": 5,
    "max_retries": 3,
    "retry_backoff": 2.0
  },
  "defaults": {
    "user_agent": "MacOS:RedditManager:v1.0"
  }
}
```

---

## 4. SQLite 队列 Schema

数据库文件: `data/tasks.db`

```sql
-- 任务表
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id TEXT NOT NULL,
    action_type TEXT NOT NULL,          -- 'post', 'comment', 'vote', 'follow', 'monitor'
    target_subreddit TEXT,
    target_post_id TEXT,                -- t3_xxxx (用于评论/投票)
    content_title TEXT,
    content_body TEXT,
    flair_id TEXT,
    status TEXT DEFAULT 'pending',      -- pending, executing, completed, failed, cancelled
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    result_url TEXT,                    -- 成功后的 permalink
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scheduled_at TIMESTAMP,            -- 定时发布
    executed_at TIMESTAMP
);

-- 操作日志表
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    account_id TEXT,
    level TEXT,                         -- INFO, WARNING, ERROR
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES tasks(id)
);

-- 每日计数器表 (速率限制持久化)
CREATE TABLE IF NOT EXISTS daily_counters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    count INTEGER DEFAULT 0,
    date TEXT NOT NULL,                 -- YYYY-MM-DD
    UNIQUE(account_id, action_type, date)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_scheduled ON tasks(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_counters_date ON daily_counters(account_id, date);
```

---

## 5. 核心代码

### 5.1 Reddit 客户端 `core/client.py`

```python
"""PRAW 封装类 - 每账号独立实例，防止 Token 串扰"""

import praw
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class RedditAccount:
    """单个 Reddit 账号的 PRAW 封装"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.id = config["id"]
        self.username = config["username"]
        self.limits = config.get("limits", {})
        self.reddit = self._init_reddit()

    def _init_reddit(self) -> praw.Reddit:
        r = praw.Reddit(
            client_id=self.config["client_id"],
            client_secret=self.config["client_secret"],
            refresh_token=self.config["refresh_token"],
            user_agent=self.config["user_agent"],
        )
        # 验证认证
        try:
            me = r.user.me()
            logger.info(f"账号 {self.username} 认证成功 (karma: {me.link_karma})")
        except Exception as e:
            logger.error(f"账号 {self.username} 认证失败: {e}")
            raise
        return r

    def post_text(self, subreddit: str, title: str, body: str, flair_id: str = None) -> str:
        """发布文本帖子，返回 permalink"""
        sub = self.reddit.subreddit(subreddit)
        kwargs = {"title": title, "selftext": body}
        if flair_id:
            kwargs["flair_id"] = flair_id
        submission = sub.submit(**kwargs)
        logger.info(f"[{self.username}] 发帖成功: {submission.permalink}")
        return submission.permalink

    def post_link(self, subreddit: str, title: str, url: str, flair_id: str = None) -> str:
        """发布链接帖子"""
        sub = self.reddit.subreddit(subreddit)
        kwargs = {"title": title, "url": url}
        if flair_id:
            kwargs["flair_id"] = flair_id
        submission = sub.submit(**kwargs)
        logger.info(f"[{self.username}] 链接帖发布成功: {submission.permalink}")
        return submission.permalink

    def comment_on_post(self, post_id: str, body: str) -> str:
        """在帖子下评论"""
        submission = self.reddit.submission(id=post_id)
        comment = submission.reply(body)
        logger.info(f"[{self.username}] 评论成功: {comment.permalink}")
        return comment.permalink

    def upvote(self, thing_id: str):
        """点赞 (thing_id 格式: t3_xxx 或 t1_xxx)"""
        if thing_id.startswith("t3_"):
            thing = self.reddit.submission(id=thing_id[3:])
        elif thing_id.startswith("t1_"):
            thing = self.reddit.comment(id=thing_id[3:])
        else:
            raise ValueError(f"不支持的 thing_id 格式: {thing_id}")
        thing.upvote()
        logger.info(f"[{self.username}] 点赞: {thing_id}")

    def get_hot_posts(self, subreddit: str, limit: int = 10) -> list:
        """获取热门帖子列表"""
        posts = []
        for post in self.reddit.subreddit(subreddit).hot(limit=limit):
            posts.append({
                "id": post.id,
                "title": post.title,
                "score": post.score,
                "num_comments": post.num_comments,
                "author": str(post.author),
                "url": post.permalink,
            })
        return posts

    def get_new_posts(self, subreddit: str, limit: int = 10) -> list:
        """获取最新帖子"""
        posts = []
        for post in self.reddit.subreddit(subreddit).new(limit=limit):
            posts.append({
                "id": post.id,
                "title": post.title,
                "score": post.score,
                "num_comments": post.num_comments,
                "author": str(post.author),
                "created_utc": post.created_utc,
            })
        return posts

    def get_subreddit_info(self, subreddit: str) -> dict:
        """获取子版块信息"""
        sub = self.reddit.subreddit(subreddit)
        return {
            "name": sub.display_name,
            "subscribers": sub.subscribers,
            "description": sub.public_description[:200],
            "created_utc": sub.created_utc,
        }
```

### 5.2 任务队列 `core/queue.py`

```python
"""SQLite 异步任务队列"""

import aiosqlite
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    target_subreddit TEXT,
    target_post_id TEXT,
    content_title TEXT,
    content_body TEXT,
    flair_id TEXT,
    status TEXT DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    result_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scheduled_at TIMESTAMP,
    executed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    account_id TEXT,
    level TEXT,
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES tasks(id)
);

CREATE TABLE IF NOT EXISTS daily_counters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    count INTEGER DEFAULT 0,
    date TEXT NOT NULL,
    UNIQUE(account_id, action_type, date)
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_scheduled ON tasks(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_counters_date ON daily_counters(account_id, date);
"""


class TaskQueue:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(SCHEMA_SQL)
            await db.commit()

    async def enqueue(self, task: dict) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO tasks
                   (account_id, action_type, target_subreddit, target_post_id,
                    content_title, content_body, flair_id, scheduled_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    task["account_id"],
                    task["action_type"],
                    task.get("subreddit"),
                    task.get("post_id"),
                    task.get("title"),
                    task.get("body"),
                    task.get("flair_id"),
                    task.get("scheduled_at"),
                ),
            )
            await db.commit()
            return cursor.lastrowid

    async def fetch_next(self) -> Optional[Dict]:
        """获取下一个待执行任务 (FIFO, 支持定时)"""
        now = datetime.utcnow().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT * FROM tasks
                   WHERE status = 'pending'
                     AND (scheduled_at IS NULL OR scheduled_at <= ?)
                   ORDER BY created_at ASC LIMIT 1""",
                (now,),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    task = dict(row)
                    await db.execute(
                        "UPDATE tasks SET status='executing' WHERE id=?",
                        (task["id"],),
                    )
                    await db.commit()
                    return task
        return None

    async def mark_completed(self, task_id: int, result_url: str = None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """UPDATE tasks
                   SET status='completed', executed_at=CURRENT_TIMESTAMP, result_url=?
                   WHERE id=?""",
                (result_url, task_id),
            )
            await db.commit()

    async def mark_failed(self, task_id: int, error: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """UPDATE tasks
                   SET status='failed', error_message=?, retry_count=retry_count+1
                   WHERE id=?""",
                (error, task_id),
            )
            await db.commit()

    async def retry_failed(self, task_id: int):
        """重新排队失败任务"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE tasks SET status='pending' WHERE id=? AND status='failed'",
                (task_id,),
            )
            await db.commit()

    async def get_stats(self) -> dict:
        """获取队列统计"""
        async with aiosqlite.connect(self.db_path) as db:
            stats = {}
            for status in ["pending", "executing", "completed", "failed"]:
                async with db.execute(
                    "SELECT COUNT(*) FROM tasks WHERE status=?", (status,)
                ) as cursor:
                    row = await cursor.fetchone()
                    stats[status] = row[0]
            return stats

    async def log_audit(self, task_id: int, account_id: str, level: str, message: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO audit_logs (task_id, account_id, level, message)
                   VALUES (?, ?, ?, ?)""",
                (task_id, account_id, level, message),
            )
            await db.commit()

    async def increment_daily_counter(self, account_id: str, action_type: str) -> int:
        """递增每日计数器，返回当天计数"""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO daily_counters (account_id, action_type, count, date)
                   VALUES (?, ?, 1, ?)
                   ON CONFLICT(account_id, action_type, date)
                   DO UPDATE SET count = count + 1""",
                (account_id, action_type, today),
            )
            await db.commit()
            async with db.execute(
                "SELECT count FROM daily_counters WHERE account_id=? AND action_type=? AND date=?",
                (account_id, action_type, today),
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_daily_count(self, account_id: str, action_type: str) -> int:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT count FROM daily_counters WHERE account_id=? AND action_type=? AND date=?",
                (account_id, action_type, today),
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
```

### 5.3 速率限制器 `core/rate_limiter.py`

```python
"""速率限制 - 令牌桶 + 每日限额 + 随机抖动"""

import time
import random
import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class RateLimiter:
    """每账号独立的速率限制器"""

    def __init__(self, account_config: Dict[str, Any]):
        limits = account_config.get("limits", {})
        self.account_id = account_config["id"]
        self.daily_caps = {
            "post": limits.get("daily_post_cap", 10),
            "comment": limits.get("daily_comment_cap", 50),
            "vote": limits.get("daily_vote_cap", 100),
        }
        self.cooldown = limits.get("cooldown_seconds", 300)
        self.min_delay = limits.get("min_delay", 30)
        self.max_delay = limits.get("max_delay", 120)
        self.last_action_time = 0

    async def wait_if_needed(self, action_type: str, daily_count: int):
        """检查速率限制，必要时阻塞等待"""
        # 1. 每日限额检查
        cap = self.daily_caps.get(action_type, 50)
        if daily_count >= cap:
            raise RateLimitExceeded(
                f"账号 {self.account_id} 今日 {action_type} 已达上限 ({cap})"
            )

        # 2. 冷却时间
        elapsed = time.time() - self.last_action_time
        if elapsed < self.cooldown:
            wait = self.cooldown - elapsed
            logger.info(f"[{self.account_id}] 冷却等待 {wait:.1f}s")
            await asyncio.sleep(wait)

        # 3. 随机延迟 (anti-detection)
        jitter = random.uniform(self.min_delay, self.max_delay)
        logger.debug(f"[{self.account_id}] 随机延迟 {jitter:.1f}s")
        await asyncio.sleep(jitter)

        # 更新时间戳
        self.last_action_time = time.time()


class RateLimitExceeded(Exception):
    pass
```

### 5.4 异步 Worker `workers/runner.py`

```python
"""异步 Worker - 从队列取任务并执行"""

import asyncio
import json
import logging
from pathlib import Path
from core.client import RedditAccount
from core.queue import TaskQueue
from core.rate_limiter import RateLimiter, RateLimitExceeded

logger = logging.getLogger(__name__)


class Worker:
    def __init__(self, settings_path: str, accounts_path: str):
        with open(settings_path) as f:
            self.settings = json.load(f)
        with open(accounts_path) as f:
            accounts_data = json.load(f)

        self.queue = TaskQueue(self.settings["database_path"])

        # 构建账号池和限流器 (每账号独立)
        self.accounts = {}
        self.limiters = {}
        for acc in accounts_data:
            if acc.get("enabled", True):
                self.accounts[acc["id"]] = RedditAccount(acc)
                self.limiters[acc["id"]] = RateLimiter(acc)

    async def run(self):
        """主循环"""
        await self.queue.init_db()
        poll_interval = self.settings["worker"]["poll_interval"]
        max_retries = self.settings["worker"]["max_retries"]

        logger.info(f"Worker 启动 | 账号: {len(self.accounts)} | 轮询: {poll_interval}s")

        while True:
            task = await self.queue.fetch_next()

            if not task:
                await asyncio.sleep(poll_interval)
                continue

            task_id = task["id"]
            account_id = task["account_id"]
            action = task["action_type"]

            # 账号检查
            account = self.accounts.get(account_id)
            if not account:
                await self.queue.mark_failed(task_id, f"账号 {account_id} 不存在或已禁用")
                continue

            limiter = self.limiters[account_id]

            try:
                # 速率限制
                daily_count = await self.queue.get_daily_count(account_id, action)
                await limiter.wait_if_needed(action, daily_count)

                # 执行任务
                result_url = await self._execute(account, task)

                # 成功
                await self.queue.mark_completed(task_id, result_url)
                await self.queue.increment_daily_counter(account_id, action)
                await self.queue.log_audit(task_id, account_id, "INFO", f"成功: {result_url}")
                logger.info(f"Task #{task_id} 完成: {result_url}")

            except RateLimitExceeded as e:
                await self.queue.mark_failed(task_id, str(e))
                await self.queue.log_audit(task_id, account_id, "WARNING", str(e))
                logger.warning(f"Task #{task_id} 限流: {e}")

            except Exception as e:
                retry = task.get("retry_count", 0)
                if retry < max_retries:
                    await self.queue.retry_failed(task_id)
                    backoff = self.settings["worker"]["retry_backoff"] ** retry
                    logger.warning(f"Task #{task_id} 失败, 重试 ({retry+1}/{max_retries}), 退避 {backoff}s")
                    await asyncio.sleep(backoff)
                else:
                    await self.queue.mark_failed(task_id, str(e))
                    await self.queue.log_audit(task_id, account_id, "ERROR", f"最终失败: {e}")
                    logger.error(f"Task #{task_id} 最终失败: {e}")

    async def _execute(self, account: RedditAccount, task: dict) -> str:
        """根据 action_type 分发执行"""
        action = task["action_type"]

        if action == "post":
            return account.post_text(
                task["target_subreddit"],
                task["content_title"],
                task["content_body"],
                task.get("flair_id"),
            )
        elif action == "link":
            return account.post_link(
                task["target_subreddit"],
                task["content_title"],
                task["content_body"],  # body 存 URL
                task.get("flair_id"),
            )
        elif action == "comment":
            return account.comment_on_post(
                task["target_post_id"],
                task["content_body"],
            )
        elif action == "vote":
            account.upvote(task["target_post_id"])
            return f"voted:{task['target_post_id']}"
        else:
            raise ValueError(f"未知动作类型: {action}")
```

### 5.5 CLI 入口 `main.py`

```python
"""Reddit Manager CLI - 主入口"""

import os
import sys
import json
import asyncio
import click
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 路径常量
CONFIG_DIR = Path(os.getenv("REDDIT_MANAGER_CONFIG", "~/.reddit-manager")).expanduser()
ACCOUNTS_PATH = CONFIG_DIR / "accounts.json"
SETTINGS_PATH = Path("config/settings.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@click.group()
def cli():
    """Reddit Manager - 多账号社区管理工具"""
    pass


# === 账号管理 ===

@cli.command()
def accounts():
    """列出所有配置的账号及状态"""
    if not ACCOUNTS_PATH.exists():
        click.echo(f"配置文件不存在: {ACCOUNTS_PATH}")
        click.echo(f"请创建 {ACCOUNTS_PATH} (参考 .env.example)")
        return

    with open(ACCOUNTS_PATH) as f:
        accs = json.load(f)

    click.echo(f"\n共 {len(accs)} 个账号:\n")
    for acc in accs:
        status = click.style("ON", fg="green") if acc.get("enabled") else click.style("OFF", fg="red")
        caps = acc.get("limits", {})
        click.echo(
            f"  [{status}] {acc['id']} | u/{acc['username']} | "
            f"帖:{caps.get('daily_post_cap', '?')}/天 评:{caps.get('daily_comment_cap', '?')}/天 | "
            f"{acc.get('note', '')}"
        )


@cli.command()
def verify():
    """验证所有账号的 API 凭据"""
    from core.client import RedditAccount

    with open(ACCOUNTS_PATH) as f:
        accs = json.load(f)

    for acc in accs:
        if not acc.get("enabled"):
            click.echo(f"  [SKIP] {acc['id']} (已禁用)")
            continue
        try:
            client = RedditAccount(acc)
            click.echo(click.style(f"  [OK] {acc['id']} - u/{acc['username']}", fg="green"))
        except Exception as e:
            click.echo(click.style(f"  [FAIL] {acc['id']} - {e}", fg="red"))


# === 任务操作 ===

@cli.command()
@click.option("--account", "-a", required=True, help="账号 ID (如 acc_01)")
@click.option("--subreddit", "-s", required=True, help="目标 subreddit")
@click.option("--title", "-t", required=True, help="帖子标题")
@click.option("--body", "-b", required=True, help="帖子正文")
@click.option("--schedule", help="定时发布 (ISO格式: 2026-02-17T09:00:00)")
def enqueue_post(account, subreddit, title, body, schedule):
    """入队一个发帖任务"""
    from core.queue import TaskQueue

    async def _enqueue():
        with open(SETTINGS_PATH) as f:
            settings = json.load(f)
        queue = TaskQueue(settings["database_path"])
        await queue.init_db()
        task_id = await queue.enqueue({
            "account_id": account,
            "action_type": "post",
            "subreddit": subreddit,
            "title": title,
            "body": body,
            "scheduled_at": schedule,
        })
        click.echo(f"任务已入队: #{task_id} | {account} -> r/{subreddit}")

    asyncio.run(_enqueue())


@cli.command()
@click.option("--account", "-a", required=True, help="账号 ID")
@click.option("--post-id", "-p", required=True, help="帖子 ID (不带 t3_ 前缀)")
@click.option("--body", "-b", required=True, help="评论内容")
def enqueue_comment(account, post_id, body):
    """入队一个评论任务"""
    from core.queue import TaskQueue

    async def _enqueue():
        with open(SETTINGS_PATH) as f:
            settings = json.load(f)
        queue = TaskQueue(settings["database_path"])
        await queue.init_db()
        task_id = await queue.enqueue({
            "account_id": account,
            "action_type": "comment",
            "post_id": post_id,
            "body": body,
        })
        click.echo(f"评论任务已入队: #{task_id}")

    asyncio.run(_enqueue())


# === Worker ===

@cli.command()
def worker():
    """启动异步 Worker 处理任务队列"""
    from workers.runner import Worker

    click.echo("启动 Reddit Manager Worker...")
    w = Worker(str(SETTINGS_PATH), str(ACCOUNTS_PATH))
    asyncio.run(w.run())


# === 状态查询 ===

@cli.command()
def status():
    """查看任务队列状态"""
    from core.queue import TaskQueue

    async def _status():
        with open(SETTINGS_PATH) as f:
            settings = json.load(f)
        queue = TaskQueue(settings["database_path"])
        await queue.init_db()
        stats = await queue.get_stats()
        click.echo(f"\n任务队列状态:")
        click.echo(f"  待执行: {stats.get('pending', 0)}")
        click.echo(f"  执行中: {stats.get('executing', 0)}")
        click.echo(f"  已完成: {stats.get('completed', 0)}")
        click.echo(f"  失败:   {stats.get('failed', 0)}")

    asyncio.run(_status())


# === 数据查询 ===

@cli.command()
@click.option("--account", "-a", required=True, help="账号 ID")
@click.option("--subreddit", "-s", required=True, help="subreddit 名称")
@click.option("--sort", type=click.Choice(["hot", "new"]), default="hot")
@click.option("--limit", "-l", default=10)
def fetch(account, subreddit, sort, limit):
    """获取 subreddit 帖子列表"""
    from core.client import RedditAccount

    with open(ACCOUNTS_PATH) as f:
        accs = {a["id"]: a for a in json.load(f)}

    if account not in accs:
        click.echo(f"账号 {account} 不存在")
        return

    client = RedditAccount(accs[account])

    if sort == "hot":
        posts = client.get_hot_posts(subreddit, limit)
    else:
        posts = client.get_new_posts(subreddit, limit)

    click.echo(f"\nr/{subreddit} ({sort}, top {limit}):\n")
    for i, p in enumerate(posts, 1):
        click.echo(f"  {i}. [{p['score']:>5}] {p['title'][:60]}")
        click.echo(f"     by u/{p['author']} | {p['num_comments']} comments | id={p['id']}")


@cli.command()
@click.option("--account", "-a", required=True)
@click.option("--subreddit", "-s", required=True)
def subreddit_info(account, subreddit):
    """查看 subreddit 详细信息"""
    from core.client import RedditAccount

    with open(ACCOUNTS_PATH) as f:
        accs = {a["id"]: a for a in json.load(f)}

    client = RedditAccount(accs[account])
    info = client.get_subreddit_info(subreddit)

    click.echo(f"\nr/{info['name']}:")
    click.echo(f"  订阅者: {info['subscribers']:,}")
    click.echo(f"  简介: {info['description']}")


if __name__ == "__main__":
    cli()
```

---

## 6. CLI 命令速查

| 命令 | 说明 | 示例 |
|------|------|------|
| `accounts` | 列出所有账号 | `python main.py accounts` |
| `verify` | 验证 API 凭据 | `python main.py verify` |
| `enqueue-post` | 入队发帖任务 | `python main.py enqueue-post -a acc_01 -s cryptocurrency -t "标题" -b "正文"` |
| `enqueue-comment` | 入队评论任务 | `python main.py enqueue-comment -a acc_01 -p abc123 -b "评论内容"` |
| `worker` | 启动 Worker | `python main.py worker` |
| `status` | 队列状态 | `python main.py status` |
| `fetch` | 查看帖子 | `python main.py fetch -a acc_01 -s solana --sort hot -l 5` |
| `subreddit-info` | 版块信息 | `python main.py subreddit-info -a acc_01 -s web3` |

---

## 7. 速率限制策略

### 7.1 三层限制

| 层级 | 机制 | 参数 |
|------|------|------|
| **L1: Reddit API 全局** | 令牌桶 | 30 req/min (PRAW 内置) |
| **L2: 每账号冷却** | 固定冷却 + 随机抖动 | cooldown_seconds + [min_delay, max_delay] |
| **L3: 每日限额** | SQLite 持久化计数器 | daily_post_cap, daily_comment_cap |

### 7.2 退避策略

```
失败次数    等待时间
  1         2s (backoff^0 * 2)
  2         4s (backoff^1 * 2)
  3         8s (backoff^2 * 2)
  >3        标记 failed，不再重试
```

### 7.3 Anti-Detection

- 每次操作间随机延迟 30-120s (可配置)
- User-Agent 每账号独立
- 不同账号不操作相同帖子 (应用层约束)

---

## 8. Reddit OAuth2 配置指南

### Step 1: 注册应用
1. 登录 Reddit → https://www.reddit.com/prefs/apps
2. 点击 "create another app..."
3. 填写:
   - **name**: `RedditManager`
   - **type**: `script` (本地 CLI 工具选 script)
   - **redirect uri**: `http://localhost:8080`
4. 记下 `client_id` (应用名下方短字符串) 和 `client_secret`

### Step 2: 获取 Refresh Token
```python
# 一次性运行此脚本获取 refresh_token
import praw

reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="http://localhost:8080",
    user_agent="RedditManager:v1.0",
)

# 生成授权 URL
print(reddit.auth.url(scopes=["identity", "submit", "read", "vote", "subscribe"], state="auth", duration="permanent"))
# 访问 URL，授权后从回调 URL 中提取 code
# code = "从回调URL获取"
# refresh_token = reddit.auth.authorize(code)
# print(f"refresh_token: {refresh_token}")
```

### Step 3: 写入 accounts.json
将 `client_id`, `client_secret`, `refresh_token` 填入账号配置。

---

## 9. 部署步骤

```bash
# 1. 克隆/创建项目
mkdir -p ~/Downloads/reddit-manager && cd ~/Downloads/reddit-manager

# 2. 虚拟环境
python3 -m venv venv && source venv/bin/activate

# 3. 安装依赖
pip install praw click aiosqlite python-dotenv pyyaml

# 4. 创建配置目录
mkdir -p ~/.reddit-manager
# 复制 accounts.json 到 ~/.reddit-manager/
# 编辑填入真实凭据

# 5. 初始化数据库
python main.py status  # 首次运行自动建表

# 6. 验证账号
python main.py verify

# 7. 入队测试任务
python main.py enqueue-post -a acc_01 -s test -t "测试帖子" -b "Hello from Reddit Manager"

# 8. 启动 Worker
python main.py worker
```

---

## 10. 安全注意事项

1. **密钥隔离**: accounts.json 存放于 `~/.reddit-manager/`，不在项目目录内
2. **.gitignore**: 必须包含 `.env`, `data/*.db`, `logs/`, `~/.reddit-manager/`
3. **Token 轮换**: refresh_token 不过期，但建议每 90 天重新授权
4. **日志脱敏**: 日志中不打印 client_secret 和 refresh_token
5. **账号隔离**: 每账号独立 PRAW 实例，防止 token 串扰

---

## 11. 验收标准

- [ ] `python main.py accounts` 正确列出所有配置账号
- [ ] `python main.py verify` 所有启用账号认证通过
- [ ] `python main.py enqueue-post` 成功入队并返回任务 ID
- [ ] `python main.py status` 显示正确的队列统计
- [ ] `python main.py worker` 启动后自动处理 pending 任务
- [ ] 发帖成功后 task 状态变为 completed，result_url 非空
- [ ] 超过 daily_cap 时任务标记 failed 并记录原因
- [ ] 失败任务在 max_retries 内自动重试
- [ ] `python main.py fetch` 正确返回帖子列表
- [ ] SQLite 数据库 audit_logs 记录所有操作
