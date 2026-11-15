# M19 P2.8 R88 — diagnostic Runtime WinUAE, caches AGPC en Fast RAM (15/11/2026)

## Preuves observees

- Binaire attendu par le test : **R88 v0.13.33**, candidate active non promue, 75 040 octets SHA256 `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc`. La chaine `LIBRARY_EXPECTED` du journal ne prouve pas a elle seule les octets de la bibliotheque effectivement chargee.
- Journal utilisateur initial `M19_P28_RUNTIME.TXT` : `PRG_STATE 1`, `RESULT 0`, `ERR 12`, `PARITY_OK 0`, `RLE_CALLS 0`, `CACHE_CALLS 0`, `FRAMES_TOTAL 0`, `SWAPS 0`, `CLOSE_RETURNED 1`.
- Journal de diagnostic `M19_P28_DIAG_RUNTIME.TXT` : `PRG_STATE 1`, `DIAG_DONE 1`, `ERR 0`, banques **11 et 13** de 360 octets, nom `AGPCACHE`, `B11/B13_AGPC_FLAGS 3`, enveloppe AMOS de 376 octets. Les flags AMOS en memoire sont revenus a **0** dans les deux banques.
- `CHIP_BEFORE 1796336`, `CHIP_AFTER_LOAD 1796336` (delta 0) ; `FAST_BEFORE 138189720`, `FAST_AFTER_LOAD 138188952` (delta -768). Les adresses payload sont `B11 0x40429B60` et `B13 0x40429CE0`.
- **Quatre rejets propres** : `CACHE_11_MODE0 0`, `CACHE_11_MODE1 0`, `CACHE_13_MODE0 0`, `CACHE_13_MODE1 0`. Fermeture AGA : `CLOSE_RETURNED 1`. Aucune mesure FPS disponible.

## Diagnostic technique

Le fichier ABK contient bien le cache AGPC v1/v2 et indique une preference Chip (flags disque 3), mais **AMOS Load ne garantit pas la residence DMA en Chip RAM** dans l'environnement essaye. Le moteur natif R88 reutilise le coeur Blitter masque M18, qui exige `TypeOfMem(MEMF_CHIP)` pour les blocs source. Son rejet `0` est attendu avec ces banques Fast. Le diagnostic est fort au vu de la variation memoire et des refus observes ; il reste a confirmer que le staging corrige donne des appels et pixels corrects.

Source : `tools/m18_ficon16_chip_blit_emit.py` (MEMF_CHIP du source slot), `tools/m19_p28_agpc_ap20_emit.py` (controle AP20 + entete), manuel AMOS Pro, annexe E (flags bank Chip/Fast et nom modifiable) : https://amospromanual.dev/99-appendix-e-memory-bank-structures.html.

## Correction du banc — NON VALIDEE EN RUNTIME

Le banc courant `tests/current/M19_P28_R88_CACHE_BLIT_FPS_01.asc` (Git blob `001396551cad6fed57903b714bc374e0988f63ea`) charge chaque banque AGPC d'abord en banque temporaire **20**, reserve ensuite la banque definitive **11/13** par `Reserve As Chip Data N,360`, copie les **360 octets** et les **8 octets du nom de banque** uniquement (pas les flags/tete systeme), efface la banque temporaire et verifie flags Chip Data **3** et delta Chip positif. Nettoyage securise de la banque 20 en cas d'erreur ; `CHIP_BANKS_STAGED`, `CHIP_FLAG11/13`, `CHIP_STAGE_DELTA` dans le journal.

Le moteur `dist/AMOSPro_AGA.Lib` n'est **pas modifie** ; l'architecture n'abandonne pas la protection DMA Chip. Les actifs `dist/AMOSPro_AGA.Lib` (R88), R87 archive, `dist/AMOSPro_AGA_LAST_GOOD.Lib` (R84), et `tests/passed/` demeurent proteges.

**Gates** : A native R88 PASS sur le binaire precedent inchange ; B de l'ASC original FAIL ; B de l'ASC avec staging **NON TESTEE** ; C Compiler R88 **NON TESTEE** ; D physique **NON TESTEE**. Refaire Runtime et verifier `RESULT 1`, `ERR 0`, parites et `FRAMES_TOTAL 288` avant toute mesure de performance.
