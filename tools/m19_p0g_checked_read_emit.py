#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0g: checked-read private BOBS relay for future persistent Draw.

Source-only, no new public AP20 token, installation, Chip operation or Swap.
Preserve P0f public Set/Off and P0e raw read byte-for-byte; append a distinct
private checked read which uses the existing P0f AGA-side identity_check.
This must not be presented as an implemented public Aga Bob Draw.

Input D0=object ID 1..64, A1=caller-owned 24-byte descriptor, A5=owner.
Output D3=1 only when the object is active AND its recorded AMOS bank
identity is still valid; D2=0. On rejection output bytes are untouched.
D0/D1/D4-D7/A0-A6 including A3/A5 and SP are preserved as in relay_common.
"""
from __future__ import annotations

from hashlib import sha256

from m68k_emit import Code, D, I
from m19_p0e_split_bridge_emit import AGA_CORE
from m19_p0f_object_identity_emit import emit_object_identity
from build_m19_p0f_public_bound_in_memory import emit_bound_public


NATIVE_CHECKED_READ_SHA = 'a30d4a4bc9c2ea1e50aa9a69fe62df6f684f58d1ffa0737559cd891becdc8f87'
NATIVE_CHECKED_READ_BYTES = 16444


def checked_read_offset() -> int:
    native, labels = emit_object_identity()
    offset = len(AGA_CORE) + labels['identity_check_entry']
    if not 0 <= offset < 65534 or offset & 1:
        raise ValueError('Invalid AGA-side checked-read offset')
    if native[labels['identity_check_entry']:][:4] != bytes.fromhex('48e7efee'):
        raise ValueError('Missing identity_check MC68020 entry prologue')
    return offset


def emit_checked_read() -> tuple[bytes, dict[str, int]]:
    original, original_labels = emit_bound_public()
    c = Code()
    c.raw(original.hex())
    c.labels.update(original_labels)
    c.label('relay_checked_read_entry')
    c.raw('48e7efee')                      # same MOVEM ABI as relay_read
    c.move(I(checked_read_offset()), D(7))  # target AGA identity_check
    c.branch(0, 'relay_common')           # BRA.W via verified shared relay
    native = c.out()
    if not native.startswith(original) or len(native) & 1 or len(native) >= 32766:
        raise ValueError('BOBS private suffix overflow or historical prefix drift')
    if c.labels['relay_checked_read_entry'] != len(original):
        raise ValueError('Checked-read is not a strictly appended private entry')
    if not native[len(original):].startswith(bytes.fromhex('48e7efee')):
        raise ValueError('Checked-read entry ABI damaged')
    if len(native) != NATIVE_CHECKED_READ_BYTES or sha256(native).hexdigest() != NATIVE_CHECKED_READ_SHA:
        raise ValueError('P0g checked-read native byte-exact source drift')
    return native, c.labels


if __name__ == '__main__':
    from hashlib import sha256
    raw, labels = emit_checked_read()
    print('M19 P0g PRIVATE CHECKED READ 020 SOURCE ONLY',
          len(raw), sha256(raw).hexdigest(),
          'checked entry', labels['relay_checked_read_entry'],
          'AGA offset', checked_read_offset(),
          'NO public Draw / no active .Lib')
