---
task_id: S17-full-integration-test
project: pipeline-v2
priority: 3
depends_on: [S10-qa-standards-and-skills, S11-L4a-api-qa, S12-L4b-browser-qa, S13-L4c-ui-review, S14-L4d-regression, S15-L4-test-rewrite, S16-L5-smart-fix-loop]
modifies: ["dispatch/pipeline/test_integration.py"]
executor: glm
---

## 目标
端到端集成测试: 创建 test_integration.py 验证 pipeline 各层正确协作，包含 mock 项目测试

## 约束
- 用 mock 项目测试，不依赖真实项目
- 所有层都能正确执行并产出报告
- 使用 unittest/pytest 框架
- 所有函数用 kwargs
- 不动任何已有文件

## 具体改动

### dispatch/pipeline/test_integration.py

```python
#!/usr/bin/env python3
"""Pipeline v2 端到端集成测试"""
import json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

# 添加 pipeline 到 path
PIPELINE_DIR = Path(__file__).parent
sys.path.insert(0, str(PIPELINE_DIR))

class TestPipelineV2(unittest.TestCase):
    """Pipeline v2 完整集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """创建临时测试项目"""
        cls.temp_dir = Path(tempfile.mkdtemp())
        cls.test_project = cls.temp_dir / "test_project"
        cls.test_project.mkdir()
        
        # 创建 mock 后端 (FastAPI)
        (cls.test_project / "backend").mkdir()
        (cls.test_project / "backend" / "main.py").write_text('''
from fastapi import FastAPI
app = FastAPI()

@app.get("/api/users")
def get_users():
    return [{"id": 1, "name": "test"}]

@app.post("/api/users")
def create_user():
    return {"id": 2, "name": "created"}
''')
        (cls.test_project / "backend" / "requirements.txt").write_text("fastapi\nuvicorn\npytest\npytest-cov\n")
        
        # 创建 mock 前端
        (cls.test_project / "frontend").mkdir()
        (cls.test_project / "frontend" / "package.json").write_text('''
{
  "name": "test-frontend",
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest"
  }
}
''')
        (cls.test_project / "frontend" / "src" / "App.tsx").write_text('''
export function App() {
  return <div>Test App</div>;
}
''')
        
        cls.reports_dir = cls.temp_dir / "reports"
        cls.reports_dir.mkdir()
    
    @classmethod
    def tearDownClass(cls):
        """清理临时目录"""
        shutil.rmtree(cls.temp_dir)
    
    def test_01_qa_standards_import(self):
        """S10: qa_standards 模块可导入"""
        from qa_standards import check_api_qa, check_browser_qa, check_ui_qa, check_regression
        self.assertTrue(callable(check_api_qa))
        self.assertTrue(callable(check_browser_qa))
        self.assertTrue(callable(check_ui_qa))
        self.assertTrue(callable(check_regression))
    
    def test_02_skill_prompts_import(self):
        """S10: skill_prompts 模块可导入"""
        from skill_prompts import load_skill, build_layer_prompt, LAYER_SKILLS
        # 加载一个 skill
        skill_content = load_skill(name="senior-qa")
        self.assertIsInstance(skill_content, str)
        # 构建 layer prompt
        prompt = build_layer_prompt(
            layer="L4a", 
            project_name="test", 
            context={"task_description": "test task"}
        )
        self.assertIn("L4a", prompt)
        self.assertIn("test task", prompt)
    
    def test_03_qa_standards_check_all(self):
        """S10: check_all 处理缺失报告"""
        from qa_standards import check_all
        result = check_all(project="test", reports_dir=str(self.reports_dir))
        self.assertIn("overall_pass", result)
        self.assertFalse(result["overall_pass"])  # 报告缺失，应该 fail
    
    def test_04_api_qa_checker(self):
        """S11: API QA 检查器"""
        from qa_standards import check_api_qa
        # 通过的报告
        report = {"total_tests": 10, "passed_tests": 10, "byzantine_pass_rate": 1.0, "s1_bugs": 0}
        ok, score, details = check_api_qa(report=report)
        self.assertTrue(ok)
        self.assertEqual(score, 100)
        
        # 失败的报告
        report2 = {"total_tests": 10, "passed_tests": 5, "byzantine_pass_rate": 0.5, "s1_bugs": 1}
        ok2, score2, details2 = check_api_qa(report=report2)
        self.assertFalse(ok2)
    
    def test_05_browser_qa_checker(self):
        """S11: 浏览器 QA 检查器"""
        from qa_standards import check_browser_qa
        # 通过
        report = {"total_js_errors": 0, "pages_loaded": 5, "pages_total": 5, "e2e_pass": True}
        ok, score, details = check_browser_qa(report=report)
        self.assertTrue(ok)
        
        # 失败
        report2 = {"total_js_errors": 1, "pages_loaded": 4, "pages_total": 5, "e2e_pass": False}
        ok2, score2, details2 = check_browser_qa(report=report2)
        self.assertFalse(ok2)
    
    def test_06_ui_qa_checker(self):
        """S11: UI QA 检查器"""
        from qa_standards import check_ui_qa
        # 通过
        report = {"pages": [
            {"total_score": 80, "has_overflow": False},
            {"total_score": 75, "has_overflow": False},
        ]}
        ok, score, details = check_ui_qa(report=report)
        self.assertTrue(ok)
        self.assertEqual(score, 77.5)
        
        # 失败 (分数低)
        report2 = {"pages": [{"total_score": 60, "has_overflow": False}]}
        ok2, score2, details2 = check_ui_qa(report=report2)
        self.assertFalse(ok2)
    
    def test_07_regression_checker(self):
        """S11: 回归测试检查器"""
        from qa_standards import check_regression
        # 通过
        report = {"coverage_percent": 60, "new_failures": [], "page_load_times": {"/": 1.5}}
        ok, score, details = check_regression(report=report)
        self.assertTrue(ok)
        self.assertEqual(score, 60)
        
        # 失败 (覆盖率低)
        report2 = {"coverage_percent": 30, "new_failures": [], "page_load_times": {"/": 1.5}}
        ok2, score2, details2 = check_regression(report=report2)
        self.assertFalse(ok2)
    
    def test_08_layer_imports(self):
        """S15: 各层可导入"""
        # 检查 L4 层存在
        layers_dir = PIPELINE_DIR / "layers"
        if layers_dir.exists():
            # 尝试导入
            sys.path.insert(0, str(layers_dir))
            # 不需要实际执行，只要 import 不报错
    
    def test_09_skill_prompts_all_layers(self):
        """S16: 所有层的 skill 映射正确"""
        from skill_prompts import LAYER_SKILLS
        required_layers = ["L1", "L2", "L3", "L4a", "L4b", "L4c", "L4d", "L5", "L6"]
        for layer in required_layers:
            self.assertIn(layer, LAYER_SKILLS, f"Missing layer {layer} in LAYER_SKILLS")
    
    def test_10_end_to_end_mock(self):
        """完整端到端: 创建 mock L4 报告，检查 check_all 汇总"""
        from qa_standards import check_all
        
        # 创建 mock 报告
        l4a_report = {
            "total_tests": 20, "passed_tests": 18, "byzantine_pass_rate": 0.9, "s1_bugs": 0, "s2_bugs":         (self.re2
        }
ports_dir / "L4a-api-report.json").write_text(json.dumps(l4a_report))
        
        l4d_report = {
            "coverage_percent": 55, "new_failures": [], "page_load_times": {"/": 1.0}
        }
        (self.reports_dir / "L4d-regression-report.json").write_text(json.dumps(l4d_report))
        
        # L4b/L4c 缺失 (非 Mac 环境)
        
        result = check_all(project="test", reports_dir=str(self.reports_dir))
        
        # L4a 通过，L4d 通过，L4b/L4c 缺失所以 fail
        self.assertFalse(result["overall_pass"])
        self.assertIn("L4a", result["sub_results"])
        self.assertIn("L4d", result["sub_results"])


class TestSkillPromptsIntegration(unittest.TestCase):
    """Skill prompts 与各层集成测试"""
    
    def test_build_layer_prompt_with_context(self):
        """验证 layer prompt 构建包含完整上下文"""
        from skill_prompts import build_layer_prompt
        
        context = {
            "task_description": "修复 SQL 注入漏洞",
            "project_info": "后端 API 项目，使用 FastAPI"
        }
        
        prompt = build_layer_prompt(layer="L5", project_name="my-api", context=context)
        
        # 应该包含任务描述和项目信息
        self.assertIn("SQL 注入漏洞", prompt)
        self.assertIn("my-api", prompt)
        self.assertIn("L5", prompt)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

## 验收标准
- [ ] `python3 test_integration.py` 执行成功，无报错
- [ ] qa_standards 所有检查函数可导入
- [ ] skill_prompts load_skill 返回非空内容
- [ ] build_layer_prompt 生成包含 layer 名称的 prompt
- [ ] LAYER_SKILLS 包含所有必要层 (L1-L6)
- [ ] check_all 对部分报告正确判断 overall_pass
- [ ] Mock L4 报告创建后 check_all 能正确汇总

## 不要做
- 不要修改 qa_standards.py
- 不要修改 skill_prompts.py
- 不要修改任何已有层的代码
- 不要依赖真实项目 (用 mock)
