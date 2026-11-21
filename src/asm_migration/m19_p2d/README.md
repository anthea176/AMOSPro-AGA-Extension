# M19 P2d — migration assembleur MC68020

Le source de production de l'extension reste **le code Python des emitters**
(`tools/build_m19_p2d_in_memory.py` et ses modules). Les fichiers .s places
ici sont une **conversion verifiee**, destinée à migrer les routines vers un
assembleur maintenable, pas un nouveau binaire a installer.

## Contrat exact

- Original : `dist/AMOSPro_AGA.Lib` **M19 P2d**, 136 020 octets,
  SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`.
- Cible : Motorola **MC68020** minimum.
- Source : builder exact P2d, quatre groupes AP20 identifies dans le binaire
  mais verifies contre les emitters Python et leurs labels ; les instructions
  reconnues deviennent de vrais mnemoniques (MOVE, BSR, JSR, BFEXTU, RTS...).
- Le wrapper AP20, les marqueurs AMOS `FE31`, les donnees et les octets de
  code restant a classer sont conserves en directives de donnees. Il ne faut
  pas les confondre avec du source assembleur maintenable deja restaure.
- Verification : chaque unite `.s` reassemblee par vasm `-Fbin -m68020 -no-opt`
  doit etre **identique octet pour octet** au groupe correspondant du builder ;
  le `M19_P2D_AP20_SOURCE.s` relie doit etre identique aux 136 020 octets.
  Un simple listing/decompilateur ne suffit pas.

## Reproduire sous Windows

Mettre `vasmm68k_mot.exe` dans `tools/`, mettre a jour `main`, et
executer le `EXPORT_REAL_SOURCE.bat` a la racine. Les sources sont produites
dans `src/generated/p2d_source/` ; verifier
`M19_P2D_SOURCE_MANIFEST.json` avec `verified_native_asm: true`.

## Statut

**Gate A source/vasm** : voir la CI
[reconstruction P2d](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/workflows/m19-p2d-source-assembler.yml).
Le resultat de chaque export est aussi lie a son manifeste JSON. Ce travail
**ne remplace pas** le builder Python ni les Gates WinUAE Runtime et Compiler
de la Lib. Aucun fichier de `dist/`, `tests/current/`, `tests/passed/`
ou autre depot n'est modifie par l'export.
