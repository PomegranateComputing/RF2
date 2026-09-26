"""Install the six generated corpse assets after Opus has reviewed MODELDEF.
The handoff importer's allowed prefixes do not include src/models; no map is touched.
This explicit, deterministic install step avoids pretending OBJ files are sprites.
"""
from pathlib import Path
import shutil,hashlib
here=Path(__file__).resolve().parent
root=here.parents[1]
for p in sorted((here/'enemies/model_exports').glob('*')):
    assert p.suffix in ('.obj','.png')
    dst=root/'src/models/rf2_art_01'/p.name
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(p,dst)
    print(dst.relative_to(root),hashlib.sha256(dst.read_bytes()).hexdigest())
