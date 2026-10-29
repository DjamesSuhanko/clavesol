"""Banner da entrada; imagens numeradas são ordenadas numericamente."""
from html import escape
from pathlib import Path
import re
from urllib.parse import quote


def images(root):
    numbered=[]
    for path in (root/'carrossel').iterdir():
        if path.is_file() and re.fullmatch(r'\d+',path.stem) and path.suffix.lower() in ('.png','.jpg','.jpeg','.webp','.svg'):
            numbered.append((int(path.stem),path.name))
    numbered.sort()
    if len({n for n,_ in numbered}) != len(numbered):
        raise ValueError('Há números repetidos em carrossel/ (por exemplo 01.jpg e 01.png).')
    return [name for _,name in numbered] or ['padrao.svg']


def banner(root,base):
    names=images(root)
    slides=''.join(f'<img src="{base}/carrossel/{quote(name)}" alt="{escape((root/"carrossel"/(Path(name).stem+".txt")).read_text().strip(),quote=True) if (root/"carrossel"/(Path(name).stem+".txt")).exists() else "Banner Clave Sol"}" width="1600" height="320"'+(' hidden loading="lazy"' if i else ' fetchpriority="high"')+'>' for i,name in enumerate(names))
    controls='<div class="carousel-controls" hidden><button type="button" data-prev aria-label="Imagem anterior">‹</button><span data-count role="status" aria-live="polite"></span><button type="button" data-next aria-label="Próxima imagem">›</button></div>' if len(names)>1 else ''
    return f'<link rel="stylesheet" href="{base}/assets/carrossel.css"><section class="collection-carousel" aria-label="Destaques do acervo" aria-roledescription="carrossel" tabindex="0"><div class="carousel-slides">{slides}</div>{controls}</section><script type="module" src="{base}/assets/carrossel.mjs"></script>'
