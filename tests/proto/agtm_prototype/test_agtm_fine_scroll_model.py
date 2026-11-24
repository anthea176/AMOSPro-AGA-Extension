"""Host geometry/planar oracle for AGTM_FINE_SCROLL_BENCH.asc, not an AGA emulator."""
import hashlib
import unittest
from pathlib import Path

W, H, T = 320, 256, 16
STEPS = 4
CASES = ((1, 14), (8, 0), (16, 0))
SAMPLE_X = (0, 1, 7, 8, 15, 16, 159, 303, 304, 311, 318, 319)
SAMPLE_Y = (0, 1, 15, 16, 127, 254, 255)
ASC_SHA256 = 'a2d2de907f69e70a1dc86d0e7550dc5312d65a8a5ba6d6e648458be7ce70c3d6'


def tile_pen(tile, x, y):
    if x == y:
        return 255
    if x == 0 or y == 0:
        return 0
    return ((tile + 1) * 29 + x * 7 + y * 13) % 256


TILES = tuple(bytes(tile_pen(tile, x, y) for y in range(T) for x in range(T))
              for tile in range(16))
MAP = tuple(tuple((x * 3 + y * 5 + x // 3 + y // 5) % 16
                  for x in range(64)) for y in range(16))


def reference(camera):
    """World-coordinate oracle, independent of tile clipping and copy ranges."""
    return bytes(TILES[MAP[y // T][(camera + x) // T]]
                 [(y % T) * T + (camera + x) % T]
                 for y in range(H) for x in range(W))


def draw_cols(frame, camera, first, last):
    assert 0 <= first <= last < 64
    count = 0
    for row in range(16):
        for col in range(first, last + 1):
            dx = col * T - camera
            lo, hi = max(0, dx), min(W, dx + T)
            assert lo < hi
            tile = TILES[MAP[row][col]]
            for ty in range(T):
                dst = (row * T + ty) * W
                src = ty * T
                frame[dst + lo:dst + hi] = tile[src + lo - dx:src + hi - dx]
            count += 1
    return count


def full(camera):
    frame = bytearray(W * H)
    count = draw_cols(frame, camera, camera // T, (camera + W - 1) // T)
    return frame, count


def scroll(frame, old, camera):
    delta = abs(camera - old)
    assert 0 < delta <= T
    for y in range(H):
        off = y * W
        # Python slices are a snapshot, modelling the overlap-safe contract,
        # not testing whether real graphics.library honours that contract.
        if camera > old:
            frame[off:off + W - delta] = frame[off + delta:off + W]
        else:
            frame[off + delta:off + W] = frame[off:off + W - delta]
    if camera > old:
        first, last = (old + W) // T, (camera + W - 1) // T
    else:
        first, last = camera // T, (old - 1) // T
    return draw_cols(frame, camera, first, last)


def pack_planes(frame):
    stride = W // 8
    plane_bytes = stride * H
    out = bytearray(plane_bytes * 8)
    for i, pen in enumerate(frame):
        offset = i // 8
        mask = 128 >> (i % 8)
        for plane in range(8):
            if pen & (1 << plane):
                out[plane * plane_bytes + offset] |= mask
    return out


def read_pixel(planar, x, y):
    offset = y * 40 + x // 8
    mask = 128 >> (x % 8)
    return sum(1 << p for p in range(8) if planar[p * 10240 + offset] & mask)


class FineScrollTests(unittest.TestCase):
    def test_exact_source(self):
        source = Path(__file__).with_name('AGTM_FINE_SCROLL_BENCH.asc').read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), ASC_SHA256)

    def test_continuous_24_transitions_and_call_counts(self):
        expected_full_calls = {1: 2656, 8: 2624, 16: 2560}
        for step, base in CASES:
            with self.subTest(step=step):
                frame, _ = full(base)
                camera = base
                full_calls = scroll_calls = blits = 0
                for sign in (1, -1):
                    for _ in range(STEPS):
                        old = camera
                        camera += sign * step
                        scroll_calls += scroll(frame, old, camera)
                        fresh, calls = full(camera)
                        full_calls += calls
                        blits += 1
                        self.assertEqual(frame, fresh)
                        self.assertEqual(frame, reference(camera))
                self.assertEqual(camera, base)
                self.assertEqual(full_calls, expected_full_calls[step])
                self.assertEqual(scroll_calls, 128)
                self.assertEqual(blits, 8)

    def test_planar_samples_and_exact_compare_count(self):
        checks = samples = total_bytes = 0
        for step, base in CASES:
            camera = base
            frame, _ = full(camera)
            for sign in (1, -1):
                for _ in range(2):
                    old = camera
                    camera += sign * step
                    scroll(frame, old, camera)
                    expected = reference(camera)
                    planar = pack_planes(frame)
                    self.assertEqual(len(planar), 81920)
                    self.assertEqual(planar, pack_planes(expected))
                    for y in SAMPLE_Y:
                        for x in SAMPLE_X:
                            self.assertEqual(read_pixel(planar, x, y), expected[y * W + x])
                            samples += 1
                    checks += 1
                    total_bytes += len(planar)
        self.assertEqual((checks, total_bytes, samples), (12, 983040, 1008))


if __name__ == '__main__':
    unittest.main(verbosity=2)
