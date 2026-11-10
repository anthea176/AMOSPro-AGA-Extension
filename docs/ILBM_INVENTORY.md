# Inventaire ILBM réel

Décodage de référence Python ; ne constitue pas un PASS AMOS/WinUAE.

| Fichier | Dimensions | Plans | CMAP | CAMG | Compression | Mode | BODY consommé | Statique |
|---|---|---:|---:|---|---|---|---:|---|
| examples/demo.iff | 320×256 | 8 | 256 | 00021000 | ByteRun1 | indexed LoRes | 40437 | PASS |
| iff-TEST/AGA_DEMO_320x256_256c.iff | 320×256 | 8 | 256 | 00021000 | ByteRun1 | indexed LoRes | 79940 | PASS |
| iff-TEST/AGA_TEST_MODES/AGA_TESTCARD_320x256_256C.iff | 320×256 | 8 | 256 | 00021000 | ByteRun1 | indexed LoRes | 40437 | PASS |
| iff-TEST/AGA_TEST_MODES/DBLNTSC_320x200.iff | 320×200 | 4 | 16 | 00091000 | ByteRun1 | indexed LoRes | 12604 | PASS |
| iff-TEST/AGA_TEST_MODES/DBLPAL_320x256.iff | 320×256 | 4 | 16 | 000a1000 | ByteRun1 | indexed LoRes | 16442 | PASS |
| iff-TEST/AGA_TEST_MODES/HAM6_PAL_320x256.iff | 320×256 | 6 | 16 | 00021800 | ByteRun1 | ham6 | 37440 | PASS |
| iff-TEST/AGA_TEST_MODES/HAM8_PAL_320x256.iff | 320×256 | 8 | 64 | 00021800 | ByteRun1 | ham8 | 55597 | PASS |
| iff-TEST/AGA_TEST_MODES/SHIRES_LACE_PAL_1280x512.iff | 1280×512 | 4 | 16 | 00029024 | ByteRun1 | hires/interlace | 46597 | PASS |
| iff-TEST/AGA_TEST_MODES/SHIRES_PAL_1280x256.iff | 1280×256 | 4 | 16 | 00029020 | ByteRun1 | hires | 23152 | PASS |
| iff-TEST/AGA_TESTCARD_320x256_256C.iff | 320×256 | 8 | 256 | 00021000 | ByteRun1 | indexed LoRes | 40437 | PASS |
| iff-TEST/beijita.iff | 697×900 | 1 | 2 | 00008004 | ByteRun1 | hires/interlace | 24235 | PASS |
| iff-TEST/Champoo_aga.iff | 640×512 | 6 | 64 | 00029004 | ByteRun1 | hires/interlace | 80622 | PASS |
| iff-TEST/city_hunter_aga.iff | 640×400 | 5 | 32 | 00029000 | ByteRun1 | hires | 52513 | PASS |
| iff-TEST/Etoile.iff | 640×200 | 4 | 16 | 00029000 | ByteRun1 | hires | 18477 | PASS |
| iff-TEST/gohan.iff | 462×902 | 1 | 2 | 00008004 | ByteRun1 | hires/interlace | 16581 | PASS |
| iff-TEST/Infermiere.iff | 640×686 | 5 | 32 | 00029004 | ByteRun1 | hires/interlace | 84794 | PASS |
| iff-TEST/Kyoko.iff | 640×256 | 4 | 16 | 00029000 | ByteRun1 | hires | 23778 | PASS |
| iff-TEST/lunch.iff | 640×340 | 4 | 16 | 00029000 | ByteRun1 | hires | 39539 | PASS |
| iff-TEST/miho.iff | 640×256 | 4 | 16 | 00029000 | ByteRun1 | hires | 16771 | PASS |
| iff-TEST/modoka.iff | 545×956 | 1 | 2 | 00008004 | ByteRun1 | hires/interlace | 23462 | PASS |
| iff-TEST/modoka2.iff | 675×1272 | 1 | 2 | 00008004 | ByteRun1 | hires/interlace | 28511 | PASS |
| iff-TEST/ranma-chan&san.iff | 640×400 | 4 | 16 | 00029000 | ByteRun1 | hires | 47851 | PASS |
| iff-TEST/ranma_&_genma.iff | 704×512 | 4 | 16 | 00029000 | ByteRun1 | hires | 55719 | PASS |
| iff-TEST/shina.iff | 640×256 | 4 | 16 | 00029000 | ByteRun1 | hires | 20334 | PASS |
| iff-TEST/shunsuke.iff | 640×256 | 4 | 16 | 00029000 | ByteRun1 | hires | 28528 | PASS |
| iff-TEST/soyokaze.iff | 384×512 | 6 | 32 | 00004084 | ByteRun1 | ehb/interlace | 51262 | PASS |
| iff-TEST/Urusei_yatsura.iff | 640×450 | 4 | 16 | 00029000 | ByteRun1 | hires | 77630 | PASS |
| iff-TEST/valis decors.iff | 320×256 | 4 | 16 | 00004000 | ByteRun1 | indexed LoRes | 27135 | PASS |
| iff-TEST/valis.iff | 320×290 | 6 | 64 | 00021080 | ByteRun1 | ehb | 14236 | PASS |
| iff-TEST/WBgunnm.iff | 318×255 | 8 | 256 | 00029000 | ByteRun1 | hires | 18386 | PASS |

Le JSON associé contient chaque BMHD, palette RGB complète, chunk, padding, taille et SHA256 par plan.
Les octets suivant FORM sont signalés, jamais interprétés comme des chunks de cette image.
