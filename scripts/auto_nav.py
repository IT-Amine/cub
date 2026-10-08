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

def get_all_md_files(directory):
    """Récupère récursivement tous les fichiers markdown d'un dossier."""
    md_files = []
    for root, dirs, files in os.walk(directory):
        # Exclure les dossiers cachés
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith('.md'):
                md_files.append(Path(root) / file)
    return sorted(md_files)

def build_nav(docs_path):
    items = []
    
    # 1. Gestion des fichiers à la racine (Contexte & Accueil)
    root_files = [p for p in docs_path.iterdir() if p.is_file() and p.suffix == '.md' and not p.name.startswith('.')]
    
    # Accueil d'abord
    index_file = next((f for f in root_files if f.name == 'index.md'), None)
    if index_file:
        items.append(f'  {{ "{get_title(index_file)}" = "index.md" }}')
        root_files.remove(index_file)
        
    # Le reste des fichiers racines va dans "Contexte"
    if root_files:
        contexte_items = []
        for f in sorted(root_files, key=lambda x: x.name):
            title = get_title(f).replace('"', '\\"')
            contexte_items.append(f'      {{ "{title}" = "{f.name}" }}')
        
        items.append('  { "Contexte" = [\n' + ",\n".join(contexte_items) + '\n  ] }')

    # 2. Gestion des dossiers principaux
    main_dirs = sorted([d for d in docs_path.iterdir() if d.is_dir() and not d.name.startswith('.') and d.name != 'assets'])
    
    for main_dir in main_dirs:
        dir_name = main_dir.name.replace("-", " ").title()
        dir_items = []
        
        # Fichiers à la racine de ce dossier principal (ex: reseau/index.md, reseau/vlsm-routage.md)
        local_files = sorted([f for f in main_dir.iterdir() if f.is_file() and f.suffix == '.md'])
        for f in local_files:
            rel_path = f.relative_to(docs_path).as_posix()
            title = get_title(f).replace('"', '\\"')
            dir_items.append(f'      {{ "{title}" = "{rel_path}" }}')
            
        # Sous-dossiers de niveau 2 (ex: reseau/cisco)
        sub_dirs = sorted([d for d in main_dir.iterdir() if d.is_dir() and not d.name.startswith('.')])
        for sub_dir in sub_dirs:
            sub_dir_name = sub_dir.name.replace("-", " ").title()
            
            # On aplatit tous les fichiers contenus dans ce sous-dossier, peu importe leur profondeur
            all_sub_files = get_all_md_files(sub_dir)
            
            if not all_sub_files:
                continue
                
            sub_items = []
            for f in all_sub_files:
                rel_path = f.relative_to(docs_path).as_posix()
                title = get_title(f).replace('"', '\\"')
                sub_items.append(f'          {{ "{title}" = "{rel_path}" }}')
                
            dir_items.append(f'      {{ "{sub_dir_name}" = [\n' + ",\n".join(sub_items) + '\n      ] }')
            
        if dir_items:
            items.append(f'  {{ "{dir_name}" = [\n' + ",\n".join(dir_items) + '\n  ] }')
            
    return items

def update_toml():
    docs = Path('docs')
    tree_items = build_nav(docs)
    
    nav_str = "nav = [\n" + ",\n".join(tree_items) + "\n]\n"
    
    with open('zensical.toml', 'r', encoding='utf-8') as f:
        content = f.read()
        
    new_content = re.sub(r'nav\s*=\s*\[.*?\]\n', nav_str, content, flags=re.DOTALL)
    
    with open('zensical.toml', 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("zensical.toml a été mis à jour avec une structure optimisée et aplatie !")

if __name__ == "__main__":
    update_toml()
