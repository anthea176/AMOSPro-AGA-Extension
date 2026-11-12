#!/usr/bin/env python3
"""Static regression/portability test: R44 and R45 candidates, no writes."""
from pathlib import Path
from ap20_utils import digest, split
from audit_ap20 import parse, inspect
from build_aga_compiler_compat import BASELINES, CURSOR, RBSR_OPCODE, STATE_GETTER, build, rbsr


def run():
    candidates = {}
    for revision in ("r44", "r45"):
        original_path, expected_sha, expected_count = BASELINES[revision]
        original = original_path.read_bytes()
        assert digest(original) == expected_sha
        source_tokens, source_parts, source_title = split(original)
        binary, meta = build(revision)
        assert binary == build(revision)[0]
        tokens, parts, title = split(binary)
        assert len(source_parts) == expected_count
        assert len(parts) == expected_count + 2
        assert tokens == source_tokens and title == source_title
        assert inspect(parse(original))["tokens"] == inspect(parse(binary))["tokens"]
        assert not inspect(parse(binary))["issues"]
        assert parts[meta["state_index"]] == STATE_GETTER
        assert parts[CURSOR][meta["cursor_lea"]:meta["cursor_lea"]+4] == rbsr(meta["state_index"])
        assert parts[meta["close_index"]][6:10] == rbsr(meta["state_index"])
        assert parts[meta["close_index"]][10:12] == bytes.fromhex("284a")
        assert parts[meta["close_index"]][-6:] == bytes.fromhex("4cdf7fff4e75")
        for segment, site in meta["close_sites"].items():
            assert parts[segment][site:site+4] == rbsr(meta["close_index"])
            assert parts[segment][:site] == source_parts[segment][:site]
            assert parts[segment][site+4:] == source_parts[segment][site+4:]
        assert RBSR_OPCODE == bytes.fromhex("fe31")
        if revision == "r45":
            assert parts[55] == source_parts[55], "R45 Image Draw must stay untouched"
            assert parts[54].endswith(b"GetP"), "R45 cursor parameter marker must remain"
        else:
            assert parts[54].endswith(bytes(8)), "R44 cursor stored state remains as inert legacy bytes"
        if revision == "r44":
            archived = Path(__file__).resolve().parents[1] / "dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R44_CANDIDATE.Lib"
            assert binary == archived.read_bytes(), "R44 candidate archive is not reproducible"
        assert digest(original_path.read_bytes()) == expected_sha
        candidates[revision] = meta
        print("STATIC PORTABILITY:", revision, meta)
    assert candidates["r45"]["state_index"] == candidates["r44"]["state_index"] + 1
    assert candidates["r45"]["close_index"] == candidates["r44"]["close_index"] + 1
    print("STATIC R44 + R45 TRANSPOSE PASS; no production files modified")


if __name__ == "__main__":
    run()
