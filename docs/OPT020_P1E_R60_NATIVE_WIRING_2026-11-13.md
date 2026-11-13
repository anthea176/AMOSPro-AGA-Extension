# OPT020/P1e — raccordement réel R60 → noyaux 68020

**13 novembre 2026 — Gate A CPU/CI PASS, aucune validation WinUAE.**

- Branche unique : `main`, commit source testé : `91de56fcbec4a3ba544fe969ae92a34d0aac92ab`.
- [GitHub Actions OPT020 43497183949](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43497183949) : PASS, y compris tous les contrôles P1/P1b/P1c/P1d et la nouvelle étape P1e.
- 51 cas d'exécution CPU du véritable chemin R60 avec services AMOS/Exec simulés sous Musashi, dont les cas 68000 rejetés avant les instructions 020, 68EC020 et 68020 acceptés.
- La prévalidation 68000 R60 n'est **pas réécrite** : contrôle banque DATA vivante via `Bnk.GetAdr`, enveloppe mémoire, dimensions et format AGAPIC v1, offsets de lignes, tous paquets RLE/masques/padding en PASS 0. Aucun pixel n'est modifié avant succès de cette passe.
- Une fois les limites de la destination vérifiées, acquisition `Safe` non bloquante, PASS 1 et dessin dans les plans du **bitmap Intuition inactif**, sans Blitter ni copie intégrale source en Chip.
- Nouveau peintre [`opt020_p1e_painter_emit.py`](../tools/opt020_p1e_painter_emit.py) : réutilisation du clipping P1c, `emit_masked_multiplane_020` (groupes complets) et `emit_fragment_020` (champs partiels); pointeurs temporaires dans la trame R60.
- `emit_image_region()` historique **inchangé** : 2 012 octets. `emit_image_region(opt020=True)` : 2 174 octets ; SHA256 `504a61d49ac95967cfddab041841c72f09df11d86845c71366c950d1d742a8c9`.
- ABI vérifiée : 7 paramètres consommés `A3+28`, `A7`, `D2=0`, `D3=0/1`, registres, arrière-plan/canaries/front et refus non destructifs ; contrôle `ExecBase.AttnFlags` avant tout opcode 020.
- Vérification V2 sans écriture disque : **51 228 octets** AP20, unité de compilation monolithique **48 528 octets**, structures et jetons conservés ; ce test n'est pas un véritable Compiler.
- Les premiers essais ont révélé deux défauts **du nouvel adaptateur seulement** : retour imbriqué `decode_rows → paint_group` (restauration A2 via `SP+8`, et non `SP+4`) et chute du succès `D3=1` dans le rejet explicite. Corrigés et confirmés par la CI finale.

## Contrat de protection

`dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` demeurent la R68 v0.13.13, empreinte protégée SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`. Ni binaire de travail, ni ASC actif, ni archives, ni `tests/passed/` n'ont été modifiés. Aucun autre candidat produit.

## Limites et prochaine étape

La CI prouve **Gate A CPU uniquement**, pas l'installation de l'extension sous AMOS ni le comportement du Compiler réel. Le banc utilise des hooks simulés pour `Bnk.GetAdr`, `TypeOfMem` et `GetMsg`, et le modèle Intuition mémoire ; il ne remplace pas WinUAE.

Compléter la matrice profondeurs 1/2/4/8, stride/clip aux bords, source RLE malformée, échecs `Safe`, flags DATA 0/1/3 et scénarios de relocation AP20, puis produire **une seule candidate** dans `dist/AMOSPro_AGA.Lib`, après Gate A/CI. Gate B AMOS interprété ensuite ; réserver la **seule** compilation AMOS Compiler à la fin de P1e (Gate C) ; bench WinUAE JIT OFF avant tout chiffre de performance.
