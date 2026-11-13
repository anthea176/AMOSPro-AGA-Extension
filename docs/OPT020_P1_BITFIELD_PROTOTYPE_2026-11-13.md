# OPT020/P1 — Noyau opaque AGAPIC 16 pixels, 68000 vs 68020

**Validation P1 du 13 novembre 2026 : PASS sur le noyau autonome 68000 / 68EC020 / 68020, [CI 43489837368](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43489837368).** Travail exclusivement sur `main`. Aucune bibliothèque 020 installable.

[Émetteur source](../tools/opt020_p1_bitfield_emit.py) · [Test natif](../tools/test_opt020_p1_bitfield_native.py) · [Workflow P1](../.github/workflows/opt020-p1.yml)

## 1. Ce que ce prototype teste

Un **groupe opaque de 16 pixels**, pris dans un groupe planaire AGAPIC déjà décodé, est copié depuis un mot 16 bits dans le back buffer cible. La source est alignée ; l'origine X destination a un **offset de 0 à 7 bits**. Les bits extérieurs aux 16 pixels copiés ne doivent pas changer.

La version **68000** utilise une boucle réelle de 16 itérations `BTST/BSET/BCLR`. La variante **68020/68EC020** encode et exécute réellement :
- `BFEXTU (A0){0:16},D1` : extraire les 16 pixels planaires.
- `BFINS D1,(A1){D0:16}` : les insérer dans le back buffer sans toucher aux bits voisins.

La variante 68020 occupe **12 octets** de code autonome. Les mots sont encodés explicitement selon le manuel Motorola, puis **désassemblés Capstone en mode 020**. Il ne s'agit pas d'un simple réglage de compilation qui générerait encore du code 68000.

## 2. Contrat et limites de l'optimisation

**Préconditions imposées au futur wrapper :** `A0` pointe vers un mot source lisible et aligné, `A1` vers une zone de destination valide (au moins 3 octets disponibles), `D0` vaut 0..7 ; les 16 pixels sont entièrement visibles, le groupe est opaque, sans masque, et la destination est le back buffer **inactif** dont le `Safe` a été obtenu. `D3=1` au retour ; le sous-noyau ne préserve que les invariants `A3`, `D5` et la pile vérifiés dans le banc. Les autres registres, et `A1` dans la référence 000, sont des temporaires.

**Non traité à P1 :** flux RLE et limites des paquets, mode masqué, clipping, bords de lignes, taille/validité d'une banque, 8 plans à la fois, allocation, resynchronisation Blitter, ABI AP20/Compiler V2, émission du binaire installable. Ces cas nécessitent un fallback ou des validations avant toute intégration. La source AGAPIC peut rester en Fast RAM puisque les accès sont CPU.

## 3. Validation réelle — CPU 020 autonome PASS

Le [test](../tools/test_opt020_p1_bitfield_native.py) utilise la bibliothèque **Musashi via `machine68k==0.4.0`**, capable d'exécuter du vrai code **68EC020 et 68020**, en plus du témoin 68000. Les opcodes sont contrôlés par **Capstone 5.0.9** avec les modes 000 et 020.

Le protocole a réellement exécuté **256 couples (offset, motif)** sur chacun des trois CPU, soit **768 exécutions Musashi PASS**, avec fond aléatoire, oracle bit-à-bit, comparaison de **tout le buffer** (dont les canaries), contrôles de la source, du retour, d'A3/D5 et de la pile. **Zéro différence et zéro erreur**. La CI atteste le décodage Capstone et l'exécution native complète du sous-noyau. Les opcodes ne sont pas intégrés à un exécutable AMOS ; le workflow P1 isolé ne modifie aucun livrable.

| Cible | Source exécutée | Octets de code | SHA256 du code natif | Résultat |
|---|---|---:|---|---|
| **68000** | Boucle de référence | 54 | `be7d3d5ba8352b12805e9d20197b9166ca24673c27434bf9721ef4ab0f87a0cf` | PASS 256/256 |
| **68EC020** | `BFEXTU` + `BFINS` | 12 | `27b068d79e7e8b043e1d453dcca36846b75c08c5dfb0d626017f0618be55e6b5` | PASS 256/256 |
| **68020** | Même binaire 020 | 12 | `27b068d79e7e8b043e1d453dcca36846b75c08c5dfb0d626017f0618be55e6b5` | PASS 256/256 |

**Estimation Musashi cumulée (à ne pas utiliser comme chronométrage Amiga) :** 68000 `312256` cycles, 68EC020 `14336`, 68020 `14336` pour les 256 cas par cible. Les nombres reflètent le sous-noyau autonome dans Musashi, **sans** coût de décodage RLE, API AMOS, Fast/Chip, DMA, caches ou Clip ; ne pas en faire un ratio de performance réel.

[Journal de validation complet](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43489837368) · [Commit des opcodes/test](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/17df14a8e4a677fdefa59b59bc6e0b2145518231).

**Les cycles Musashi ne sont pas des mesures WinUAE/Amiga**. Aucun gain ne sera affirmé avant un benchmark WinUAE sans JIT à conditions comparables (68020/14 MHz puis 68030/28 MHz). La prochaine phase devra traiter les 8 plans, le masquage, les groupes RLE et les bords de ligne avant toute bibliothèque.

## 4. Protection de la version promue

**R68 v0.13.13 reste la `LAST_GOOD` inchangée :** 51 064 octets, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`. Gates A/B/C déjà qualifiées sur R68, D physique non testée. **Aucune Gate OPT020 B/C/D ni nouvelle `.Lib` revendiquée.** `tests/current/` garde son seul ASC R68 ; aucun autre ASC actif. `c2p.library` reste hors chantier.

**Suite du 13/11/2026 :** [P1b multi-plans, masques, RLE et clipping](OPT020_P1B_AGAPIC_RLE_MASK_2026-11-13.md) **PASS sous Musashi** sur 68EC020 et 68020 : 320 contrôles directs, 432 rendus complets, 5 352 groupes natifs, huit refus sans écriture. Le noyau multiplan autonome fait 36 octets ; le décodage RLE et le clipping restent orchestrés en Python. Aucune accélération mesurée dans WinUAE et aucun binaire AMOS modifié.
