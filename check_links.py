import os
import re
from pathlib import Path
import urllib.parse

def check_markdown_links(docs_dir):
    docs_path = Path(docs_dir)
    md_files = list(docs_path.rglob("*.md"))
    
    # Regex for standard markdown links/images: [text](link) or ![alt](link)
    link_pattern = re.compile(r'!?\[.*?\]\((.*?)\)')
    # Regex for HTML img tags: <img src="link"
    img_pattern = re.compile(r'<img[^>]+src="([^"]+)"')
    # Regex for HTML href tags: <a href="link"
    href_pattern = re.compile(r'<a[^>]+href="([^"]+)"')

    errors = []

    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        links = link_pattern.findall(content)
        links.extend(img_pattern.findall(content))
        links.extend(href_pattern.findall(content))

        for link_with_anchor in links:
            # Remove anchors/fragments (e.g., file.md#section)
            link = urllib.parse.unquote(link_with_anchor.split('#')[0])
            
            # Skip empty links, external links, and mailto
            if not link or link.startswith(('http://', 'https://', 'mailto:')):
                continue
                
            # Handle absolute links relative to mkdocs root (usually /docs)
            # In mkdocs, a path starting with '/' usually maps to the 'docs' directory.
            # However, standard markdown absolute paths are relative to filesystem root. 
            # We'll check if they exist relative to docs_path if they start with '/'.
            if link.startswith('/'):
                target_path = docs_path / link.lstrip('/')
            else:
                target_path = (md_file.parent / link).resolve()
            
            if not target_path.exists():
                errors.append(f"Fichier: {md_file.relative_to(docs_path)}\n  -> Lien cassé: {link_with_anchor} (Cherché à: {target_path})")

    if errors:
        print("Erreurs de liens trouvées :")
        for err in errors:
            print(err)
    else:
        print("Aucun lien cassé trouvé !")

if __name__ == "__main__":
    check_markdown_links("docs")
