import os
import re
from pathlib import Path

def get_title(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('# '):
                title = line.strip()[2:]
                # Clean up known prefixes
                title = re.sub(r'^GÉNÉRAL - ', '', title)
                title = re.sub(r'^BLOC \d+ - ', '', title)
                return title
    return filepath.name.replace('.md', '').capitalize()

def build_tree(path):
    tree = {}
    for item in sorted(path.iterdir()):
        if item.is_dir() and item.name not in ['assets']:
            sub_tree = build_tree(item)
            if sub_tree:
                # capitalize folder name for category
                tree[item.name.capitalize()] = sub_tree
        elif item.is_file() and item.suffix == '.md':
            tree[item.name] = get_title(item)
    return tree

def print_tree(tree, indent=0):
    for k, v in tree.items():
        if isinstance(v, dict):
            print("  " * indent + f"{k}:")
            print_tree(v, indent + 1)
        else:
            print("  " * indent + f"- {v}")

docs = Path('docs')
tree = build_tree(docs)
print_tree(tree)
