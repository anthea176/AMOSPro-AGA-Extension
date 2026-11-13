# OPT020/P1 — Noyau opaque AGAPIC 16 pixels, 68000 vs 68020

**Ouverture : 13 novembre 2026. État à la publication : code soumis, exécution CPU Musashi / CI en attente.** Travail exclusivement sur `main`.

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

## 3. Validation prévue

Le [test](../tools/test_opt020_p1_bitfield_native.py) utilise la bibliothèque **Musashi via `machine68k==0.4.0`**, capable d'exécuter du vrai code **68EC020 et 68020**, en plus du témoin 68000. Les opcodes sont contrôlés par **Capstone 5.0.9** avec les modes 000 et 020.

Le protocole couvre **256 couples (offset, motif)** par CPU, soit **768 exécutions** indépendantes, avec fond aléatoire, oracle bit-à-bit, comparaison de **tout le buffer** pour détecter les modifications hors champ, contrôles de la source, du retour, d'A3/D5 et de la pile. Les opcodes ne sont pas intégrés à un exécutable AMOS : c'est un **test CPU autonome**. Le workflow P1 isolé ne modifie aucun livrable et n'allonge pas les vérifications R68 normales.

**Les cycles Musashi ne sont pas des mesures WinUAE/Amiga**. Aucun gain ne sera affirmé avant un benchmark WinUAE sans JIT à conditions comparables (68020/14 MHz puis 68030/28 MHz). La prochaine phase devra traiter les 8 plans, le masquage, les groupes RLE et les bords de ligne avant toute bibliothèque.

## 4. Protection de la version promue

**R68 v0.13.13 reste la `LAST_GOOD` inchangée :** 51 064 octets, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`. Gates A/B/C déjà qualifiées sur R68, D physique non testée. **Aucune Gate OPT020 B/C/D ni nouvelle `.Lib` revendiquée.** `tests/current/` garde son seul ASC R68 ; aucun autre ASC actif. `c2p.library` reste hors chantier.
