"""Host routing and pixel oracle; no real AGA, DMA, or CPU timing."""
import hashlib
import unittest
from pathlib import Path
from unittest.mock import patch

import test_agtm_db_dirty_model as base

SHA256 = '1bdffdc5faf4f60808f36711a94a233e4df10ae217f404469a49d7659fd90c4a'


def run_backend(backend):
    world = base.make_map()
    pages = [base.full(world, base.CAM[0], [0]*4) for _ in range(2)]
    cameras, revisions = [base.CAM[0]]*2, [0, 0]
    counts = [0]*4
    routes = [0, 0]

    def region(out, world, camera, bounds, counts):
        l, r, t, b = bounds
        cx, cy = camera
        assert 0 <= l <= r < 64 and 0 <= t <= b < 32
        for ty in range(t, b+1):
            for tx in range(l, r+1):
                cell = ty*64+tx
                x0, y0 = tx*16-cx, ty*16-cy
                lo, hi = max(0, x0), min(320, x0+16)
                assert lo < hi
                for mode, tile_id in enumerate((world[0][cell], world[1][cell])):
                    if mode and not tile_id:
                        continue
                    counts[mode] += 1
                    use_blit = backend == 1 or (backend == 2 and mode == 0
                        and 0 <= x0 <= 304 and 0 <= y0 <= 240)
                    routes[int(use_blit)] += 1
                    tile = base.TILES[tile_id]
                    for y in range(max(0, y0), min(256, y0+16)):
                        q = (y-y0)*16+lo-x0
                        pos = y*320+lo
                        if use_blit:
                            pixels = tile[q:q+hi-lo]
                            if mode:
                                pixels = bytes(p or old for p, old in
                                    zip(pixels, out[pos:pos+hi-lo]))
                            out[pos:pos+hi-lo] = pixels
                        else:
                            for x in range(hi-lo):
                                pen = tile[q+x]
                                if not mode or pen:
                                    out[pos+x] = pen

    back = 0
    with patch.object(base, 'region', region):
        for frame in range(1, 13):
            base.edit(world, frame)
            front = bytes(pages[1-back])
            base.dirty(pages[back], world, cameras[back], base.CAM[frame],
                       revisions[back], frame, counts)
            assert pages[back] == base.oracle(world, base.CAM[frame]), (backend, frame)
            assert pages[1-back] == front
            cameras[back], revisions[back] = base.CAM[frame], frame
            back = 1-back
    assert revisions == [11, 12]
    return counts, routes


class BackendTests(unittest.TestCase):
    def test_source_identity(self):
        source = Path(__file__).with_name('AGTM_BACKEND_BENCH.asc').read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SHA256)

    def test_same_pixels_and_calls_for_all_backends(self):
        for backend in range(3):
            with self.subTest(backend=backend):
                counts, routes = run_backend(backend)
                print('METHOD', backend, 'COUNTS', counts, 'CPU/BLIT', routes)
                self.assertEqual(counts, [480, 127, 11, 21])
                self.assertEqual(sum(routes), 607)
                if backend == 0:
                    self.assertEqual(routes, [607, 0])
                elif backend == 1:
                    self.assertEqual(routes, [0, 607])
                else:
                    self.assertEqual(routes, [389, 218])

    def test_protocol_totals(self):
        order = [r if r < 3 else r-3 if r < 6 else 8-r for r in range(9)]
        self.assertEqual(order, [0, 1, 2, 0, 1, 2, 2, 1, 0])
        self.assertEqual((3*12*81920, 3*12*6, 9*(12+2)), (2949120,216,126))


if __name__ == '__main__':
    unittest.main(verbosity=2)
