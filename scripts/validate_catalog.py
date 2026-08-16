#!/usr/bin/env python3
"""
validate_catalog.py - Validate catalog.json freshness and structure
"""

import json
import sys
from pathlib import Path

CATALOG_PATH = Path(__file__).parent.parent / "catalog.json"
SKILLS_DIR = Path(__file__).parent.parent / "skills"


def main():
    # Load catalog
    if not CATALOG_PATH.exists():
        print("ERROR: catalog.json not found. Run `python scripts/skillctl.py catalog` first.")
        sys.exit(1)
    
    with open(CATALOG_PATH, encoding='utf-8') as f:
        try:
            catalog = json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in catalog.json: {e}")
            sys.exit(1)
    
    # Count actual skills
    actual_skills = [d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith('.') and (d / "SKILL.md").exists()]
    
    catalog_names = {s.get('name') for s in catalog if s.get('name')}
    actual_names = {d.name for d in actual_skills}
    
    missing_in_catalog = actual_names - catalog_names
    extra_in_catalog = catalog_names - actual_names
    
    errors = 0
    warnings = 0
    
    if missing_in_catalog:
        print(f"ERROR: {len(missing_in_catalog)} skills in filesystem but not in catalog:")
        for name in sorted(missing_in_catalog):
            print(f"  - {name}")
        errors += 1
    
    if extra_in_catalog:
        print(f"WARNING: {len(extra_in_catalog)} skills in catalog but not in filesystem:")
        for name in sorted(extra_in_catalog):
            print(f"  - {name}")
        warnings += 1
    
    # Validate catalog structure
    for i, skill in enumerate(catalog):
        if not skill.get('name'):
            print(f"ERROR: Catalog entry {i}: missing 'name'")
            errors += 1
        if not skill.get('description'):
            print(f"WARNING: {skill.get('name', f'entry {i}')}: missing 'description'")
            warnings += 1
        if not skill.get('category'):
            print(f"WARNING: {skill.get('name', f'entry {i}')}: missing 'category'")
            warnings += 1
        if not skill.get('path'):
            print(f"WARNING: {skill.get('name', f'entry {i}')}: missing 'path'")
            warnings += 1
    
    print(f"\nCatalog: {len(catalog)} entries")
    print(f"Filesystem: {len(actual_skills)} skills")
    print(f"Errors: {errors}, Warnings: {warnings}")
    
    if errors > 0:
        sys.exit(1)
    
    print("[OK] Catalog is valid and up to date")


if __name__ == '__main__':
    main()