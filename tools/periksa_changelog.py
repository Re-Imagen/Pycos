#!/usr/bin/env python3
"""Wajibkan catatan kompatibilitas baru untuk diff AST from_dict produksi."""
from __future__ import annotations

import argparse
import ast
from pathlib import Path
import subprocess
from typing import Dict, List

AKAR = Path(__file__).resolve().parents[1]


def loaders(source: str) -> List[str]:
    return sorted(ast.dump(node, include_attributes=False)
                  for node in ast.walk(ast.parse(source))
                  if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                  and node.name == 'from_dict')


def unreleased(text: str) -> str:
    lines = text.splitlines()
    start = next((i + 1 for i, line in enumerate(lines)
                  if line == '## [Unreleased]'), len(lines))
    end = next((i for i in range(start, len(lines))
                if lines[i].startswith('## ')), len(lines))
    return '\n'.join(lines[start:end])


def errors(before: Dict[str, str], after: Dict[str, str],
           old_log: str, new_log: str) -> List[str]:
    old_lines = set(unreleased(old_log).splitlines())
    added = set(unreleased(new_log).splitlines()) - old_lines
    changed = [path for path in sorted(before.keys() | after.keys())
               if loaders(before.get(path, '')) != loaders(after.get(path, ''))]
    return [path + ': perlu baris Kompatibilitas save baru pada Unreleased'
            for path in changed if not any(
                line.startswith('- Kompatibilitas save: `' + path + '` — ')
                and line.split(' — ', 1)[1].strip() for line in added)]


def git(*args: str) -> str:
    return subprocess.run(['git', *args], cwd=AKAR, check=True,
                          stdout=subprocess.PIPE, encoding='utf-8').stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True, help='commit base PR yang tersedia lokal')
    args = parser.parse_args()
    # Invalid base must fail, never silently skip the check.
    git('rev-parse', '--verify', args.base + '^{commit}')
    paths = git('ls-tree', '-r', '--name-only', args.base, '--', 'pycos').splitlines()
    before = {p: git('show', args.base + ':' + p) for p in paths if p.endswith('.py')}
    after = {p.relative_to(AKAR).as_posix(): p.read_text(encoding='utf-8')
             for p in (AKAR / 'pycos').rglob('*.py')}
    log_paths = git('ls-tree', '--name-only', args.base, '--', 'CHANGELOG.md')
    old = git('show', args.base + ':CHANGELOG.md') if log_paths.strip() else ''
    problems = errors(before, after, old, (AKAR / 'CHANGELOG.md').read_text(encoding='utf-8'))
    for problem in problems:
        print(problem)
    print('Changelog: ' + ('GAGAL' if problems else 'LULUS'))
    return int(bool(problems))


if __name__ == '__main__':
    raise SystemExit(main())
