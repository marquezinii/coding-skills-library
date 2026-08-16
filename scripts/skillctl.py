#!/usr/bin/env python3
"""
skillctl.py - Coding Skills Library Management CLI

Usage:
    python skillctl.py list
    python skillctl.py search <query>
    python skillctl.py info <skill>
    python skillctl.py install <skill> --target <path>
    python skillctl.py install-all --target <path>
    python skillctl.py install-category <category> --target <path>
    python skillctl.py validate [skill]
    python skillctl.py catalog
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

SKILLS_DIR = Path(__file__).parent.parent / "skills"
CATALOG_PATH = Path(__file__).parent.parent / "catalog.json"


def load_catalog() -> List[Dict[str, Any]]:
    """Load the skill catalog."""
    if CATALOG_PATH.exists():
        with open(CATALOG_PATH, encoding='utf-8') as f:
            return json.load(f)
    return []


def build_catalog() -> List[Dict[str, Any]]:
    """Build catalog from skills directory."""
    import datetime
    
    def sanitize(obj):
        """Convert non-JSON-serializable objects to strings."""
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, dict):
            return {k: sanitize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [sanitize(v) for v in obj]
        if isinstance(obj, set):
            return [sanitize(v) for v in obj]
        return obj
    
    catalog = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        if skill_dir.name.startswith('.'):
            continue
        
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        
        # Parse frontmatter
        meta = parse_frontmatter(skill_md)
        meta["path"] = str(skill_dir.relative_to(SKILLS_DIR.parent))
        catalog.append(sanitize(meta))
    
    return catalog


def parse_frontmatter(skill_md: Path) -> Dict[str, Any]:
    """Parse YAML frontmatter from SKILL.md."""
    import yaml
    
    content = skill_md.read_text(encoding='utf-8')
    meta = {
        "name": skill_md.parent.name,
        "description": "",
        "license": "MIT",
        "category": "uncategorized",
        "tags": [],
        "selection_policy": "automatic"
    }
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1])
                if fm:
                    meta.update(fm)
                    # Handle metadata sub-object
                    if 'metadata' in fm and isinstance(fm['metadata'], dict):
                        meta.update(fm['metadata'])
            except yaml.YAMLError:
                pass
    
    # Extract description from first paragraph if not in frontmatter
    if not meta.get("description"):
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('---'):
                meta["description"] = line[:200]
                break
    
    return meta


def list_skills(args):
    """List all skills."""
    catalog = load_catalog() or build_catalog()
    
    if args.category:
        catalog = [s for s in catalog if s.get('category', '').lower() == args.category.lower()]
    
    if args.json:
        print(json.dumps(catalog, indent=2))
        return
    
    for skill in catalog:
        name = skill.get('name', 'unknown')
        desc = skill.get('description', 'No description')[:80]
        cat = skill.get('category', 'uncategorized')
        policy = skill.get('selection_policy', 'automatic')
        print(f"{name:40} [{cat:20}] ({policy}) - {desc}")


def search_skills(args):
    """Search skills by query."""
    catalog = load_catalog() or build_catalog()
    query = args.query.lower()
    
    results = []
    for skill in catalog:
        name = skill.get('name', '').lower()
        desc = skill.get('description', '').lower()
        tags = ' '.join(skill.get('tags', [])).lower()
        cat = skill.get('category', '').lower()
        
        if query in name or query in desc or query in tags or query in cat:
            results.append(skill)
    
    if args.json:
        print(json.dumps(results, indent=2))
        return
    
    if not results:
        print(f"No skills found for '{args.query}'")
        return
    
    for skill in results:
        name = skill.get('name', 'unknown')
        desc = skill.get('description', 'No description')[:80]
        cat = skill.get('category', 'uncategorized')
        print(f"{name:40} [{cat:20}] - {desc}")


def info_skill(args):
    """Show detailed info for a skill."""
    catalog = load_catalog() or build_catalog()
    
    skill = next((s for s in catalog if s.get('name') == args.skill), None)
    if not skill:
        print(f"Skill '{args.skill}' not found")
        sys.exit(1)
    
    if args.json:
        print(json.dumps(skill, indent=2))
        return
    
    print(f"Name:        {skill.get('name')}")
    print(f"Category:    {skill.get('category', 'uncategorized')}")
    print(f"License:     {skill.get('license', 'MIT')}")
    print(f"Policy:      {skill.get('selection_policy', 'automatic')}")
    print(f"Tags:        {', '.join(skill.get('tags', [])) or 'none'}")
    print(f"Path:        {skill.get('path', 'skills/' + skill.get('name'))}")
    print(f"\nDescription:\n{skill.get('description', 'No description')}")
    
    # Show references if any
    skill_dir = SKILLS_DIR / skill.get('name')
    refs = list((skill_dir / "references").glob("*")) if (skill_dir / "references").exists() else []
    if refs:
        print(f"\nReferences ({len(refs)} files):")
        for r in refs[:10]:
            print(f"  - {r.name}")
        if len(refs) > 10:
            print(f"  ... and {len(refs) - 10} more")


def install_skill(args):
    """Install a skill to target directory."""
    skill_dir = SKILLS_DIR / args.skill
    if not skill_dir.exists():
        print(f"Skill '{args.skill}' not found")
        sys.exit(1)
    
    target = Path(args.target).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    
    dest = target / args.skill
    if dest.exists():
        if args.force:
            shutil.rmtree(dest)
        else:
            print(f"Destination {dest} exists. Use --force to overwrite.")
            sys.exit(1)
    
    shutil.copytree(skill_dir, dest)
    print(f"Installed {args.skill} to {dest}")


def install_all(args):
    """Install all skills to target directory."""
    target = Path(args.target).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    
    catalog = load_catalog() or build_catalog()
    count = 0
    
    for skill in catalog:
        name = skill.get('name')
        skill_dir = SKILLS_DIR / name
        dest = target / name
        
        if dest.exists():
            if args.force:
                shutil.rmtree(dest)
            else:
                print(f"Skipping {name} (exists, use --force)")
                continue
        
        shutil.copytree(skill_dir, dest)
        count += 1
    
    print(f"Installed {count} skills to {target}")


def install_category(args):
    """Install skills by category."""
    catalog = load_catalog() or build_catalog()
    
    filtered = [s for s in catalog if s.get('category', '').lower() == args.category.lower()]
    if not filtered:
        print(f"No skills found in category '{args.category}'")
        print(f"Available categories: {sorted(set(s.get('category', 'uncategorized') for s in catalog))}")
        sys.exit(1)
    
    target = Path(args.target).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for skill in filtered:
        name = skill.get('name')
        skill_dir = SKILLS_DIR / name
        dest = target / name
        
        if dest.exists():
            if args.force:
                shutil.rmtree(dest)
            else:
                print(f"Skipping {name} (exists, use --force)")
                continue
        
        shutil.copytree(skill_dir, dest)
        count += 1
    
    print(f"Installed {count} skills from category '{args.category}' to {target}")


def validate_skill(args):
    """Validate a skill or all skills."""
    import yaml
    
    if args.skill:
        skills_to_check = [args.skill]
    else:
        skills_to_check = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    errors = 0
    warnings = 0
    
    for name in skills_to_check:
        skill_dir = SKILLS_DIR / name
        skill_md = skill_dir / "SKILL.md"
        
        if not skill_md.exists():
            print(f"ERROR: {name}: Missing SKILL.md")
            errors += 1
            continue
        
        # Validate frontmatter
        try:
            content = skill_md.read_text(encoding='utf-8')
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    fm = yaml.safe_load(parts[1])
                    if not fm:
                        print(f"WARNING: {name}: Empty frontmatter")
                        warnings += 1
                    else:
                        required = ['name', 'description', 'license']
                        for field in required:
                            if field not in fm:
                                print(f"WARNING: {name}: Missing frontmatter field '{field}'")
                                warnings += 1
        except yaml.YAMLError as e:
            print(f"ERROR: {name}: Invalid YAML frontmatter: {e}")
            errors += 1
        except Exception as e:
            print(f"ERROR: {name}: {e}")
            errors += 1
        
        # Check for nested .git
        if (skill_dir / ".git").exists():
            print(f"ERROR: {name}: Contains nested .git directory")
            errors += 1
        
        # Check file count reasonable
        file_count = len(list(skill_dir.rglob("*")))
        if file_count > 200:
            print(f"WARNING: {name}: {file_count} files (unusually high)")
            warnings += 1
    
    print(f"\nValidation complete: {errors} errors, {warnings} warnings")
    if errors > 0:
        sys.exit(1)


def generate_catalog(args):
    """Generate catalog.json."""
    catalog = build_catalog()
    
    with open(CATALOG_PATH, 'w') as f:
        json.dump(catalog, f, indent=2)
    
    print(f"Generated catalog.json with {len(catalog)} skills")


def main():
    parser = argparse.ArgumentParser(description="Coding Skills Library CLI")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # list
    p_list = subparsers.add_parser('list', help='List all skills')
    p_list.add_argument('--category', help='Filter by category')
    p_list.add_argument('--json', action='store_true', help='Output as JSON')
    p_list.set_defaults(func=list_skills)
    
    # search
    p_search = subparsers.add_parser('search', help='Search skills')
    p_search.add_argument('query', help='Search query')
    p_search.add_argument('--json', action='store_true', help='Output as JSON')
    p_search.set_defaults(func=search_skills)
    
    # info
    p_info = subparsers.add_parser('info', help='Show skill details')
    p_info.add_argument('skill', help='Skill name')
    p_info.add_argument('--json', action='store_true', help='Output as JSON')
    p_info.set_defaults(func=info_skill)
    
    # install
    p_install = subparsers.add_parser('install', help='Install a skill')
    p_install.add_argument('skill', help='Skill name')
    p_install.add_argument('--target', required=True, help='Target directory')
    p_install.add_argument('--force', action='store_true', help='Overwrite existing')
    p_install.set_defaults(func=install_skill)
    
    # install-all
    p_install_all = subparsers.add_parser('install-all', help='Install all skills')
    p_install_all.add_argument('--target', required=True, help='Target directory')
    p_install_all.add_argument('--force', action='store_true', help='Overwrite existing')
    p_install_all.set_defaults(func=install_all)
    
    # install-category
    p_install_cat = subparsers.add_parser('install-category', help='Install skills by category')
    p_install_cat.add_argument('category', help='Category name')
    p_install_cat.add_argument('--target', required=True, help='Target directory')
    p_install_cat.add_argument('--force', action='store_true', help='Overwrite existing')
    p_install_cat.set_defaults(func=install_category)
    
    # validate
    p_validate = subparsers.add_parser('validate', help='Validate skill(s)')
    p_validate.add_argument('skill', nargs='?', help='Specific skill (default: all)')
    p_validate.set_defaults(func=validate_skill)
    
    # catalog
    p_catalog = subparsers.add_parser('catalog', help='Generate catalog.json')
    p_catalog.set_defaults(func=generate_catalog)
    
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()