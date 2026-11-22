# M19 S1-P1b — Premier pont écran AGA privé vers AGSP RGB24

> **Gate A CPU PARTIELLE PASS 22/11/2026 :** [CI 45011441994](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45011441994) : 6 tests du vrai binaire MC68020 assemble et execute sous Unicorn. Services systeme et buffers simules ; aucune vraie commande AMOS ni Gate B/C.

**Date :** 22 novembre 2026. **Cible : MC68020 / 68EC020 minimum.**

**Statut initial : module source MC68020 proposé, à tester par CI vasm/Unicorn.**
Ce module est **isolé** ; il ne modifie pas P2d, LAST_GOOD, AP20, aucune banque AMOS, ni un Sprite matériel. Il ne prétend pas avoir exécuté WinUAE ou le Compiler.

## Source et interface

[Source ASM](../src/native/m19_s1/M19_S1P1B_SCREEN_RGB24_MC68020.s), [banc CPU 68020](../tools/test_m19_s1p1b_screen_rgb24.py), [workflow](../.github/workflows/m19-s1-p1b-screen-rgb24.yml).
Le noyau P1 existant reste [source unique de conversion des pixels](../src/native/m19_s1/M19_S1P1_AGSP_CAPTURE_MC68020.s).

Le pont prend `A0` = pointeur d'une **requête de 36 octets** fournie par le futur wrapper AP20 :

| Offset | Type | Contenu |
| ---: | --- | --- |
| 0 | LONG | Pointeur de l'état écran AGA privé, normalement `$01C8(A5)` |
| 4 | LONG | Tampon RGB32 temporaire, capacité **3072 octets** |
| 8 | LONG | Tampon RGB24 temporaire, capacité **768 octets** |
| 12 | LONG | Descripteur P1 de sortie, capacité **64 octets** |
| 16 | LONG | Pixels planaires de staging, capacité **4×H octets** |
| 20 | LONG | Palette AGSP locale de staging, capacité **48 octets** |
| 24 | WORD | X de capture sur l'écran privé |
| 26 | WORD | Y de capture |
| 28 | WORD | Hauteur, **1..256**, largeur fixe 16 |
| 30 | WORD | Index transparent `0..255` |
| 32 | LONG | Réservé = 0 |

Sortie `D0=1, D1=256` succès, `D0=0, D1=0` refus. Registres `D2..D7/A2..A6` préservés ; le module appelle `graphics.library/WaitBlit` puis `GetRGB32(ColorMap,0,256,temp)`. Les octets de poids fort des 768 LONGs sont copiés dans la palette RGB24 exacte ; aucun écrit dans `ColorMap`.

## Contrats issus de la source P2d et d'AGAPIC

- `Screen` est à `state+0`, `graphics.library` à `state+8`, largeur/hauteur à `+12/+16`, nombre de couleurs `+20`, profondeur `+28`, DoubleBuffer à `+32`.
- `ColorMap` est à `Screen+48`, et `ColorMap.Count` à `+2` ; ici **mode 8 plans et au moins 256 couleurs** seulement.
- Sélection du buffer inactif : `front=0` utilise `DoubleBuffer+4`, `front=1` utilise `DoubleBuffer+0`. Vérifier **bit 0 Safe** à `DoubleBuffer+20` avant tout appel graphique.
- `ScreenBuffer.sb_BitMap` à +0, puis `BitMap.BytesPerRow` WORD +0, `Rows` WORD +2, `Depth` BYTE +5, `Planes[8]` à +8.
- Aucune attente bloquante ni consommation de message `SafePort` si l'état n'est pas prêt ; **refus sans écriture dans descripteur/RGB24**. Pas de `Aga Swap`, pas de DMA Sprite.

**Préconditions de sécurité encore non levées :** la requête doit être construite par une routine native propriétaire qui **prouve l'allocation et la taille complètes de tous les pointeurs** par les services Exec, l'écran et la stabilité pendant l'extraction ; ce helper vérifie géométrie, état Safe, pointeurs non nuls et parité, mais **n'est pas un validateur de mémoire arbitraire**. L'absence de remplacement des banques sur refus est assurée seulement lorsque l'étape de commit transactionnel est raccordée.

**Attention IFF :** le bridge lit le buffer arrière suivant le contrat Bob P2d, mais **il reste à vérifier dans le véritable WinUAE que `Aga Iff Load` dépose effectivement la planche dans ce buffer** dans la configuration choisie. Ne pas inventer de changement de page.

## Validations et jalons

Le banc exécute **les octets MC68020 vasm** sur Unicorn : état faux/Unsafe, face avant 0/1, ColorMap 256, RGB32 simulé en respectant le vrai ABI GetRGB32, stride, refus sans modification, **puis le vrai noyau natif P1** sur le descripteur produit, comparé à `m19_s1_agsp_bank.py`. Simulations OS ≠ WinUAE.

**Prochaine tranche S1-P1b** : un wrapper AMOS/AP20 vérifie les tailles et les pointeurs sous Exec, gère les buffers temporaires, appelle ces deux modules, prépare et publie une **banque DATA AGSP transactionnelle** (insertion/remplacement/sauvegarde). Le vrai test `Save/Load` AMOS reste **Gate B non exécutée**. N'autoriser aucun Sprite DMA/Off avant qualification de la palette et du démontage Copper.
