# C2P OPT020 — variantes expérimentales R78 / R79 / R80

**Date : 14 novembre 2026 — branche \`main\`. Statut : sources de préparation uniquement.**
**R80 v0.13.25 reste le chantier actif, non clôturé.** Ce document n'autorise pas une nouvelle candidate, une compilation AMOS, une promotion ou un remplacement de \`LAST_GOOD\`.

## Livrables de préparation

- [\`tools/c2p_opt020_variants.py\`](../tools/c2p_opt020_variants.py) : trois fonctions d'émission **séparées** des émetteurs historiques. Elles reprennent le binaire émis par chaque version, vérifient les quatre octets à remplacer, insèrent un \`BRA.W\` PC-relatif et ajoutent un nouveau noyau à la fin de l'entrée native.
- [\`tools/test_c2p_opt020_variants.py\`](../tools/test_c2p_opt020_variants.py) : vérifications structurelles de conservation des octets d'origine, des branches, du caractère déterministe, du tableau de correspondance et de l'arithmétique nearest-neighbour. Lancer explicitement depuis la racine : \`python -B tools/test_c2p_opt020_variants.py\`.
- **Aucun** des trois émetteurs \`c2p_r78_blit_emit.py\`, \`c2p_r79_zoom_emit.py\`, \`c2p_r80_iff_chunky_emit.py\` n'est modifié. Les builders historiques et leurs SHA restent la référence.

| Variante | Remplacement préparé | Sémantique conservée |
|---|---|---|
| **R78 Blit / OPT020** | Copie par \`MOVE.L (A0)+,(A1)+\` de quatre indices puis 0–3 octets résiduels | Protection des deux banques, recouvrement interdit, clipping, couleur 0 opaque, ABI et retour |
| **R79 Zoom / OPT020** | Quotient, reste et dénominateur DDA chargés **une fois par ligne** dans les registres au lieu d'être relus à chaque pixel ; \`ADDA.L\` sur le pointeur source | Nearest-neighbour exact, géométrie/clipping, aucun changement de palette |
| **R80 IFF→Chunky / OPT020** | Table de 16 nibbles / 64 octets, adressage 68020 \`(A6,D0.L*4)\`, expansion par deux \`OR.L\` pour huit indices, sans \`BTST/BSET\` par pixel. Vérification \`AFF_68020\` avant le décodage | Prévalidation du BODY, RAW/ByteRun1, banques intactes en cas de rejet, deux passes, sortie chunky 320×256 |

Les nouvelles routines ne modifient pas les précédentes fonctionnalités, mais **aucun avantage chronométré n'est revendiqué**. Le 68020 est désormais le CPU minimal du projet ; le code de vérification du CPU avant instructions exclusives reste 68000-safe pour refuser proprement une machine incompatible.

## Bloquants avant une intégration éventuelle

1. **Finir la R80 en cours** et conserver ses résultats comme référence. Ne toucher ni à \`dist/AMOSPro_AGA.Lib\`, ni à \`dist/AMOSPro_AGA_LAST_GOOD.Lib\`, ni à \`tests/current/\` tant que ce jalon n'est pas clôturé.
2. Vérifier le **vrai code émis** avec les sources historiques du dépôt, désassemblage et exécution sous émulateur CPU 68020 (Gate A) ; les seuls tests Python structurels **ne prouvent pas** son exécution, l'ABI ou la sûreté mémoire.
3. Lors du futur assemblage d'une candidate approuvée, sélectionner les variantes dans un **nouveau builder**, sans modifier les builders figés R78/R79/R80 ni leurs SHA. Vérifier la disposition AP20 finale, les sept LEA clavier/souris, les branches, \`D2/D3/A3/A7\`, les canaries et les cas de refus.
4. Vérifier pixels exacts, 4–8 plans, rectangles impairs/non alignés, clipping et tailles extrêmes, IFF RAW/ByteRun1, indices 0 et 255. Puis seulement les Gates WinUAE interprétée et Compiler selon le protocole du projet.
5. **Pas de campagne de mesure de vitesse imposée** pour décider de développer ces optimisations ; les contrôles fonctionnels et de non-régression restent obligatoires.

**Aucune modification au code installé de l'extension, aucun build et aucune publication.**
