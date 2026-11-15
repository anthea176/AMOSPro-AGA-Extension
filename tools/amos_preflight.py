#!/usr/bin/env python3
"""Conservative read-only preflight for AMOS Professional ASCII exports.

This does NOT parse the complete AMOS grammar, compile a program, or validate
AGA extension ABI/runtime behavior. It flags only high-signal patterns.

Usage: python scripts/amos_preflight.py [--strict-target] foo.asc [bar.asc ...]
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    file: str
    line: int
    message: str


RE_IF = re.compile(r"^If\b", re.I)
RE_ELSE_IF = re.compile(r"^Else\s+If\b", re.I)
RE_ELSE = re.compile(r"^Else\b", re.I)
RE_END_IF = re.compile(r"^End\s+If\b", re.I)
RE_THEN = re.compile(r"\bThen\b", re.I)
RE_PROCEDURE = re.compile(r"^Procedure\s+([_A-Za-z][_A-Za-z0-9]*)\b", re.I)
RE_END_PROC = re.compile(r"^End\s+Proc\b", re.I)
RE_POP_PROC = re.compile(r"\bPop\s+Proc\b", re.I)
RE_DIM = re.compile(r"^Dim\s+", re.I)
RE_GLOBAL = re.compile(r"^Global\s+", re.I)
RE_ARRAY = re.compile(r"([_A-Za-z][_A-Za-z0-9]*)\s*\(")
RE_RESTORE = re.compile(r"^Restore\s+([_A-Za-z][_A-Za-z0-9]*)\b", re.I)
RE_LABEL = re.compile(r"^\s*([_A-Za-z][_A-Za-z0-9]*)\s*:")
RE_FOR_COUNT = re.compile(
    r"^For\s+[_A-Za-z][_A-Za-z0-9]*\s*=\s*0\s+To\s+"
    r"[_A-Za-z][_A-Za-z0-9]*\s*-\s*1\b", re.I
)
RE_SET_ZONE_ZERO = re.compile(
    r"^Set\s+Zone\s+[^,]+,\s*0\s*,\s*0\s+To\s+0\s*,\s*0\s*$", re.I
)
RE_AGA_OPEN = re.compile(r"\bAga\s+Screen\s+Open\s*\(", re.I)
RE_AGA_CLOSE = re.compile(r"\bAga\s+Screen\s+Close\b", re.I)
RE_AMOS_FRONT = re.compile(r"\bAmos\s+To\s+Front\b", re.I)
RE_AGA_DETECT_ONE = re.compile(r"\bAga\s+Detect\s*=\s*1\b", re.I)
RE_AGA_BOB_PROBE = re.compile(r"\bAga\s+Bob\s+Probe\b", re.I)


def read_asc(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            pass
    raise AssertionError("latin-1 should decode all byte values")


def remove_strings_comments(line: str) -> str:
    """Blank string literals and apostrophe comments, preserve code punctuation."""
    if re.match(r"^\s*Rem(?:\s|$)", line, re.I):
        return ""
    buf = []
    quoted = False
    index = 0
    while index < len(line):
        ch = line[index]
        if quoted:
            if ch == '"':
                if index + 1 < len(line) and line[index + 1] == '"':
                    buf.extend((" ", " "))
                    index += 2
                    continue
                quoted = False
            buf.append(" ")
        else:
            if ch == "'":
                break
            if ch == '"':
                quoted = True
                buf.append(" ")
            else:
                buf.append(ch)
        index += 1
    return "".join(buf)


def analyze_source(path: Path, strict_target: bool = False) -> list[Finding]:
    source, _encoding = read_asc(path)
    findings: list[Finding] = []
    filename = str(path)

    def emit(level: str, code: str, line: int, message: str) -> None:
        findings.append(Finding(level, code, filename, line, message))

    structured_if: list[int] = []
    declared_arrays: set[str] = set()
    procedures: set[str] = set()
    current_proc: dict | None = None
    seen_aga_open = False
    seen_aga_close = False
    seen_amos_front = False

    def end_procedure(line_num: int, has_return: bool) -> None:
        nonlocal current_proc
        assert current_proc is not None
        if has_return and current_proc["pops"]:
            emit("ERREUR", "POP_PROC_RETURN", current_proc["pops"][0],
                 "Pop Proc dans une procedure End Proc[...] : Param peut etre obsolete")
        for restore_line, label in current_proc["restores"]:
            if label not in current_proc["labels"]:
                emit("AVERTISSEMENT", "RESTORE_SCOPE", restore_line,
                     "Restore vers etiquette non trouvee dans cette procedure (verifier DATA local)")
        current_proc = None

    for line_num, raw_line in enumerate(source.splitlines(), start=1):
        if len(raw_line) > 255:
            emit("ERREUR", "LINE_255", line_num,
                 f"ligne physique de {len(raw_line)} caracteres (maximum AMOS : 255)")
        elif len(raw_line) > 220:
            emit("ERREUR" if strict_target else "AVERTISSEMENT", "LINE_220", line_num,
                 f"ligne physique de {len(raw_line)} caracteres (cible nouveau code : 220)")

        clean = remove_strings_comments(raw_line)
        label = RE_LABEL.match(clean)
        if label is not None and current_proc is not None:
            current_proc["labels"].add(label.group(1).upper())

        if RE_AGA_OPEN.search(clean):
            seen_aga_open = True
        if RE_AGA_CLOSE.search(clean):
            seen_aga_close = True
        if RE_AMOS_FRONT.search(clean):
            seen_amos_front = True
        if RE_AGA_DETECT_ONE.search(clean):
            emit("AVERTISSEMENT", "AGA_DETECT_BOOLEAN", line_num,
                 "Aga Detect peut retourner -1 pour VRAI; tester =0 pour absence ou <>0")
        if RE_AGA_BOB_PROBE.search(clean):
            emit("AVERTISSEMENT", "AGA_BOB_PROBE", line_num,
                 "Aga Bob Probe absente de la candidate R87; verifier la version cible")
        if current_proc is not None and RE_POP_PROC.search(clean):
            current_proc["pops"].append(line_num)

        for piece in clean.split(":"):
            statement = piece.strip()
            if not statement:
                continue
            if re.match(r"^Rem(?:\s|$)", statement, re.I):
                break
            if match := RE_PROCEDURE.match(statement):
                proc_name = match.group(1).upper()
                if proc_name in procedures:
                    emit("ERREUR", "DUP_PROC", line_num,
                         f"declaration Procedure repetee : {proc_name}")
                procedures.add(proc_name)
                if current_proc is not None:
                    emit("ERREUR", "NESTED_PROC", line_num,
                         "Procedure imbriquee / End Proc manquant")
                current_proc = {"start": line_num, "pops": [], "restores": [], "labels": set()}
                continue
            if RE_END_PROC.match(statement):
                if current_proc is None:
                    emit("ERREUR", "END_PROC_ORPHAN", line_num,
                         "End Proc sans Procedure active")
                else:
                    end_procedure(line_num, "[" in statement)
                continue
            if RE_DIM.match(statement):
                for array in RE_ARRAY.findall(RE_DIM.sub("", statement, count=1)):
                    declared_arrays.add(array.upper())
            elif RE_GLOBAL.match(statement):
                for array in RE_ARRAY.findall(RE_GLOBAL.sub("", statement, count=1)):
                    if array.upper() not in declared_arrays:
                        emit("ERREUR", "GLOBAL_BEFORE_DIM", line_num,
                             f"Global {array}() avant Dim {array}(...) dans ce fichier")
            elif match := RE_RESTORE.match(statement):
                if current_proc is not None:
                    current_proc["restores"].append((line_num, match.group(1).upper()))

            if RE_END_IF.match(statement):
                if structured_if:
                    structured_if.pop()
                else:
                    emit("ERREUR", "END_IF_ORPHAN", line_num,
                         "End If sans If structure actif")
            elif RE_ELSE_IF.match(statement):
                if not structured_if:
                    emit("ERREUR", "ELSE_IF_ORPHAN", line_num,
                         "Else If sans If structure actif")
                if RE_THEN.search(statement):
                    emit("ERREUR", "THEN_IN_STRUCTURED_IF", line_num,
                         "Then interdit dans un test If ... End If")
            elif RE_ELSE.match(statement):
                if not structured_if:
                    emit("ERREUR", "ELSE_ORPHAN", line_num,
                         "Else sans If structure actif")
            elif RE_IF.match(statement):
                if RE_THEN.search(statement):
                    if structured_if:
                        emit("ERREUR", "THEN_IN_STRUCTURED_IF", line_num,
                             "If ... Then imbrique dans un test If ... End If")
                else:
                    structured_if.append(line_num)

            if RE_FOR_COUNT.match(statement):
                emit("AVERTISSEMENT", "ZERO_COUNT_LOOP", line_num,
                     "For 0 To COUNT-1 : confirmer qu'une garde COUNT>0 empeche COUNT=0")
            if RE_SET_ZONE_ZERO.match(statement):
                emit("AVERTISSEMENT", "ZONE_ZERO", line_num,
                     "Set Zone 0,0 To 0,0 ne desactive pas la zone : utiliser Reset Zone")

    if current_proc is not None:
        emit("ERREUR", "PROC_UNCLOSED", current_proc["start"],
             "Procedure sans End Proc")
    for open_line in structured_if:
        emit("ERREUR", "IF_UNCLOSED", open_line,
             "If structure sans End If")
    if seen_aga_open and not seen_aga_close:
        emit("AVERTISSEMENT", "AGA_MISSING_CLOSE", 1,
             "Aga Screen Open detecte sans Aga Screen Close dans le fichier")
    if seen_aga_open and not seen_amos_front:
        emit("AVERTISSEMENT", "AGA_MISSING_FRONT", 1,
             "Aga Screen Open detecte sans Amos To Front dans le fichier")
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict-target", action="store_true",
                        help="consider physical lines >220 characters blocking")
    parser.add_argument("--fail-on-warnings", action="store_true")
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args(argv)
    all_findings: list[Finding] = []
    for path in args.files:
        try:
            all_findings.extend(analyze_source(path, args.strict_target))
        except (OSError, UnicodeError) as exc:
            all_findings.append(Finding("ERREUR", "READ_ERROR", str(path), 0, str(exc)))
    for finding in all_findings:
        print(f"{finding.file}:{finding.line}: {finding.level} [{finding.code}]: {finding.message}")
    errors = sum(item.level == "ERREUR" for item in all_findings)
    warnings = sum(item.level == "AVERTISSEMENT" for item in all_findings)
    if errors:
        print(f"AMOS PREFLIGHT: FAIL ({errors} erreur(s), {warnings} avertissement(s))")
        return 2
    if warnings:
        print(f"AMOS PREFLIGHT: PASS WITH WARNINGS ({warnings} avertissement(s))")
        return 1 if args.fail_on_warnings else 0
    print("AMOS PREFLIGHT: PASS (controle statique uniquement; Runtime/Compiler non testes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
