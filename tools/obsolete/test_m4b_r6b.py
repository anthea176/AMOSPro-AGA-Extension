import hashlib, struct, unittest
from audit_ap20 import inspect, parse
from build_m4b_r6b import BASE, DEST, R6B_SHA, build

class TestR6B(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=build()
        cls.lib=parse(cls.raw)
        cls.base=parse(BASE.read_bytes())

    def seg(self,i,lib=None):
        lib=lib or self.lib
        s=lib.starts[i]
        return lib.code[s:s+2*lib.jumps[i]]

    def test_hash_size_and_ap20(self):
        self.assertEqual(len(self.raw),2372)
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),R6B_SHA)
        self.assertEqual(inspect(self.lib)['issues'],[])

    def test_committed_binary_matches_builder(self):
        self.assertTrue(DEST.exists())
        self.assertEqual(DEST.read_bytes(),self.raw)

    def test_open_unchanged(self):
        self.assertEqual(self.seg(6),self.seg(6,self.base))

    def test_shared_state_36(self):
        cold=self.seg(0)
        start=len(cold)-36
        self.assertEqual(cold[-36:],b'\0'*36)
        for field in (12,32):
            self.assertEqual(field+struct.unpack_from('>h',cold,field)[0],start)

    def test_dbstate_24_and_two_ports(self):
        db=self.seg(10)
        self.assertIn(bytes.fromhex('7018223c00010001'),db)
        self.assertEqual(db.count(bytes.fromhex('4eaefd66')),2)
        self.assertIn(bytes.fromhex('2940000c'),db)
        self.assertIn(bytes.fromhex('29400010'),db)

    def test_reply_ports_both_buffers(self):
        db=self.seg(10)
        self.assertEqual(db.count(bytes.fromhex('21400016')),2)
        self.assertEqual(db.count(bytes.fromhex('21400036')),2)
        publish=db.index(bytes.fromhex('254c0020'))
        self.assertLess(db.rindex(bytes.fromhex('21400036')),publish)

    def test_swap_one_change_no_replymsg(self):
        sw=self.seg(11)
        self.assertEqual(sw.count(bytes.fromhex('4eaefcf4')),1)
        self.assertNotIn(bytes.fromhex('4eaefe86'),sw)
        self.assertEqual(sw.count(bytes.fromhex('4eaefe80')),2)
        self.assertEqual(sw.count(bytes.fromhex('4eaefe8c')),2)

    def test_waitblit_before_change_and_index_after(self):
        sw=self.seg(11)
        wb=sw.index(bytes.fromhex('4eaeff1c'))
        ch=sw.index(bytes.fromhex('4eaefcf4'))
        ix=sw.index(bytes.fromhex('29470008'))
        self.assertLess(wb,ch)
        self.assertLess(ch,ix)

    def test_a3_preserved_result_d3(self):
        for i in (8,10,11):
            s=self.seg(i)
            self.assertEqual(s[:4],bytes.fromhex('48e7fffe') if i==8 else bytes.fromhex('48e7effe'))
            self.assertIn(bytes.fromhex('4cdf7fff4e75') if i==8 else bytes.fromhex('4cdf7ff774004e75'),s)

    def test_cleanup_two_ports_after_screenbuffers(self):
        cl=self.seg(8)
        self.assertEqual(cl.count(bytes.fromhex('4eaefd60')),2)
        self.assertLess(cl.rindex(bytes.fromhex('4eaefcfa')),cl.index(bytes.fromhex('4eaefd60')))

    def test_backfill_stays_stub(self):
        self.assertEqual(self.seg(12),bytes.fromhex('4e75'))

if __name__=='__main__':
    unittest.main(verbosity=2)
