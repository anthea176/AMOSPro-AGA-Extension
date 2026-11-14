# P4 — R82 réelle séparée en deux unités AP20 natives

Branche **\`experiment/ap20-v3-multiunit-64k\`** uniquement.
Aucun changement de \`main\`, \`dist/\`, \`tests/current/\`, ou \`LAST_GOOD\`.

## Hypothèse testée

La V3 FIX01 démontrait deux unités avec une deuxième unité constituée
d'un faux handler isolé. P4 répartit cette fois le **vrai code R82** :

- **Unité 80 — C2P** : entrées natives 70–75, 7 998 octets originaux,
  réparties dans un groupe de 8 032 octets + 12 000 octets de NOP
  non exécutables, uniquement pour dépasser la taille native agrégée 64 Kio ;
  taille du groupe : **20 032 octets**.
- **Unité 81 — AGA + AGAPIC/palettes** : entrées 0–69, 76–79,
  49 828 + 3 112 octets natifs + un dispatcher de 34 octets :
  **52 974 octets**.
- **Total des unités** : **73 006 octets**, contre 65 534 octets
  maximum par **unité** pour le Compiler V2.
- **API R82** : ses 74 noms de commandes, signatures, numéros de fonction
  et conventions GetP sont conservés. Aucun ajout public V3.

Le groupe C2P précède physiquement AGA dans le HUNK AP20. Un audit de
tous les stubs RBSR vérifie leur déplacement **BSR.W en tant que véritable
chargeur AMOS365** et rejette le layout provoquant une ILLEGAL.

## Références croisées connues

Conserver le **premier bloc natif R82 0–69 en ordre original** :
les 6 branches natives connues du moteur AGA restent exactement en
place (3 manifestes historiques et 3 hooks fermeture/init). Le bloc
d'état clavier/souris, ses 144 octets, et les 7 LEA restent aussi à leurs
adresses de départ.

Le bloc palettes R82 76–79 passe juste derrière 0–69.
Quatre BSR.L MC68020 vers les handlers legacy 41–44 sont les **seuls
octets natifs réécrits** : offsets d'instruction 90, 90, 146 et 174.
Le constructeur prouve que les liens anciens visaient les entrées
attendues et que les quatre nouveaux liens aboutissent sur les bonnes
entrées.

Le C2P continue d'utiliser State/DBState via A5, mais aucun lien natif
direct entre C2P et AGA n'est présumé : un audit de désassemblage
exhaustif et les tests fonctionnels WinUAE doivent encore le confirmer.

## Validation

Les tests CPU MC68020 de P4 exécutent les **vrais stubs RBSR patchés en
BSR.W et les vrais deux dispatchers V2**, jusqu'au premier octet de
16 handlers R82 (Core, C2P, palettes). Ils arrêtent la simulation avant
le corps du handler : le code de fonction R82 lui-même **n'est pas encore
réexécuté par le test CPU**, seulement protégé octet à octet.

La CI produit une bibliothèque **expérimentale**, pas une R83 promue,
et un journal des contrôles. Les Gates B WinUAE Runtime et C AMOS
Compiler des fonctions C2P et AGA réelles sont à faire avec les bancs
R82 et R81/C2P. Le mode interprété pur et le matériel physique
restent des validations distinctes.

L'objectif est une séparation stable pour accueillir les futurs
modules M2/M3/M4. Cette P4 **ne démontre pas encore** la possibilité
de trois unités ou plus sans un contrat inter-modules supplémentaire.


## P4 -- WinUAE author logs: smoke Gate B / C PASS (2026-11-14)

The author executed **exactly the P4 true-split smoke program** on the
experimental `AMOSPro_AGA_V3_R82_SPLIT_TEST.Lib` (not the synthetic P3 probe).
Two authentic AMOS output logs are retained:

- [Runtime Gate B evidence](evidence/AP20_V3_R82_SPLIT_P4_RUNTIME_2026-11-14.TXT):
  `RUN_MODE RUNTIME`, `PRG_STATE 1`, `RESULT 1`,
  `VERDICT PASS`, `R82_DETECT -1`, `ERR 0`.
- [Compiled Gate C evidence](evidence/AP20_V3_R82_SPLIT_P4_COMPILED_2026-11-14.TXT):
  `RUN_MODE COMPILED`, `PRG_STATE -1`, `RESULT 1`,
  `VERDICT PASS`, `R82_DETECT -1`, `ERR 0`.

Both logs also report `C2P_OPEN_REJECT 0`, `C2P_CLOSE_REJECT 0`,
`IFF_REJECT 0`, and exactly **zero net Chip/Fast memory delta**.
The test calls native handlers in the two real AP20 units and verifies
expected rejection behavior with **invalid** C2P inputs.

**Scope restriction:** These are **smoke Gate B/C PASS only**, not full R82
graphic regression qualification. No successful C2P open/convert/zoom,
AGAPIC image draw/palette operations, actual image decoding, or physical
Amiga test is demonstrated. Those remain **NOT TESTED on P4**; the tests
listed in `experimental/AP20_V3_R82/P4_WINUAE_TEST.md` must run before
any proposed promotion.

SHA256 of original CRLF evidence:
- Runtime `95667d79166cbd8394b7b0c198949b70b9a7bba3ed6a634762183a2d0f19c470`
- Compiled `f7c3da8583b0434f84cec2dcc17a348b0bf6c241b05f8f7fde3b425f6734ae2d`

No change to `main`, `dist/`, `tests/current/`, or R82 LAST_GOOD.

## P4 -- R82/AGAPIC and C2P positive functional Runtime evidence (2026-11-14)

The author supplied two additional WinUAE **Runtime** logs while testing
P4's real C2P/AGA two-unit experimental library. Neither log records the
installed .Lib's checksum: association with P4 is based on test context,
not an in-guest hash verification. Historical test headers still say
R79 and R82 because the ASCII fixtures were not changed.

- [R82 AGAPIC Runtime evidence](evidence/AP20_V3_R82_SPLIT_P4_AGAPIC_RUNTIME_2026-11-14.TXT):
  `RUN_MODE RUNTIME`, `PRG_STATE 1`, CPU reported 68030,
  `RESULT 1`, `ERR 0`,  all AGAPIC v1/v2, AGAPAL, palettes,
  fades, capture, drawing, regions, invalid input and swap flags equal 1,
  `CLOSE_RETURNED 1`; Chip and Fast free exactly unchanged.
  **Positive AGAPIC functional Runtime PASS on the reported P4 setup.**
- [C2P IFF showcase Runtime evidence](evidence/AP20_V3_R82_SPLIT_P4_C2P_SHOWCASE_RUNTIME_2026-11-14.TXT):
  `RUN_MODE RUNTIME`, `PRG_STATE 1`, `RESULT 1`, `ERR 0`, 
  all IFF loading, palette, raw bank, C2P base, Blit, Zoom, invalid calls,
  re-open and Escape flags equal 1; `PIXEL_CHECK_COUNT 14`, normal close.
  Chip free unchanged. **Fast free decreased by 17,024 bytes**
  (138,189,072 -> 138,172,048; `FAST_DELTA 17024`).
  **C2P functional Runtime PASS, memory-cleanup status UNRESOLVED.**

The C2P reference showcase previously achieved **zero** Fast RAM delta on
R79 (see `docs/C2P_INTEGRATED_IFF_REFERENCE_2026-11-14.md`).
This new +17,024-byte consumed-memory delta is a real observation, not
proof of an extension leak: AMOS/OS lazy resource allocation or other
persistent state is also possible. Need clean warm-up then two successive
runs in the same WinUAE instance, preferably compare to R82 LAST_GOOD
in another isolated setup; if the 17,024-byte loss accumulates, investigate
C2P Close/Screen Close and system library ownership. The test measures Fast
Free after `Fsel$` / Pic Info but before C2P and screens, and measures
again after Screen Close, `Erase 13`, `Erase 12` and `Amos To Front`.

**P4 qualification is NOT complete:** AGAPIC/C2P fresh compiled functional
runs are pending, and the C2P Fast RAM anomaly must be understood. The
showcase does not exercise the `Aga Iff To Chunky` R80 decoder. The user
has not supplied an interpreter-only `PRG_STATE 0` test or physical Amiga
result. Do not merge/promote to main or change LAST_GOOD.

Original uploaded-file SHA256:
- AGAPIC Runtime `17bbb53bb0cd78a404ce6725a31c816be20df8261c57cab3710438aff2f38b13`
- C2P Runtime `24ef7575a6d8037bb23a46fb00cfad41c919f67e97bbf21536399a6b286ceb26`
