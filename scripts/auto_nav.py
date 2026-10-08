import os
import re
from pathlib import Path

def get_title(filepath):
    if filepath.suffix != '.md':
        return filepath.name
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('# '):
                title = line.strip()[2:]
                title = re.sub(r'^GÉNÉRAL - ', '', title)
                title = re.sub(r'^BLOC \d+ - ', '', title)
                return title
    return filepath.name.replace('.md', '').replace('-', ' ').title()

def indent_lines(text, spaces):
    prefix = ' ' * spaces
    return '\n'.join(prefix + line if line.strip() else line for line in text.split('\n'))

def build_tree(path, base_path, indent=2):
    items = []
    
    entries = sorted(path.iterdir(), key=lambda x: (x.is_dir(), x.name))
    
    for item in entries:
        if item.name.startswith('.') or item.name == 'assets':
            continue
            
        if item.is_dir():
            sub_tree = build_tree(item, base_path, indent + 4)
            if sub_tree:
                folder_name = item.name.replace("-", " ").title()
                space = ' ' * indent
                items.append(f'{space}{{ "{folder_name}" = [\n' + ",\n".join(sub_tree) + f'\n{space}] }}')
        elif item.is_file() and item.suffix == '.md':
            rel_path = item.relative_to(base_path).as_posix()
            title = get_title(item)
            title = title.replace('"', '\\"')
            space = ' ' * indent
            items.append(f'{space}{{ "{title}" = "{rel_path}" }}')
            
    return items

def update_toml():
    docs = Path('docs')
    tree_items = build_tree(docs, docs, indent=2)
    
    nav_str = "nav = [\n" + ",\n".join(tree_items) + "\n]\n"
    
    with open('zensical.toml', 'r', encoding='utf-8') as f:
        content = f.read()
        
    new_content = re.sub(r'nav\s*=\s*\[.*?\]\n', nav_str, content, flags=re.DOTALL)
    
    with open('zensical.toml', 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("zensical.toml a été mis à jour automatiquement !")

if __name__ == "__main__":
    update_toml()
