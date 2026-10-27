"""Publica solo public/ en gh-pages. Ejecutar únicamente con pedido de publicación."""
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def git(*args, **kwargs):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], **kwargs).decode().strip()

assert not git('status', '--porcelain'), 'Guardar primero los cambios que se van a publicar.'
subprocess.run(['node', str(ROOT / 'scripts/check.mjs')], check=True)
remote = git('ls-remote', 'origin', 'refs/heads/gh-pages')
parent = None
if remote:
    subprocess.run(['git', '-C', str(ROOT), 'fetch', 'origin', 'gh-pages'], check=True)
    parent = git('rev-parse', 'FETCH_HEAD')
with tempfile.TemporaryDirectory(prefix='shelby-pages-index-') as folder:
    env = dict(os.environ, GIT_INDEX_FILE=str(Path(folder) / 'index'))
    git('read-tree', 'HEAD:public', env=env)
    empty = git('hash-object', '-w', '--stdin', input=b'')
    git('update-index', '--add', '--cacheinfo', f'100644,{empty},.nojekyll', env=env)
    tree = git('write-tree', env=env)
    if parent and git('rev-parse', f'{parent}^{{tree}}') == tree:
        print('gh-pages ya contiene exactamente los archivos públicos actuales.')
        raise SystemExit(0)
    commit = git('commit-tree', tree, *(['-p', parent] if parent else []), input=b'Deploy standalone public routines preview\n')
    git('update-ref', 'refs/heads/gh-pages', commit)
    subprocess.run(['git', '-C', str(ROOT), 'push', 'origin', 'gh-pages:gh-pages'], check=True)
    print('Rama gh-pages publicada con public/ y .nojekyll; main permanece intacta.')
    print('La activación y el estado de GitHub Pages se comprueban por separado.')
