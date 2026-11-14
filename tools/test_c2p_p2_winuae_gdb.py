#!/usr/bin/env python3
"""Host-only tests for read-only WinUAE GDB P2 snapshot (no real WinUAE)."""
import socket
import struct
import threading
import unittest

from c2p_p2_layout_check import check_document
from c2p_p2_winuae_gdb import ProbeError, RSP, inspect_guest


class MockGuest:
    def __init__(self, *, broken=False, chip_map=True, interleaved=False):
        self.regs = [0] * 18
        self.regs[13] = 0x8000
        self.segments = {}
        self.segments[0x81c8] = struct.pack('>I', 0x9000)
        state = bytearray(36)
        struct.pack_into('>III', state, 12, 320, 256, 256)
        struct.pack_into('>I', state, 32, 0xA000)
        if broken:
            struct.pack_into('>III', state, 12, 320, 256, 16)
        self.segments[0x9000] = bytes(state)
        self.segments[0xA000] = struct.pack('>III', 0xB000, 0xB100, 0) + bytes(12)
        for i, sb in enumerate((0xB000, 0xB100)):
            bitmap = 0xC000 + 0x100 * i
            self.segments[sb] = struct.pack('>II', 0, bitmap)
            header = bytearray(40)
            stride = 320 if interleaved else 40
            struct.pack_into('>HHBB', header, 0, stride, 256, 4 if interleaved else 0, 8)
            start = 0x20000 + i * 0x20000
            for j in range(8):
                struct.pack_into('>I', header, 8 + 4*j, start + j * (40 if interleaved else 10240))
            self.segments[bitmap] = bytes(header)
        self.chip_map = chip_map

    def read(self, address, count):
        b = self.segments.get(address)
        if b is None or len(b) < count:
            raise ProbeError(f'unmapped memory at {address:#x}')
        return b[:count]

    def ram_intervals(self):
        return [(0, 0x200000)] if self.chip_map else [(0x400000, 0x600000)]


class ProbeTests(unittest.TestCase):
    def test_capture_two_buffers_with_explicit_chip_size(self):
        guest = MockGuest()
        data = inspect_guest(guest, a5=guest.regs[13], chip_ram_bytes=0x200000)
        self.assertEqual(data['observation']['front_index'], 0)
        self.assertTrue(check_document(data)['direct_custom_bitmap_candidate'])
        self.assertEqual(data['buffers'][0]['planes'][1], '0x00022800')
        self.assertFalse(check_document(data)['runtime_qualified'])

    def test_missing_chip_proof_is_pending(self):
        data = inspect_guest(MockGuest(), a5=0x8000, chip_ram_bytes=None)
        report = check_document(data)
        self.assertFalse(report['direct_custom_bitmap_candidate'])
        self.assertFalse(report['buffers'][0]['memory_chip_verified'])

    def test_invalid_mode_fails_closed(self):
        with self.assertRaisesRegex(ProbeError, 'Wrong active AGA screen'):
            inspect_guest(MockGuest(broken=True), a5=0x8000, chip_ram_bytes=0x200000)

    def test_unmapped_chip_range_fails_closed(self):
        with self.assertRaisesRegex(ProbeError, 'GDB memory-map'):
            inspect_guest(MockGuest(chip_map=False), a5=0x8000, chip_ram_bytes=0x200000)

    def test_interleaved_is_not_passed(self):
        data = inspect_guest(MockGuest(interleaved=True), a5=0x8000, chip_ram_bytes=0x200000)
        self.assertFalse(check_document(data)['direct_custom_bitmap_candidate'])
        self.assertEqual(check_document(data)['buffers'][1]['layout'], 'interleaved')

    def test_rsp_readonly_wire(self):
        """Loopback fake WinUAE verifies register/memory protocol and detach."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 0))
        server.listen(1)
        port = server.getsockname()[1]
        observed = []

        def serve():
            try:
                connection, _ = server.accept()
                with connection:
                    connection.settimeout(4)
                    while True:
                        lead = connection.recv(1)
                        if lead in (b'+', b'-'):
                            continue
                        if not lead:
                            break
                        assert lead == b'$', lead
                        payload = bytearray()
                        while True:
                            nxt = connection.recv(1)
                            if nxt == b'#':
                                break
                            payload.extend(nxt)
                        checksum = connection.recv(2)
                        assert int(checksum, 16) == sum(payload) & 255
                        observed.append(payload.decode('ascii'))
                        connection.sendall(b'+')
                        name = payload.decode('ascii')
                        reply = {'?': 'S05', 'g': '00000000'*13 + '00008000' + '00000000'*4,
                                 'qSupported': 'PacketSize=10000;qXfer:memory-map:read+',
                                 'qXfer:memory-map:read::0,800': 'l<memory-map><memory type="ram" start="0" length="2097152"/></memory-map>',
                                 'm81c8,4': '00009000', 'D': 'OK'}[name]
                        answer = reply.encode('ascii')
                        connection.sendall(b'$' + answer + f'#{sum(answer)&255:02x}'.encode('ascii'))
                        if name == 'D':
                            break
            finally:
                server.close()

        thread = threading.Thread(target=serve)
        thread.start()
        with RSP(port=port) as client:
            self.assertEqual(client.registers()[13], 0x8000)
            self.assertEqual(client.read(0x81c8, 4), b'\x00\x00\x90\x00')
            self.assertEqual(client.ram_intervals(), [(0, 2097152)])
        thread.join(timeout=5)
        self.assertEqual(observed[-1], 'D')
        self.assertTrue(all(x[0] not in 'MPGZzc' for x in observed))

    def test_no_write_packets_allowed(self):
        rsp = RSP()
        for p in ('M100,2:ffee', 'P0=00000000', 'G00000', 'Z0,300,2', 'c', 'vCont;c', 'qRcmd,7868'):
            with self.assertRaises(ProbeError):
                rsp.command(p)


if __name__ == '__main__':
    unittest.main()
