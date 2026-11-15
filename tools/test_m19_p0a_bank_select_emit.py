#!/usr/bin/env python3
"""M19 P0a bank-select native preflight (STATIC, not CPU Gate A)."""
import unittest
from hashlib import sha256
from struct import pack

from m19_p0a_bank_select_emit import (
    emit_bank_select, MARKER, FRAME, STATE_SIZE,
)
from m19_p0a_amos_bank_transaction_emit import IDX, MARKERS
from m19_p0a_multi_bob_abk import empty_bank


class BankSelectEmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw,cls.labels=emit_bank_select()

    def test_deterministic_bytes(self):
        self.assertEqual((self.raw,self.labels),emit_bank_select())
        self.assertEqual(len(self.raw),1336)
        self.assertEqual(sha256(self.raw).hexdigest(),
            '7f2658c8f53a0b21502fd4505212015b8619b76fd0ef56fbcd2292ac5962554b')

    def test_abi_and_embedded_transaction(self):
        self.assertEqual(self.raw[:8],bytes.fromhex('48e7efee4fefffc0'))
        self.assertEqual(FRAME,64)
        self.assertEqual(self.raw.count(MARKER),4)
        self.assertEqual(self.raw.count(MARKERS['Lst.Cree']),1)
        self.assertEqual(self.raw.count(MARKERS['Lst.Del']),2)
        self.assertEqual(self.raw.count(MARKERS['Bnk.Change']),1)
        self.assertNotIn(bytes.fromhex('fe11f700')+pack('>H',816),self.raw)

    def test_private_pc_relative_state_and_canonical_empty(self):
        state=self.labels['active_state']
        payload=self.labels['canonical_empty']
        self.assertEqual(payload-state,STATE_SIZE)
        self.assertEqual(self.raw[state:payload],bytes(STATE_SIZE))
        self.assertEqual(self.raw[payload:],empty_bank())
        self.assertLess(self.labels['done'],self.labels['commit'])
        self.assertLess(self.labels['commit'],state)
        self.assertEqual(self.labels['bank_select'],0)

    def test_non_destructive_selection_guards(self):
        for k in ('bank_select','existing','flags_ok','done','commit',
                  'active_state','canonical_empty'):
            self.assertIn(k,self.labels)
            self.assertEqual(self.labels[k]%2,0)
        self.assertLess(self.labels['existing'],self.labels['done'])
        self.assertIn(pack('>I',0x4147424f),self.raw)
        self.assertIn(pack('>I',0x41474142),self.raw)
        self.assertIn(pack('>I',0x4f425320),self.raw)
        self.assertEqual(IDX['Bnk.GetAdr'],797)


if __name__=='__main__':
    unittest.main(verbosity=2)
