# M6 R14 0.7.1 — `Aga Blit Fill` : PASS AMOS/WinUAE

> **Historique :** le candidat actif est désormais R15 Clear, voir [M6_BLITTER_R15.md](M6_BLITTER_R15.md). Les chemins ci-dessous désignant R14 comme bibliothèque active ne décrivent que son checkpoint de validation. Le binaire R14 est conservé intact dans `dist/experimental/`.

**État au 10/11/2026 :** R14 est le candidat courant **validé en AMOS interprété/WinUAE pour Fill et la régression Copy**, construit depuis R13 0.7.0 (Copy déjà validé). Compilation AMOS et matériel AGA réel non testés.

## Emplacements officiels

| Élément | Chemin |
|---|---|
| Binaire candidat courant | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) |
| Copie versionnée identique | [`dist/experimental/AMOSPro_AGA_M6_v0.7.1_BLIT_FILL_R14.Lib`](../dist/experimental/AMOSPro_AGA_M6_v0.7.1_BLIT_FILL_R14.Lib) |
| Taille / SHA256 R14 | **9 712 octets**, `a8c43c478efdb2ddcb3547a807a2dba60bd125fc0d7ab5bb791ef565aeb90e4f` |
| Base immuable R13 | `dist/experimental/AMOSPro_AGA_M6_v0.7.0_BLIT_COPY_R13.Lib` (SHA256 `c71cab88d2294ed70c019f546d6c60ac72c278c1b625ded07d0aa6603e50a0cf`) |
| Repli protégé | `dist/AMOSPro_AGA_LAST_GOOD.Lib` = R10 0.6.1 **inchangé** |
| Builder reproductible | `tools/build_m6_blit_fill_r14.py` |
| CPU/ABI | `tools/test_m6_blit_fill_r14.py` |
| **Programme AMOS validé** | [`tests/passed/M6_R14_BLIT_FILL_01.asc`](../tests/passed/M6_R14_BLIT_FILL_01.asc) — fichier identique au test exécuté |

## Commande et garanties

```amos
_OK=Aga Blit Fill(x,y,width,height,colorIndex)
```

- Le résultat entier est **1** si tous les plans ont été remplis et synchronisés ; **0** si argument/état invalide ou si un blit échoue. Ne pas supposer l'atomicité si un appel système échoue après qu'un plan a déjà été modifié.
- Travail uniquement dans le **back buffer actif du double buffering**, en utilisant les structures BitMap réelles, sans écrire dans l'écran frontal.
- Index de couleur **0..(2^Depth-1)** pour 1 à 8 bitplanes ; toute couleur hors plage ou négative est refusée **avant** la première modification.
- Vérification de la géométrie logique ET physique : rectangles dans les limites sans dépassement, largeur/hauteur et stride, Rows, Depth et pointeurs de **tous** les plans de destination non nuls.
- `graphics.library/BltBitMap(-30)` appelé successivement pour chaque bitplane avec **Mask = 1 << plane**, et minterm **$F0** pour le bit de couleur à 1, **$00** pour le bit à 0 ; `WaitBlit(-228)` après **chaque** appel réussi. Il serait erroné d'utiliser $F0 sur tous les plans si l'index n'a pas tous ses bits à 1.
- Les appels AmigaOS peuvent détruire D0/D1/A0/A1 : ces registres sont rechargés à chaque plan. Pas de `WaitPort`, ni de blits directs sur registres chipset.

**Source officielle :** [Autodoc graphics.library/BltBitMap](https://developer.amigaos3.net/autodocs/graphics.library/BltBitMap.html), notamment les minterms $00 et $F0, les limites signées 16 bits et `WaitBlit`.

## Contrat AMOS / AP20

- Signature `00,0,0,0,0` ; entrée **20**. D3 = `colorIndex`, arguments restants lus par `(A3)+` : h, w, y, x.
- À la sortie : A3 a avancé de **16 octets**, D3 = résultat, D2 = 0, SP équilibré ; autres registres conservés selon l'ABI validée.
- Les segments R13 **0 à 18 sont strictement inchangés** ; le segment 19, `Aga Blit Copy`, ne reçoit que le séparateur AP20 final `GetP` ; le segment **20** porte tout le nouveau code Fill.
- Constructeur depuis **l'archive figée R13**, jamais depuis la Lib courante ; aucun changement de R12 ni de `LAST_GOOD`.

## Validation

**Gate A (statique / CPU 68000) : PASS** ([CI #42854705517](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42854705517) — 56 scénarios, reproductibilité, conservation R13, R12, LAST_GOOD). Tests : valeurs de 1, 2, 4 et 8 plans, index 0/max, masques par plan, pixels attendus exacts, zones non affectées, deux valeurs de front buffer, limites/états/pointeurs invalides, échec simulé d'un plan, restitution registres/SP/A3 et non-régression de la R13 Copy.

**Gate B (AMOS interprété/WinUAE) : PASS le 10/11/2026**, sur **MYGIRL.IFF** 320×256×8. Deux captures utilisateur : trois rectangles uniformes aux index 15, 63 et 0, copie du premier en bas. Sortie avec bandeau `M6-R14-BLIT-FILL-01` : `F1 1 F2 1 F0 1`, `COL 0 RECT 0`, `COPY 1 SWAP 1`, `KEY 64 CLOSE RETURNED`. La boîte AMOS indique `End of program at line 77.` Le fichier `.asc` a été archivé sans changement dans `tests/passed/`.

**Gate C AMOS Compiler : NON TESTÉ ; Gate D vrai Amiga : NON TESTÉ.** Ne pas attribuer à R14 les résultats déjà obtenus avec R13.

## Suite

**Fill validé et archivé.** Le prochain sous-jalon M6 est `Aga Blit Clear`, à développer et tester séparément. Aucun test `.asc` actif pour l'instant. Ne pas promouvoir `LAST_GOOD` sans décision explicite.
