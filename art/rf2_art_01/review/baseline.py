"""Build a comparison PK3: base art + Opus 844b50f code + identical evidence driver."""
from pathlib import Path
import subprocess,zipfile,hashlib,json
ROOT=Path(__file__).resolve().parents[3]
REPO=Path(r'C:/PROJECTS/RF2_UZDOOM')
def main():
    original=zipfile.ZipFile(ROOT/'art_pass/base/RF2_BASE_REVIEW_ONLY.pk3')
    data={n:original.read(n) for n in original.namelist()}
    paths=subprocess.check_output(['git','-C',str(REPO),'diff','--name-only','6e1a31b','844b50f'],text=True).splitlines()
    for p in paths:
        if p.startswith('src/'):
            data[p[4:]]=subprocess.check_output(['git','-C',str(REPO),'show','844b50f:'+p])
    for p in ['src/zscript/rf/dev.zs','src/CVARINFO']:
        data[p[4:]]=(ROOT/p).read_bytes()
    dest=ROOT/'art_pass/base/COMPARISON_844b50f.pk3'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for n,d in sorted(data.items()):z.writestr(n,d)
    print(dest,hashlib.sha256(dest.read_bytes()).hexdigest())
if __name__=='__main__':main()
