# M19 P2.8 — R88 candidate active, non promue (15 novembre 2026)

## Emplacement officiel des bibliothèques

| Rôle | Chemin | Taille | SHA256 |
|---|---|---:|---|
| **Candidate actuelle R88 v0.13.33** | `dist/AMOSPro_AGA.Lib` | **75 040** | `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc` |
| Archive précédente R87 v0.13.32, tests P2.5–P2.7 | `dist/experimental/AMOSPro_AGA_R87_v0.13.32_M19_P25_BC_PASS.Lib` | 73 184 | `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302` |
| Archive supplémentaire exacte R88 Gate A | `dist/experimental/AMOSPro_AGA_R88_v0.13.33_M19_P28_GATE_A_ONLY.Lib` | 75 040 | `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc` |
| **R84 v0.13.29 LAST_GOOD protégée** | `dist/AMOSPro_AGA_LAST_GOOD.Lib` | **67 904** | `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d` |

**R88 est le binaire de travail actif et non une promotion LAST_GOOD.** Aucune modification d'octets dans R88 par rapport à la candidate qui a passé Gate A. L'ancien texte `UNINSTALLED GATE A ONLY` reste **dans le titre binaire d'origine** pour préserver les SHA et la preuve native, malgré son emplacement actif.

## Compatibilité de l'environnement

- CPU minimal **MC68020**, extension AMOS Professional / AP20, R88 **78 commandes** et **88 entrées**, une commande supplémentaire `Aga Cache Blit(CacheBank,X,Y,Mode)`.
- Gate A hôte/native MC68020 : **PASS** (130 scénarios Interpreter + relocation Compiler V2), [preuve CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43730968430). P2.8 **Runtime B / Compiled C WinUAE : NON TESTÉES** ; Amiga physique D non testé.
- Seul ASC actif : [`tests/current/M19_P28_R88_CACHE_BLIT_FPS_01.asc`](../tests/current/M19_P28_R88_CACHE_BLIT_FPS_01.asc) ; quatre ABK sources : [`tests/fixtures/m19_p28/`](../tests/fixtures/m19_p28/). Import ASCII par **Project → Merge ASCII** ; exécuter en Runtime, puis compiler le même ASC sous AMOS Compiler V2. Journaux `RAM:M19_P28_RUNTIME.TXT`, `RAM:M19_P28_COMPILED.TXT`.
- Builder R88 source-backed : `tools/build_m19_p28_r88_in_memory.py`. Il lit le **R87 historique figé** plutôt que le binaire de travail actif, donc la reproduction est possible sans remplacer la R88. Vérification active `tools/verify_fast.py`, archive `tools/verify_p28_archive.py`. Les scripts R87 historiques ne doivent jamais réinstaller R87 automatiquement.

**Aucune modification de `LAST_GOOD`, aucune autre branche, tag, release ou promotion automatique.**
