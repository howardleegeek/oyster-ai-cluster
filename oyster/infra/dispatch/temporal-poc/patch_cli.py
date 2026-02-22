import yaml
from pathlib import Path

def parse_spec_metadata(spec_path):
    text = Path(spec_path).read_text()
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                meta = {}
            content = parts[2].strip()
            return meta, content
    return {}, text

def load_specs_for_project(project):
    from workflows import TaskSpec
    base_dir = Path("~/Downloads/specs").expanduser()
    
    # Try different paths
    paths_to_try = [
        base_dir / project / "PROJECTS" / "SPEC",
        base_dir / project,
        base_dir
    ]
    
    specs_path = None
    for p in paths_to_try:
        if p.exists() and (list(p.glob("S*.md")) or list(p.glob("P*.md"))):
            specs_path = p
            break
            
    if not specs_path:
        print(f"Error: No specs found for project {project}")
        return []
        
    tasks = []
    for spec_file in sorted(specs_path.glob("*.md")):
        if not (spec_file.stem.startswith("S") or spec_file.stem.startswith("P")):
            continue
            
        task_id = spec_file.stem
        meta, content = parse_spec_metadata(spec_file)
        
        tasks.append(
            TaskSpec(
                task_id=meta.get("task_id", task_id),
                project=project,
                spec_file=str(spec_file),
                spec_content=content,
                depends_on=meta.get("depends_on", []),
                estimated_minutes=meta.get("estimated_minutes", 30),
            )
        )
    return tasks
