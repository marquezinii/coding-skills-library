#!/usr/bin/env python3
"""
validate.py - Skill validation utilities

Validates:
- SKILL.md frontmatter structure
- Required fields
- No nested .git directories
- File count limits
- Basic structure
"""

import sys
import yaml
from pathlib import Path
from typing import List, Tuple

SKILLS_DIR = Path(__file__).parent.parent / "skills"


def validate_skill(skill_dir: Path) -> Tuple[List[str], List[str]]:
    """Validate a single skill directory. Returns (errors, warnings)."""
    errors = []
    warnings = []
    name = skill_dir.name
    
    # Check SKILL.md exists
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"{name}: Missing SKILL.md")
        return errors, warnings
    
    # Validate frontmatter
    try:
        content = skill_md.read_text(encoding='utf-8')
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                fm = yaml.safe_load(parts[1])
                if not fm:
                    warnings.append(f"{name}: Empty frontmatter")
                else:
                    required = ['name', 'description', 'license']
                    for field in required:
                        if field not in fm:
                            warnings.append(f"{name}: Missing frontmatter field '{field}'")
                    
                    # Check name matches directory
                    if fm.get('name') != name:
                        warnings.append(f"{name}: frontmatter name '{fm.get('name')}' != directory name")
        else:
            warnings.append(f"{name}: No frontmatter (--- delimiter)")
    except yaml.YAMLError as e:
        errors.append(f"{name}: Invalid YAML frontmatter: {e}")
    except Exception as e:
        errors.append(f"{name}: Error reading SKILL.md: {e}")
    
    # Check for nested .git
    if (skill_dir / ".git").exists():
        errors.append(f"{name}: Contains nested .git directory")
    
    # Check for binary files (simple heuristic)
    for file_path in skill_dir.rglob("*"):
        if file_path.is_file():
            try:
                file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                warnings.append(f"{name}: Binary file detected: {file_path.relative_to(skill_dir)}")
    
    # Check file count
    file_count = len([f for f in skill_dir.rglob("*") if f.is_file()])
    if file_count > 200:
        warnings.append(f"{name}: {file_count} files (unusually high)")
    
    # Check for large files (>1MB, excluding assets)
    for file_path in skill_dir.rglob("*"):
        if file_path.is_file() and file_path.stat().st_size > 1_000_000:
            rel = file_path.relative_to(skill_dir)
            if 'assets' not in rel.parts and not rel.name.endswith('.tm7'):
                warnings.append(f"{name}: Large file: {rel} ({file_path.stat().st_size} bytes)")
    
    return errors, warnings


def main():
    skill_dirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    all_errors = []
    all_warnings = []
    
    print(f"Validating {len(skill_dirs)} skills...")
    
    for skill_dir in sorted(skill_dirs):
        errors, warnings = validate_skill(skill_dir)
        all_errors.extend(errors)
        all_warnings.extend(warnings)
    
    # Print results
    if all_errors:
        print("\nERRORS:")
        for e in all_errors:
            print(f"  - {e}")
    
    if all_warnings:
        print("\nWARNINGS:")
        for w in all_warnings:
            print(f"  - {w}")
    
    print(f"\nTotal: {len(all_errors)} errors, {len(all_warnings)} warnings across {len(skill_dirs)} skills")
    
    if all_errors:
        sys.exit(1)


if __name__ == '__main__':
    main()