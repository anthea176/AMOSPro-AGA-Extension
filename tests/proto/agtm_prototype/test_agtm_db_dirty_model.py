"""Host-only oracle for AGTM_DB_DIRTY_BENCH.asc; not a chipset emulator."""
import hashlib
import unittest
from pathlib import Path

W, H, T = 320, 256, 16
CAM = ((32,32),(33,32),(34,32),(34,40),(34,48),(42,56),(50,64),
       (34,48),(18,32),(18,32),(18,32),(19,31),(20,30))
EDITS = [None] + [(6+i%4,6+i%3) for i in range(1,13)]
EDITS[7] = (50,25)
SHA256 = '5a2749c931cb3317a39de478b4c0d1bb0dcbf19d1a30414cc3ecd632fbcee80e'


def pen(i,x,y):
    if x == y:
        return 255
    if x == 0 or y == 0:
        return 0
    return ((i+1)*29+x*7+y*13)%256


TILES = tuple(bytes(pen(i,x,y) for y in range(16) for x in range(16))
              for i in range(16))


def make_map():
    ground = bytearray((x*3+y*5+x//3+y//5)%16
                       for y in range(32) for x in range(64))
    top = bytearray(1+(x+y)%15 if (x+2*y)%4 == 0 else 0
                    for y in range(32) for x in range(64))
    return ground, top


def edit(world,frame):
    x,y = EDITS[frame]
    a = y*64+x
    if frame%2:
        world[0][a] = (world[0][a]+5)%16
    else:
        world[1][a] = 0 if world[1][a] else 1+frame%15


def oracle(world,camera):
    cx,cy = camera
    out = bytearray(W*H)
    for y in range(H):
        wy = cy+y
        for x in range(W):
            wx = cx+x
            a = wy//16*64+wx//16
            q = wy%16*16+wx%16
            base,top = world[0][a],world[1][a]
            out[y*W+x] = (TILES[top][q] if top else 0) or TILES[base][q]
    return out


def visible(c):
    x,y = c
    return x//16,(x+319)//16,y//16,(y+255)//16


def region(out,world,camera,bounds,counts):
    l,r,t,b = bounds
    assert 0 <= l <= r <64 and 0 <= t <= b <32
    cx,cy = camera
    for ty in range(t,b+1):
        for tx in range(l,r+1):
            a = ty*64+tx
            base,top = world[0][a],world[1][a]
            counts[0] += 1
            counts[1] += bool(top)
            x0,y0 = tx*16-cx,ty*16-cy
            lo,hi = max(0,x0),min(W,x0+16)
            assert lo < hi
            for y in range(max(0,y0),min(H,y0+16)):
                for x in range(lo,hi):
                    q = (y-y0)*16+x-x0
                    out[y*W+x] = (TILES[top][q] if top else 0) or TILES[base][q]


def full(world,camera,counts):
    out = bytearray(W*H)
    region(out,world,camera,visible(camera),counts)
    return out


def dirty(out,world,old,camera,rev,frame,counts):
    ox,oy = old
    cx,cy = camera
    dx,dy = cx-ox,cy-oy
    if dx or dy:
        snapshot = bytes(out)
        for y in range(max(0,-dy),min(H,H-dy)):
            l,r = max(0,-dx),min(W,W-dx)
            out[y*W+l:y*W+r] = snapshot[(y+dy)*W+l+dx:(y+dy)*W+r+dx]
        counts[2] += 1
    l,r,t,b = visible(camera)
    if dx:
        cols = ((ox+W)//16,r) if dx>0 else (l,(ox-1)//16)
        region(out,world,camera,(*cols,t,b),counts)
    if dy:
        rows = ((oy+H)//16,b) if dy>0 else (t,(oy-1)//16)
        region(out,world,camera,(l,r,*rows),counts)
    for e in range(rev+1,frame+1):
        x,y = EDITS[e]
        if l<=x<=r and t<=y<=b:
            region(out,world,camera,(x,x,y,y),counts)
            counts[3] += 1


def scenario(incremental):
    world = make_map()
    pages = [full(world,CAM[0],[0]*4) for _ in range(2)]
    cameras,rev = [CAM[0]]*2,[0,0]
    counts = [0]*4
    back = 0
    for frame in range(1,13):
        edit(world,frame)
        old_front = bytes(pages[1-back])
        if incremental:
            dirty(pages[back],world,cameras[back],CAM[frame],rev[back],frame,counts)
        else:
            pages[back] = full(world,CAM[frame],counts)
        assert pages[back] == oracle(world,CAM[frame]), (frame,back)
        assert pages[1-back] == old_front
        cameras[back],rev[back] = CAM[frame],frame
        back = 1-back
    assert rev == [11,12]
    return counts


class TestScene(unittest.TestCase):
    def test_exact_source(self):
        src = Path(__file__).with_name('AGTM_DB_DIRTY_BENCH.asc').read_bytes()
        self.assertEqual(hashlib.sha256(src).hexdigest(),SHA256)

    def test_two_pages_and_counts(self):
        a,b = scenario(False),scenario(True)
        print('FULL counts:',a,'SCROLL counts:',b)
        self.assertEqual(a[2:], [0,0])
        self.assertEqual(b[2:], [11,21])
        self.assertLess(b[0],a[0])

    def test_overlay_edits_and_stationary_frame(self):
        world = make_map()
        removals=insertions=0
        for frame in range(1,13):
            x,y=EDITS[frame]
            before=world[1][y*64+x]
            edit(world,frame)
            after=world[1][y*64+x]
            if frame%2==0:
                removals += bool(before and not after)
                insertions += bool(after and not before)
        self.assertEqual((removals,insertions),(3,3))
        self.assertEqual(CAM[8],CAM[10])


if __name__ == '__main__':
    unittest.main(verbosity=2)
