#!/usr/bin/env python3
"""Gate R5.1 untuk laporan coverage dan benchmark; tidak menjalankan benchmark."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

AKAR = Path(__file__).resolve().parent.parent
BATAS_MS = {'naluri_tick': 2.0, 'predict_2000_terbatas': 5.0}


def _angka(value: Any) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def target_coverage() -> List[str]:
    """Kelompok strict yang sudah mencapai floor coverage wajib terukur."""
    return sorted([str(p.relative_to(AKAR)).replace('\\', '/')
                   for p in (AKAR / 'pycos' / 'dukungan').glob('*.py')]
                  + ['pycos/konektor.py', 'pycos/kontrak.py', 'pycos/inti/persona.py', 'pycos/refleksi/nurani.py',
                     'pycos/bahasa/tutur.py', 'tools/periksa_gate.py', 'tools/periksa_changelog.py'])


def coverage_errors(report: Dict[str, Any], targets: Optional[List[str]] = None) -> List[str]:
    """Minimal 80% baris per berkas, bukan rata-rata yang menyembunyikan berkas."""
    errors = []
    files = report.get('files')
    if not isinstance(files, dict):
        return ['coverage: field files tidak sah']
    for path in target_coverage() if targets is None else targets:
        item = files.get(path)
        summary = item.get('summary') if isinstance(item, dict) else None
        if not isinstance(summary, dict):
            errors.append('coverage: berkas tidak terukur: ' + path)
            continue
        # Line coverage only: do not silently use combined branch percentages.
        covered = summary.get('covered_lines')
        total = summary.get('num_statements')
        if (not isinstance(covered, int) or isinstance(covered, bool)
                or not isinstance(total, int) or isinstance(total, bool)
                or total <= 0 or not 0 <= covered <= total):
            errors.append('coverage: hitungan baris tidak sah: ' + path)
        elif covered / total < .8:
            errors.append('coverage: {} {:.2f}% < 80%'.format(path, 100 * covered / total))
    return errors


def tolok_errors(report: Dict[str, Any]) -> List[str]:
    """Gate ketat: tick <2ms, predict fixture 2000/256 <5ms; gagal bila hilang."""
    errors = []
    if report.get('ok') is not True:
        errors.append('tolok: laporan keseluruhan tidak sukses')
    rows = report.get('tolok')
    if not isinstance(rows, list):
        return errors + ['tolok: field tolok tidak sah']
    for name, limit in BATAS_MS.items():
        matches = [row for row in rows if isinstance(row, dict) and row.get('nama') == name]
        if len(matches) != 1:
            errors.append('tolok: hasil hilang/duplikat: ' + name)
            continue
        row = matches[0]
        value = row.get('per_iterasi_ms')
        iterations = row.get('iterasi')
        if (row.get('ok') is not True or not _angka(value) or value < 0
                or not isinstance(iterations, int) or isinstance(iterations, bool) or iterations < 1):
            errors.append('tolok: pengukuran tidak sah: ' + name)
        elif value >= limit:
            errors.append('tolok: {} {}ms harus <{}ms'.format(name, value, limit))
    return errors


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--coverage', type=Path)
    parser.add_argument('--tolok', type=Path)
    args = parser.parse_args(argv)
    if args.coverage is None and args.tolok is None:
        parser.error('pilih --coverage dan/atau --tolok')
    errors = []
    for path, validator in [(args.coverage, coverage_errors), (args.tolok, tolok_errors)]:
        if path is None:
            continue
        try:
            report = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(report, dict):
                raise ValueError('objek JSON wajib berupa dict')
            errors.extend(validator(report))
        except (OSError, ValueError, TypeError) as exc:
            errors.append('{}: {}'.format(path, exc))
    for error in errors:
        print(error)
    print('Gate: ' + ('GAGAL' if errors else 'LULUS'))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
