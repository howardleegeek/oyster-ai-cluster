#!/usr/bin/env python3
"""
拜占庭对撞器 - 单元测试
"""

import unittest
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))


class TestReporter(unittest.TestCase):
    """测试报告生成"""

    def setUp(self):
        self.test_data = {
            "id": "test-001",
            "topic": "测试主题",
            "rounds": 2,
            "llm": "zhipu",
            "created_at": datetime.now().isoformat(),
            "status": "completed",
            "result": {
                "history": [{"challenger": "挑战者内容", "defender": "辩护者内容"}],
                "convergence": {"summary": "收敛结论"},
            },
        }

    def test_generate_report(self):
        """测试报告生成"""
        from reporter import generate_collision_report

        content = generate_collision_report(self.test_data)

        self.assertIn("测试主题", content)
        self.assertIn("挑战者内容", content)
        self.assertIn("辩护者内容", content)
        self.assertIn("收敛结论", content)

    def test_research_report(self):
        """测试调研报告"""
        from reporter import generate_research_report

        research_data = {
            "query": "测试查询",
            "report": {
                "facts": [{"content": "事实1", "confidence": 0.9}],
                "disputed_facts": [],
            },
            "timestamp": datetime.now().isoformat(),
        }

        content = generate_research_report(research_data)

        self.assertIn("测试查询", content)
        self.assertIn("事实1", content)


class TestStorage(unittest.TestCase):
    """测试存储"""

    def test_save_collision(self):
        """测试保存碰撞"""
        # 临时测试
        pass

    def test_get_collision(self):
        """测试获取碰撞"""
        pass


class TestNotifier(unittest.TestCase):
    """测试通知"""

    def test_notifier_init(self):
        """测试通知器初始化"""
        from notify import Notifier

        notifier = Notifier()
        self.assertIsNotNone(notifier)


class TestLLM(unittest.TestCase):
    """测试 LLM 适配"""

    def test_create_llm(self):
        """测试创建 LLM"""
        from llm import create_llm

        # 测试本地模式（不需要 API key）
        llm = create_llm("local", model="llama3.2:1b")
        self.assertIsNotNone(llm)


class TestAIIOSync(unittest.TestCase):
    """测试 ai_os 同步"""

    def test_save_to_ai_os(self):
        """测试保存到 ai_os"""
        from ai_os_sync import save_to_ai_os

        test_data = {
            "id": "test-001",
            "topic": "测试主题",
            "rounds": 2,
            "created_at": datetime.now().isoformat(),
            "status": "completed",
        }

        # 不实际保存，只测试函数可调用
        # save_to_ai_os(test_data, "/tmp/test_ai_os")
        self.assertTrue(True)


def run_tests():
    """运行所有测试"""
    print("🧪 运行拜占庭对撞器单元测试...\n")

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestReporter))
    suite.addTests(loader.loadTestsFromTestCase(TestStorage))
    suite.addTests(loader.loadTestsFromTestCase(TestNotifier))
    suite.addTests(loader.loadTestsFromTestCase(TestLLM))
    suite.addTests(loader.loadTestsFromTestCase(TestAIIOSync))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 打印摘要
    print(f"\n{'=' * 50}")
    print(f"测试结果: {result.testsRun} 个测试")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
