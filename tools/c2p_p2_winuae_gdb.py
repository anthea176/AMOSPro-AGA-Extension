#!/usr/bin/env python3
"""Read-only WinUAE GDB/RSP snapshot of AMOSPro AGA SB0/SB1 (P2).

WinUAE GDB server (6.1 beta 18+): 127.0.0.1:2345. Connection pauses the
emulated CPU; disconnect restores execution. NEVER sends memory writes,
register writes, breakpoints, or steps. Not a C2P/WinUAE Gate B result.

Requires the AMOS program to be PAUSED inside an AGA extension operation or
otherwise keep a valid AMOS A5, with the 320x256x256 screen/DB allocated.
"""
from __future__ import annotations

import argparse
import json
import socket
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from c2p_p2_layout_check import check_document


class ProbeError(RuntimeError):
    pass


class RSP:
    def __init__(self, host: str = "127.0.0.1", port: int = 2345) -> None:
        if host != "127.0.0.1":
            raise ProbeError("Only WinUAE's local loopback server is permitted")
        self.host = host
        self.port = port
        self.sock: socket.socket | None = None

    def __enter__(self) -> "RSP":
        self.sock = socket.create_connection((self.host, self.port), timeout=5)
        self.sock.settimeout(8)
        stopped = self.command("?")
        if not stopped.startswith(("S", "T")):
            raise ProbeError(f"WinUAE did not report a stopped CPU: {stopped!r}")
        return self

    def __exit__(self, *_ignored: object) -> None:
        if self.sock is not None:
            try:
                self.command("D")  # detach: WinUAE resumes emulation
            except (OSError, ProbeError):
                pass
            finally:
                self.sock.close()
                self.sock = None

    def _recv_exact(self, count: int) -> bytes:
        assert self.sock is not None
        data = bytearray()
        while len(data) < count:
            incoming = self.sock.recv(count - len(data))
            if not incoming:
                raise ProbeError("WinUAE closed the GDB connection")
            data.extend(incoming)
        return bytes(data)

    def command(self, text: str) -> str:
        # Strict allowlist; never send M/P/G/Z/z, monitor commands or vCont.
        if not (text in ("?", "g", "D", "qSupported") or
                text.startswith("m") and "," in text or
                text.startswith("qXfer:memory-map:read::")):
            raise ProbeError(f"Unsupported or potentially mutating GDB packet {text!r}")
        assert self.sock is not None
        request = text.encode("ascii")
        checksum = sum(request) & 255
        self.sock.sendall(b"$" + request + f"#{checksum:02x}".encode("ascii"))
        while True:
            marker = self._recv_exact(1)
            if marker == b"+":
                continue
            if marker == b"-":
                raise ProbeError("GDB server rejected packet checksum")
            if marker != b"$":
                continue
            response = bytearray()
            while True:
                nxt = self._recv_exact(1)
                if nxt == b"#":
                    break
                response.extend(nxt)
                if len(response) > 65536:
                    raise ProbeError("Oversized GDB packet")
            tail = self._recv_exact(2)
            if (sum(response) & 255) != int(tail, 16):
                self.sock.sendall(b"-")
                raise ProbeError("GDB reply checksum mismatch")
            self.sock.sendall(b"+")
            answer = response.decode("ascii")
            if answer.startswith("O") and len(answer) > 2 and len(answer) % 2 == 1:
                # Console output packet; WinUAE may emit those on attach.
                try:
                    bytes.fromhex(answer[1:])
                except ValueError:
                    pass
                else:
                    continue
            if answer.startswith("E") and len(answer) == 3:
                raise ProbeError(f"WinUAE GDB read failed: {answer}")
            return answer

    def registers(self) -> list[int]:
        packet = self.command("g")
        if len(packet) != 144:
            raise ProbeError(f"WinUAE returned {len(packet)} register hex digits, expected 144")
        return [int(packet[i:i + 8], 16) for i in range(0, 144, 8)]

    def read(self, address: int, count: int) -> bytes:
        if not 0 <= address <= 0xFFFFFFFF or not 1 <= count <= 512 or address + count > 0x100000000:
            raise ProbeError("Invalid address/length for read-only GDB memory request")
        packet = self.command(f"m{address:x},{count:x}")
        if len(packet) != count * 2:
            raise ProbeError(f"Truncated memory read at {address:#x}: {len(packet)//2}/{count}")
        return bytes.fromhex(packet)

    def ram_intervals(self) -> list[tuple[int, int]]:
        features = self.command("qSupported")
        if "qXfer:memory-map:read+" not in features:
            return []
        xml = ""
        while True:
            response = self.command(f"qXfer:memory-map:read::{len(xml):x},800")
            if not response or response[0] not in "ml":
                raise ProbeError("Unexpected GDB memory map response")
            xml += response[1:]
            if response[0] == "l":
                break
            if len(xml) > 200000:
                raise ProbeError("Oversized WinUAE memory map")
        try:
            root = ET.fromstring(xml)
            return [(int(m.attrib["start"], 0), int(m.attrib["start"], 0) + int(m.attrib["length"], 0))
                    for m in root.findall("memory") if m.get("type") == "ram"]
        except (ET.ParseError, ValueError, KeyError) as e:
            raise ProbeError(f"Invalid WinUAE memory map: {e}") from e


def u32(value: bytes) -> int:
    return struct.unpack(">I", value)[0]


def inspect_guest(guest: RSP, *, a5: int, chip_ram_bytes: int | None) -> dict:
    if a5 % 2 or not a5:
        raise ProbeError("A5 is not a valid, aligned AMOS base")
    state = u32(guest.read(a5 + 0x1C8, 4))
    if not state or state & 1:
        raise ProbeError("A5+$1C8 is null/unusable: stop inside an AGA call or while AMOS A5 is valid")
    info = guest.read(state, 36)
    width, height, colors = struct.unpack_from(">III", info, 12)
    dbstate = struct.unpack_from(">I", info, 32)[0]
    if (width, height, colors) != (320, 256, 256):
        raise ProbeError(f"Wrong active AGA screen: state reports {width}x{height}x{colors} colors")
    if not dbstate or dbstate & 1:
        raise ProbeError("Aga Double Buffer has not allocated a valid DBState")
    db = guest.read(dbstate, 24)
    sb0, sb1, front_index = struct.unpack_from(">III", db)
    if front_index not in (0, 1):
        raise ProbeError(f"Invalid current front buffer index {front_index}")
    result = {"mode": {"width": width, "height": height, "depth": 8}, "buffers": [],
              "observation": {"a5": f"0x{a5:08X}", "state": f"0x{state:08X}",
                              "dbstate": f"0x{dbstate:08X}", "front_index": front_index,
                              "source": "WinUAE GDB read-only paused guest"}}
    for index, sb in enumerate((sb0, sb1)):
        if not sb or sb & 1:
            raise ProbeError(f"Invalid ScreenBuffer SB{index} pointer {sb:#x}")
        sbdata = guest.read(sb, 8)
        bitmap = u32(sbdata[4:8])  # ScreenBuffer.sb_BitMap = +4, NOT +0
        if not bitmap or bitmap & 1:
            raise ProbeError(f"Invalid SB{index} BitMap pointer {bitmap:#x}")
        header = guest.read(bitmap, 40)
        bpr, rows, flags, dep = struct.unpack_from(">HHBB", header)
        planes = list(struct.unpack_from(">8I", header, 8))
        result["buffers"].append({
            "name": f"SB{index}", "screen_buffer": f"0x{sb:08X}",
            "bitmap": f"0x{bitmap:08X}", "bytes_per_row": bpr,
            "rows": rows, "depth": dep, "flags": flags,
            "planes": [f"0x{p:08X}" for p in planes],
            "type_of_mem_first": None, "type_of_mem_last": None,
        })
    if chip_ram_bytes is not None:
        # Chip RAM size comes EXPLICITLY from the user's WinUAE memory settings.
        # GDB memory-map can confirm mapped RAM but cannot prove MEMF_CHIP.
        if not 0x80000 <= chip_ram_bytes <= 0x800000 or chip_ram_bytes & (chip_ram_bytes - 1):
            raise ProbeError("chip_ram_bytes must be a plausible power-of-two Chip RAM size")
        mapped = guest.ram_intervals()
        if not any(start <= 0 and end >= chip_ram_bytes for start, end in mapped):
            # Fail closed: XML sometimes has split RAM regions. Never guess.
            raise ProbeError("GDB memory-map does not confirm RAM over configured CHIP range")
        result["chip_ranges"] = [{"start": "0x00000000", "end": f"0x{chip_ram_bytes:08X}",
                                   "basis": "Chip RAM size explicitly supplied from WinUAE settings, plus GDB RAM map"}]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=2345)
    parser.add_argument("--a5", type=lambda s: int(s, 0), help="AMOS A5 if the current CPU register is not reliable")
    parser.add_argument("--chip-ram-bytes", type=lambda s: int(s, 0),
                        help="exact configured Chip RAM size from WinUAE Memory tab (e.g. 0x200000)")
    parser.add_argument("--output", type=Path, default=Path("c2p_p2_winuae_observation.json"))
    args = parser.parse_args()
    try:
        with RSP(port=args.port) as guest:
            a5 = args.a5 if args.a5 is not None else guest.registers()[13]
            observation = inspect_guest(guest, a5=a5, chip_ram_bytes=args.chip_ram_bytes)
        verdict = check_document(observation)
        args.output.write_text(json.dumps(observation, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"output": str(args.output), "verdict": verdict}, indent=2))
        print("NOTE: WinUAE memory observation only. C2P conversion, Safe/Swap and Gate B are UNTESTED.")
        return 0 if verdict["direct_custom_bitmap_candidate"] else 1
    except (OSError, ValueError, ProbeError) as exc:
        print(f"C2P P2 GDB PROBE FAILED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
