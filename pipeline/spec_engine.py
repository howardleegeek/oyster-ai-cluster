#!/usr/bin/env python3
import os
import re
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional

MM_CLI = Path.home() / "Downloads" / "dispatch" / "mm"

RULES = {
    "FM_TASK_ID": {"weight": 5, "check": "task_id 存在且格式正确 (S01-xxx)"},
    "FM_PROJECT": {"weight": 3, "check": "project 存在"},
    "FM_PRIORITY": {"weight": 3, "check": "priority 存在且为 0-3"},
    "FM_DEPENDS": {"weight": 3, "check": "depends_on 是 list"},
    "FM_MODIFIES": {"weight": 8, "check": "modifies 是 list 且不为空，每个路径格式正确"},
    "FM_EXECUTOR": {"weight": 3, "check": "executor 是 glm/codex"},
    "FM_NO_CONFLICT": {"weight": 5, "check": "modifies 的文件不与同目录其他 spec 冲突"},
    "BODY_GOAL": {"weight": 8, "check": "有 ## 目标，且 > 20 字"},
    "BODY_CONSTRAINT": {"weight": 5, "check": "有 ## 约束"},
    "BODY_CHANGES": {"weight": 7, "check": "有 ## 具体改动 或代码示例"},
    "BODY_ACCEPT": {"weight": 7, "check": "有 ## 验收标准，>=2 个 checkbox"},
    "BODY_DONOT": {"weight": 3, "check": "有 ## 不要做"},
    "CODE_EXAMPLE": {"weight": 8, "check": "有 ```python 或 ```bash 代码块"},
    "CODE_KWARGS": {"weight": 4, "check": "函数定义用 kwargs 不用位置参数"},
    "CODE_NO_SECRET": {"weight": 5, "check": "无硬编码密钥/密码"},
    "CODE_ENV_VAR": {"weight": 3, "check": "用 os.environ 不用硬编码 URL"},
    "SEC_NO_ENV": {"weight": 3, "check": "不提交 .env"},
    "SEC_VALIDATE": {"weight": 5, "check": "有验证命令 (pytest/curl/npm test)"},
    "SEC_BYZANTINE": {"weight": 5, "check": "API spec 包含异常场景测试"},
    "SEC_UI_GUARD": {"weight": 4, "check": "改后端的 spec 有'不动 UI/CSS'约束"},
    "SEC_PYDANTIC": {"weight": 3, "check": "涉及 Pydantic 的有大小写约束"},
}

SECRET_PATTERNS = [
    r'password\s*=\s*["\'][^"\']+["\']',
    r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
    r'secret\s*=\s*["\'][^"\']+["\']',
    r'token\s*=\s*["\'][^"\']+["\']',
    r'Authorization:\s*[Bb]earer\s+[A-Za-z0-9_\-\.]+',
    r'AKIA[0-9A-Z]{16}',
]

URL_HARDCODE_PATTERNS = [
    r'https?://(?!localhost|127\.0\.0\.1)[^\s"\']+',
]

PYDANTIC_PATTERNS = [
    r'class\s+\w+\(BaseModel\)|Field\(|pydantic',
]

API_PATTERNS = [
    r'@app\.|@router\.|@api|def\s+\w+\(.*Request',
    r'request|response|endpoint|GET|POST|PUT|DELETE',
]


class ValidationReport:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.score = 0
        self.max_score = 0
        self.results: Dict[str, Tuple[bool, str]] = {}

    def add_result(self, rule: str, passed: bool, detail: str = ""):
        weight = RULES[rule]["weight"]
        self.max_score += weight
        if passed:
            self.score += weight
        self.results[rule] = (passed, detail)

    def format_output(self) -> str:
        lines = []
        filename = Path(self.file_path).name
        lines.append(f"\033[1m📊 {filename} — {self.score}/{self.max_score}\033[0m")
        
        failed_rules = []
        for rule, (passed, detail) in self.results.items():
            weight = RULES[rule]["weight"]
            if passed:
                lines.append(f"  ✅ {rule} ({weight}/{weight})")
            else:
                detail_msg = f" — {detail}" if detail else ""
                lines.append(f"  ❌ {rule} (0/{weight}){detail_msg}")
                failed_rules.append(rule)
        
        if failed_rules:
            lines.append(f"  → 建议: python3 spec_engine.py enhance {self.file_path}")
        
        return "\n".join(lines)


def parse_front_matter(content: str) -> Dict:
    fm = {}
    match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                fm[key.strip()] = val.strip()
    return fm


def get_body_content(content: str) -> str:
    match = re.search(r'^---\s*\n.*?\n---\s*\n(.*)', content, re.DOTALL)
    return match.group(1) if match else content


def get_modifies_list(fm: Dict) -> List[str]:
    if 'modifies' not in fm:
        return []
    modifies = fm['modifies']
    if isinstance(modifies, str):
        import yaml
        try:
            modifies = yaml.safe_load(modifies)
        except:
            modifies = [modifies]
    if isinstance(modifies, list):
        return modifies
    return []


def check_task_id_format(task_id: str) -> bool:
    return bool(re.match(r'^S\d{2}-[a-zA-Z0-9_-]+$', task_id))


def check_modifies_paths(modifies: List[str]) -> Tuple[bool, str]:
    if not modifies:
        return False, "modifies 为空"
    for path in modifies:
        if not re.match(r'^[\w/._-]+$', path):
            return False, f"路径格式错误: {path}"
    return True, ""


def check_no_conflict(spec_path: str, modifies: List[str], all_specs: Dict[str, List[str]]) -> bool:
    spec_dir = str(Path(spec_path).parent)
    for other_spec, other_modifies in all_specs.items():
        if str(Path(other_spec).parent) == spec_dir and other_spec != spec_path:
            for mod in modifies:
                if mod in other_modifies:
                    return False
    return True


def check_goal_length(content: str) -> int:
    body = get_body_content(content)
    match = re.search(r'##\s*目标\s*\n(.*?)(?=##|$)', body, re.DOTALL)
    if match:
        goal_text = match.group(1).strip()
        return len(goal_text)
    return 0


def check_has_section(content: str, section: str) -> bool:
    body = get_body_content(content)
    pattern = r'##\s*' + section + r'\s*\n'
    return bool(re.search(pattern, body))


def count_checkboxes(content: str) -> int:
    body = get_body_content(content)
    matches = re.findall(r'-\s*\[\s*\]', body)
    return len(matches)


def check_code_examples(content: str) -> bool:
    return bool(re.search(r'```(python|bash|sh|js)', content))


def check_kwargs_usage(content: str) -> bool:
    body = get_body_content(content)
    func_defs = re.findall(r'def\s+\w+\(([^)]*)\)', body)
    for func_args in func_defs:
        args = [a.strip().split('=')[0].strip() for a in func_args.split(',') if a.strip()]
        if args and '=' not in func_args:
            return False
    return True


def check_no_secrets(content: str) -> Tuple[bool, str]:
    for pattern in SECRET_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return False, "检测到硬编码密钥"
    return True, ""


def check_env_var_usage(content: str) -> bool:
    body = get_body_content(content)
    code_blocks = re.findall(r'```[^\n]*\n(.*?)```', body, re.DOTALL)
    for block in code_blocks:
        if re.search(URL_HARDCODE_PATTERNS[0], block):
            if not re.search(r'os\.environ|os\.getenv|os\.environ\.get', block):
                return False
    return True


def check_no_env_commit(content: str) -> bool:
    return '.env' not in content.lower() or '不提交 .env' in content.lower()


def check_validation_command(content: str) -> bool:
    body = get_body_content(content)
    return bool(re.search(r'(pytest|curl|npm test|npm run|python.*test)', body))


def check_byzantine(content: str) -> bool:
    body = get_body_content(content)
    if not any(re.search(p, body, re.IGNORECASE) for p in API_PATTERNS):
        return False
    byzantine_keywords = ['异常', '错误', '边界', '超时', '空', '无效', 'error', 'exception', 'timeout', 'invalid', 'empty', 'null']
    return any(kw in body.lower() for kw in byzantine_keywords)


def check_ui_guard(content: str, fm: Dict) -> bool:
    if not any(p in str(fm.get('modifies', '')).lower() for p in ['.py', 'api', 'service', 'db']):
        return True
    body = get_body_content(content)
    guard_patterns = ['不动 ui', '不动 css', '不碰 ui', '不碰 css', 'no ui', 'no css', '保持 ui', '保持 css']
    return any(p in body.lower() for p in guard_patterns)


def check_pydantic_case(content: str) -> bool:
    body = get_body_content(content)
    if not any(re.search(p, body, re.IGNORECASE) for p in PYDANTIC_PATTERNS):
        return True
    case_patterns = ['lower', 'upper', 'case', '大小写', 'to_lower', 'to_upper']
    return any(p in body.lower() for p in case_patterns)


def validate_spec(spec_path: str, all_specs: Optional[Dict[str, List[str]]] = None) -> ValidationReport:
    report = ValidationReport(spec_path)
    
    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {spec_path}: {e}")
        return report
    
    fm = parse_front_matter(content)
    modifies = get_modifies_list(fm)
    
    if all_specs is None:
        all_specs = {spec_path: modifies}
    
    task_id = fm.get('task_id', '')
    report.add_result("FM_TASK_ID", check_task_id_format(task_id), "格式应为 S01-xxx" if not check_task_id_format(task_id) else "")
    report.add_result("FM_PROJECT", 'project' in fm, "缺少 project 字段")
    
    priority = fm.get('priority', '')
    priority_valid = priority in ['0', '1', '2', '3']
    report.add_result("FM_PRIORITY", priority_valid, f"priority 应为 0-3" if not priority_valid else "")
    
    depends = fm.get('depends_on', '')
    report.add_result("FM_DEPENDS", depends.startswith('['), "depends_on 应为 list")
    
    modifies_valid, modifies_msg = check_modifies_paths(modifies)
    report.add_result("FM_MODIFIES", modifies_valid, modifies_msg)
    
    executor = fm.get('executor', '')
    report.add_result("FM_EXECUTOR", executor in ['glm', 'codex', 'glm4'], f"executor 应为 glm/codex" if executor else "")
    
    report.add_result("FM_NO_CONFLICT", check_no_conflict(spec_path, modifies, all_specs), "有文件冲突")
    
    goal_len = check_goal_length(content)
    report.add_result("BODY_GOAL", goal_len > 20, f"目标内容 {goal_len} 字 < 20" if goal_len <= 20 else "")
    
    report.add_result("BODY_CONSTRAINT", check_has_section(content, "约束"), "缺少 ## 约束 段")
    report.add_result("BODY_CHANGES", check_has_section(content, "具体改动") or check_code_examples(content), "缺少代码示例")
    
    checkbox_count = count_checkboxes(content)
    report.add_result("BODY_ACCEPT", checkbox_count >= 2, f"验收标准 {checkbox_count} 个 < 2" if checkbox_count < 2 else "")
    
    report.add_result("BODY_DONOT", check_has_section(content, "不要做"), "缺少 ## 不要做 段")
    
    report.add_result("CODE_EXAMPLE", check_code_examples(content), "缺少代码块")
    report.add_result("CODE_KWARGS", check_kwargs_usage(content), "函数定义应用 kwargs")
    
    no_secrets, secret_msg = check_no_secrets(content)
    report.add_result("CODE_NO_SECRET", no_secrets, secret_msg)
    
    report.add_result("CODE_ENV_VAR", check_env_var_usage(content), "应使用 os.environ")
    
    report.add_result("SEC_NO_ENV", check_no_env_commit(content), "spec 中不应出现 .env")
    report.add_result("SEC_VALIDATE", check_validation_command(content), "缺少验证命令")
    report.add_result("SEC_BYZANTINE", check_byzantine(content), "API spec 缺少异常场景测试")
    report.add_result("SEC_UI_GUARD", check_ui_guard(content, fm), "缺少 UI/CSS 保护约束")
    report.add_result("SEC_PYDANTIC", check_pydantic_case(content), "Pydantic 缺少大小写约束")
    
    return report


def validate_all(specs_dir: str) -> List[ValidationReport]:
    specs_dir_path = Path(specs_dir)
    spec_files = list(specs_dir_path.glob("*.md"))
    
    all_specs = {}
    for spec_file in spec_files:
        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()
        fm = parse_front_matter(content)
        modifies = get_modifies_list(fm)
        all_specs[str(spec_file)] = modifies
    
    reports = []
    for spec_file in spec_files:
        report = validate_spec(str(spec_file), all_specs)
        reports.append(report)
        print(report.format_output())
    
    return reports


def get_failed_rules(report: ValidationReport) -> List[str]:
    failed = []
    for rule, (passed, _) in report.results.items():
        if not passed:
            failed.append(f"{rule}: {RULES[rule]['check']}")
    return failed


def get_code_context(modifies: List[str], max_lines: int = 50) -> str:
    context_parts = []
    for path in modifies:
        full_path = Path(path)
        if not full_path.is_absolute():
            continue
        if full_path.exists() and full_path.suffix == '.py':
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:max_lines]
                    context_parts.append(f"=== {full_path.name} ===\n{''.join(lines)}")
            except:
                pass
    return "\n\n".join(context_parts)


def enhance_spec(spec_path: str) -> Tuple[bool, int, int]:
    with open(spec_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    report = validate_spec(spec_path)
    original_score = report.score
    
    failed_rules = get_failed_rules(report)
    if not failed_rules:
        print(f"Spec 已完整，无需增强")
        return False, original_score, original_score
    
    fm = parse_front_matter(original_content)
    modifies = get_modifies_list(fm)
    code_context = get_code_context(modifies)
    
    prompt = f"""你是 Spec 质量增强器。根据以下信息补全 spec:

原始 Spec:
{original_content}

缺失检查项:
{chr(10).join(failed_rules)}

项目代码上下文:
{code_context if code_context else "无代码上下文"}

SOP 要求:
1. 验收标准必须用 - [ ] 格式，至少 3 个
2. 必须有 ## 约束 段，包含: 不动 UI/CSS, kwargs only, 不硬编码 secret
3. 必须有 ## 不要做 段
4. 如果涉及 API，验收标准必须包含: 空输入测试, 超时测试, 无效 token 测试
5. 代码示例必须基于真实代码上下文，不能是伪代码
6. 函数定义必须用 kwargs

输出: 增强后的完整 spec (保留原始内容，补充缺失部分)"""
    
    try:
        spec_p = Path(spec_path)
        result = subprocess.run(
            ["python3", str(MM_CLI), prompt],
            capture_output=True, text=True, timeout=120,
            cwd=str(spec_p.parent) if spec_p.parent.exists() else None
        )
        enhanced_content = result.stdout if result.stdout else result.stderr
    except Exception as e:
        print(f"MiniMax 调用失败: {e}")
        return False, original_score, original_score
    
    enhanced_path = Path(spec_path)
    backup_path = enhanced_path.with_suffix(enhanced_path.suffix + '.bak')
    shutil.copy2(spec_path, backup_path)
    
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    new_report = validate_spec(spec_path)
    new_score = new_report.score
    
    return True, original_score, new_score


def enhance_all(specs_dir: str):
    specs_dir_path = Path(specs_dir)
    spec_files = list(specs_dir_path.glob("*.md"))
    
    for spec_file in spec_files:
        print(f"\n🔧 增强 {spec_file.name}")
        report = validate_spec(str(spec_file))
        print(f"  原始分数: {report.score}/100")
        
        success, old, new = enhance_spec(str(spec_file))
        if success:
            print(f"  增强后分数: {new}/100 (+{new-old})")
            print(f"  备份: {spec_file.name}.bak")


def gate(specs_dir: str):
    reports = validate_all(specs_dir)
    
    if not reports:
        print("No specs found")
        sys.exit(1)
    
    min_score = min(r.score for r in reports)
    avg_score = sum(r.score for r in reports) / len(reports)
    
    print(f"\n🚦 质量门禁: {specs_dir}")
    for r in reports:
        status = "✅" if r.score >= 80 else "⚠️"
        print(f"  {Path(r.file_path).stem}: {r.score}/100 {status}")
    
    print(f"\n  最低: {min_score} | 平均: {avg_score:.0f}")
    
    if min_score < 60:
        print(f"  状态: BLOCKED ❌")
        print(f"  原因: 最低分 {min_score} < 60，必须 enhance 后重试")
        sys.exit(2)
    elif avg_score < 80:
        print(f"  状态: WARNING ⚠️")
        print(f"  原因: 平均分 {avg_score:.0f} < 80，建议 enhance")
        sys.exit(1)
    else:
        print(f"  状态: PASSED ✅")
        sys.exit(0)


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 spec_engine.py validate <spec_file>")
        print("  python3 spec_engine.py validate-all <specs_dir>")
        print("  python3 spec_engine.py enhance <spec_file>")
        print("  python3 spec_engine.py enhance-all <specs_dir>")
        print("  python3 spec_engine.py gate <specs_dir>")
        sys.exit(1)
    
    command = sys.argv[1]
    target = sys.argv[2]
    
    if command == "validate":
        report = validate_spec(target)
        print(report.format_output())
    elif command == "validate-all":
        validate_all(target)
    elif command == "enhance":
        print(f"\n🔧 增强 {target}")
        report = validate_spec(target)
        print(f"  原始分数: {report.score}/100")
        
        success, old, new = enhance_spec(target)
        if success:
            print(f"  增强后分数: {new}/100 (+{new-old})")
            print(f"  已写回: {target}")
            print(f"  备份: {target}.bak")
    elif command == "enhance-all":
        enhance_all(target)
    elif command == "gate":
        gate(target)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
