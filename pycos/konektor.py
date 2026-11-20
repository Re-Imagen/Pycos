# -*- coding: utf-8 -*-
"""Adapter host berbasis snapshot JSON; tidak memajukan NPC/dunia host.

`npc` adalah snapshot penuh `Naluri.to_dict()`, bukan instance hidup.
Jalankan `python -m pycos.konektor --json` dengan satu request di stdin.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Any, Dict, List, Mapping, Optional, Sequence, cast

__all__ = ['observasi', 'aksi']
BATAS_INPUT = 1_000_000


def _salin(value: Any) -> Any:
    """Salin nilai JSON ketat, tanpa coerce key/tuple atau NaN diam-diam."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    if isinstance(value, list):
        return [_salin(item) for item in value]
    if isinstance(value, dict) and all(isinstance(k, str) for k in value):
        return {k: _salin(v) for k, v in value.items()}
    raise ValueError('payload wajib JSON: key string, angka hingga, list/dict')


def _npc(snapshot: Mapping[str, Any]) -> Any:
    from pycos.inti.naluri import Naluri
    if not isinstance(snapshot, dict):
        raise ValueError('npc wajib snapshot penuh berupa dict')
    return Naluri.from_dict(_salin(snapshot))


def observasi(npc: Mapping[str, Any], dunia: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Peta persepsi host ke events tick, tidak membaca/menguras antrean dunia.

    dunia = {ringkas: str, events: list[dict]}. Events divalidasi oleh clone
    Naluri, sehingga drive/angka/domain invalid gagal sebelum host menerapkan.
    """
    clone = _npc(npc)
    data = _salin(dunia)
    if not isinstance(data, dict):
        raise ValueError('dunia wajib dict persepsi')
    if set(data) - {'ringkas', 'events'}:
        raise ValueError('field dunia tidak dikenal; gunakan ringkas/events')
    ringkas = data.get('ringkas', '')
    events = data.get('events', [])
    if not isinstance(ringkas, str) or not isinstance(events, list):
        raise ValueError('ringkas wajib string dan events wajib list')
    if not all(isinstance(e, dict) for e in events):
        raise ValueError('setiap event wajib dict')
    if ringkas.strip():
        events.append({'stimulus': ringkas, 'source': 'host', 'reason': ringkas})
    # Tick hanya pada clone untuk memakai validasi domain produksi.
    clone.params["strict_events"] = True
    clone.tick(events=events)
    return events


def aksi(npc: Mapping[str, Any], kandidat: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Pilih aksi dengan mesin asli pada clone; hasil lepas dan JSON ketat.

    Tidak menerapkan aksi, memberi reward atau mencatat eligibility pada NPC
    host. Biaya clone adalah trade-off isolasi, bukan API loop real-time cepat.
    """
    clone = _npc(npc)
    data = _salin(kandidat)
    if not isinstance(data, list) or not all(isinstance(c, dict) for c in data):
        raise ValueError('kandidat wajib list dict')
    from pycos.kontrak import DRIVE_KEYS
    for candidate in data:
        effects = candidate.get('drive_effects', {})
        if not isinstance(effects, dict) or set(effects) - set(DRIVE_KEYS):
            raise ValueError('drive_effects wajib dict drive yang dikenal')
        for value in list(effects.values()) + [candidate.get('cost', 0.0),
                                               candidate.get('prob', 1.0)]:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError('efek/cost/prob wajib angka hingga, bukan bool')
        if candidate.get('cost', 0) < 0 or not 0 <= candidate.get('prob', 1) <= 1:
            raise ValueError('cost wajib non-negatif; prob wajib 0..1')
    result = clone.choose_action(data, record_eligibility=False)
    return cast(Dict[str, Any], json.loads(json.dumps(result, ensure_ascii=False, allow_nan=False)))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', required=True,
                        help='baca satu request stdin dan tulis satu respons JSON')
    parser.add_argument('--input', help='berkas request JSON; default stdin')
    args = parser.parse_args(argv)
    try:
        if args.input:
            with open(args.input, encoding='utf-8') as source:
                raw = source.read(BATAS_INPUT + 1)
        else:
            raw = sys.stdin.read(BATAS_INPUT + 1)
        if len(raw) > BATAS_INPUT:
            raise ValueError('request melampaui batas 1000000 karakter')
        request = _salin(json.loads(raw))
        if not isinstance(request, dict) or set(request) - {'npc', 'dunia', 'kandidat', 'seed'}:
            raise ValueError('request wajib dict npc/dunia/kandidat/seed')
        from pycos.inti.naluri import Naluri
        seed = request.get('seed', 7)
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise ValueError('seed wajib int')
        state = request.get('npc')
        if state is None:
            state = Naluri(name='HostNPC', rng_seed=seed).to_dict()
        events = observasi(state, request.get('dunia', {}))
        choice = aksi(state, request.get('kandidat', []))
        # Pilihan didasarkan pada snapshot awal; host memilih kapan events di-tick.
        result = {'ok': True, 'events': events, 'pilihan': choice,
                  'hud': _npc(state).hud_state()}
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 0
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError, OSError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
