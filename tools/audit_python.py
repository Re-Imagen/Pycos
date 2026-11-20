#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Indeks AST source Python proyek; dependensi dan keluaran build dikecualikan.

python3 tools/audit_python.py
python3 tools/audit_python.py --check

Indeks struktural, bukan coverage eksekusi atau verifikasi semantik otomatis.
Generator juga mengindeks source dirinya sendiri. Output deterministik supaya
--check mendeteksi penambahan/penghapusan source maupun perubahan isinya.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import os
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

AKAR = Path(__file__).resolve().parents[1]
DIREKTORI_NON_SOURCE = frozenset({
    ".git", ".venv", "venv", "env", "build", "dist", "node_modules",
    "site-packages", "__pycache__", ".tox", ".nox", ".mypy_cache",
    ".pytest_cache", ".ruff_cache",
})


def inventaris(akar: Path) -> List[Tuple[Path, str, ast.Module]]:
    """Baca setiap .py; agregasikan galat tanpa melewati berkas yang gagal."""
    hasil = []
    galat = []
    paths = []
    for direktori, dirs, files in os.walk(akar):
        dirs[:] = sorted(d for d in dirs if d not in DIREKTORI_NON_SOURCE)
        paths.extend(Path(direktori) / f for f in files if f.endswith(".py"))
    for jalur in sorted(paths):
        try:
            teks = jalur.read_text(encoding="utf-8")
            pohon = ast.parse(teks, filename=str(jalur))
            hasil.append((jalur.relative_to(akar), teks, pohon))
        except (OSError, UnicodeError, SyntaxError) as exc:
            galat.append("{}: {}".format(jalur.relative_to(akar), exc))
    if galat:
        raise ValueError("Berkas gagal dianalisis:\n" + "\n".join(galat))
    return hasil


class IndeksCallable(ast.NodeVisitor):
    """Catat seluruh fungsi termasuk nested, private, async, dan demo."""

    def __init__(self) -> None:
        self.scope: List[str] = []
        self.baris: List[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        nama = ".".join(self.scope + [node.name])
        nodes = list(ast.walk(node))
        kontrol = sum(isinstance(x, (ast.If, ast.For, ast.AsyncFor, ast.While,
                                     ast.Try, ast.With, ast.AsyncWith, ast.BoolOp,
                                     ast.comprehension)) for x in nodes)
        mutasi = sum(isinstance(x, (ast.Assign, ast.AnnAssign, ast.AugAssign,
                                    ast.Delete)) for x in nodes)
        handler = sum(isinstance(x, ast.ExceptHandler) for x in nodes)
        calls = sorted({ast.unparse(x.func) for x in nodes if isinstance(x, ast.Call)})
        self.baris.append(
            "- L{}–{} **`{}`** · kontrol={}, assignment/delete={}, except={} · Call: {}".format(
                node.lineno, node.end_lineno, nama, kontrol, mutasi, handler,
                ", ".join("`" + x.replace("`", "") + "`" for x in calls) or "tidak ada"))
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    visit_AsyncFunctionDef = visit_FunctionDef


def laporan(akar: Path) -> str:
    """Buat indeks lengkap beserta hash untuk verifikasi kebaruan source."""
    data = inventaris(akar)
    baris = ["# Lampiran audit AST seluruh Python Pycos", "",
             "Dibuat oleh `python3 tools/audit_python.py`; periksa kebaruan dengan `--check`.",
             "Seluruh source proyek termasuk private/demo/init/tool diperiksa; bukan paket dependensi atau build.",
             "Direktori non-source yang dikecualikan: " + ", ".join(sorted(DIREKTORI_NON_SOURCE)) + ".",
             "Indikator kontrol/mutasi termasuk scope nested; bukan kompleksitas siklomatik formal.",
             "Nama call bersifat sintaksis, bukan resolusi callback atau monkey patch runtime.",
             "Analisis semantik dan batas bukti: [audit lanjutan](AUDIT_PYTHON_LANJUTAN.md).", "",
             "Jumlah berkas: **{}**.".format(len(data)), ""]
    for jalur, teks, pohon in data:
        nodes = list(ast.walk(pohon))
        funcs = [x for x in nodes if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))]
        classes = [x for x in nodes if isinstance(x, ast.ClassDef)]
        imports = sorted({ast.unparse(x) for x in nodes
                          if isinstance(x, (ast.Import, ast.ImportFrom))})
        broad = [x.lineno for x in nodes if isinstance(x, ast.ExceptHandler)
                 and (x.type is None or isinstance(x.type, ast.Name)
                      and x.type.id in ("Exception", "BaseException"))]
        baris.extend(["## `{}`".format(jalur.as_posix()), "",
                      "SHA-256: `{}`".format(hashlib.sha256(teks.encode("utf-8")).hexdigest()),
                      "", "{} baris; {} kelas; {} fungsi/metode termasuk nested.".format(
                          len(teks.splitlines()), len(classes), len(funcs)), "",
                      "Kelas: " + (", ".join("`{}` L{}".format(x.name, x.lineno)
                                              for x in classes) or "tidak ada") + ".",
                      "Handler luas: " + (", ".join(map(str, broad)) or "tidak ada") + ".", "",
                      "Impor (termasuk lazy/TYPE_CHECKING): " +
                      ("; ".join("`" + x + "`" for x in imports) or "tidak ada") + ".", ""])
        visitor = IndeksCallable()
        visitor.visit(pohon)
        baris.extend(visitor.baris + [""])
    return "\n".join(baris)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=AKAR)
    parser.add_argument("--output", type=Path, default=AKAR / "docs/AUDIT_PYTHON_RINCI.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if not args.root.is_dir():
            raise ValueError("root harus direktori yang ada")
        teks = laporan(args.root.resolve())
        if args.check:
            if not args.output.is_file() or args.output.read_text(encoding="utf-8") != teks:
                print("Indeks audit tertinggal; jalankan kembali generator.")
                return 1
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(teks, encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
