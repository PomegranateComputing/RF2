#!/usr/bin/env python3
"""Plain-text extraction of the novel, so that the line numbers cited in docs/production/ are reproducible.

The novel is not copied into the repository: this reads the owner's EPUB where it is and writes the text to an
output folder outside the project (a scratch or temp folder). Line numbers in the canon documents are the line
numbers of body.txt produced here (EPUB/text/body.xhtml, paragraphs and breaks turned into newlines, blank lines
kept).

Reference EPUB: La_Couleur_de_la_Pomegrenade_KDP_MASTER_COUVERTURE.epub,
SHA-256 b5f76b0e64e8963ef28ddf346671e04d53aca9f23123a1311fcbc221b50a4af9.

Usage: python scripts/production/novel_extract.py <book.epub> <output folder>
"""
import hashlib, html, re, sys, zipfile
from pathlib import Path

REFERENCE = 'b5f76b0e64e8963ef28ddf346671e04d53aca9f23123a1311fcbc221b50a4af9'


def main():
    epub, out = Path(sys.argv[1]), Path(sys.argv[2])
    digest = hashlib.sha256(epub.read_bytes()).hexdigest()
    print('sha256', digest, 'reference' if digest == REFERENCE else 'DIFFERENT FROM THE REFERENCE EDITION')
    out.mkdir(parents=True, exist_ok=True)
    z = zipfile.ZipFile(epub)
    for name in (n for n in z.namelist() if n.endswith('.xhtml')):
        raw = z.read(name).decode('utf-8', 'replace')
        raw = re.sub(r'<(br|/p|/h\d|/li|/div)[^>]*>', '\n', raw)
        text = html.unescape(re.sub(r'<[^>]+>', '', raw))
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        (out / (Path(name).stem + '.txt')).write_text(text, encoding='utf-8')
        print(name, len(text.splitlines()), 'lines')


if __name__ == '__main__':
    main()
