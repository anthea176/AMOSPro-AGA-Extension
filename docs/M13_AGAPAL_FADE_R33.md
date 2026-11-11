# M13 / R33 0.10.5 — Aga Fade To Bank

## Contrat approuvé par l'utilisateur le 11/11/2026

Fonction unique : `_OK=Aga Fade To Bank(Start(_B),_INDEX,_VBL)`.

- `Start(_B)` doit être le pointeur d'une banque DATA AMOS **vivante** et déjà initialisée AGAPAL v1. Pas un numéro de banque, pas une adresse arbitraire/stale.
- `_INDEX` : emplacement AGAPAL à partir de 0, valide et non vide, contenant de 1 à 256 couleurs RGB24. La banque, ses descripteurs, pixels et fichiers ABK restent inchangés.
- `_VBL` : entier **1 à 255 inclus**. Durée 0, négative, ou >255 refusée ; pour une application immédiate, utiliser R32 `Aga Palette Bank Apply`.
- Écran cible : écran AGA Intuition privé actif de l'extension, couleurs indexées 1 à 8 bitplanes. HAM/EHB/dual playfield rejetés, capacité logique et `ColorMap.Count` suffisantes. Aucune troncature des couleurs cible.
- **Bloquant** : `_VBL` appels explicites à `graphics.library/WaitTOF`, chacun suivi d'un `graphics.library/LoadRGB32` ; l'appel retourne après la dernière image. Pas de temporisation cachée supplémentaire. Ce sont des **attentes de VBL**, pas une garantie d'un délai réel strict de N/50 seconde si le calcul dépasse le temps d'une trame sur 68000.
- Interpolation linéaire RGB24 indépendante par composante, depuis les valeurs affichées capturées une seule fois via `GetRGB32` (si N>1), vers les octets AGAPAL. Pas de gamma, de temporal dither, ni de Copper natif. Pas de fade global des pixels.
- Optimisation : pas 8.8 signé pour les images intermédiaires ; conversion des valeurs en tables RGB32 à fractions répétées ; la **dernière image** copie exactement les octets RGB24 cibles, supprimant les erreurs d'arrondi. Pour `_VBL=1`, un seul `WaitTOF` puis application exacte.
- Palette partielle : remplacer uniquement les pens 0..(colorCount-1), conserver tous les pens supérieurs. Aucun recalcul des pens supérieurs.
- Une seule allocation temporaire Exec `AllocVec(MEMF_PUBLIC)` de **8+42*N octets**, 10 760 octets max pour 256 couleurs : table `LoadRGB32`, snapshot `GetRGB32`, état DDA 8.8. `FreeVec` après utilisation ; aucune RAM persistante ajoutée. Fast RAM utilisable selon l'allocateur OS, sans forcer Chip.
- Retour entier `1` au terme d'un fondu complet et `0` sur rejet sans modification de l'écran. Tous les contrôles de validité et l'allocation sont faits AVANT le premier `WaitTOF`; aucune opération potentiellement refusée après le premier `LoadRGB32`. Si l'écran est fermé extérieurement au milieu de l'appel bloquant, aucun mécanisme d'annulation n'est garanti ; éviter la destruction de l'écran par une tâche concurrente.

## R33 — Candidate Gate A PASS, Gate B en attente

**Gate A native CPU 68000 : 51 scénarios PASS**, 39 commandes AP20, export strict de la source 68000 PASS. [CI R33 Gate A réussie](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43044805057). Tests incluent durée 1/2/3/16/255 VBL, palette partielle, source et cible exactes, refus sans changement, ABI D3/A3, appels WaitTOF/LoadRGB32 exacts, scratch libérée et banque inchangée. **Ce n'est pas un test WinUAE ni une validation de durée réelle.**

**Candidate publiée sur `main` :** `dist/AMOSPro_AGA.Lib` = `dist/experimental/AMOSPro_AGA_M13_v0.10.5_AGAPAL_FADE_TO_BANK_R33.Lib`, R33 0.10.5, **20 208 octets**, SHA256 `e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f`.

**R32 WinUAE-PASS reste `LAST_GOOD` :** `dist/AMOSPro_AGA_LAST_GOOD.Lib`, 19 244 octets, SHA256 `0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894`, identique à l'archive R32.

**Gate B non testée :** installer R33 dans `APSystem` sans changer le slot, relancer AMOS, puis New → Project → Merge ASCII sur [`tests/current/M13_R33_AGAPAL_FADE_01.asc`](../tests/current/M13_R33_AGAPAL_FADE_01.asc). **Attention : écrase les banques 10/11 et `RAM:R33_AGAPAL_FADE.ABK`.** Capturer vert/bleu, fondu 12 VBL vers vert, 1 VBL vers bleu, 2 VBL sur même palette, palette partielle 4 couleurs, durées invalides et index/banque invalides, ABK Save/Load, puis fermeture et retour propre. Valeurs attendues : `GREEN 65280 BLUE 255`, `PART3 660510`, `PART28 16711680`, `RELOAD 1 BLUE 255`, **`RESULT 1`**, **`CLOSE RETURNED`**. Aucune valeur WinUAE confirmée à ce stade.

**Aucune promotion R33 dans LAST_GOOD avant la preuve Gate B utilisateur ; Gates C/D non testées.**

## Contraintes de validation

1. Aucun code antérieur R32, R31 ni archives historiques ne peut changer, sauf ajout du `GetP` du dernier segment R32 nécessaire pour chaîner le nouveau token R33.
2. Builder reproductible en mémoire, syntaxe AP20 39 commandes, signature 3 entiers et ABI AMOS : `D3=_VBL`, `(A3)+=_INDEX`, `(A3)+=Start(_B)`, retour `D3=1/0` et `D2=0`.
3. Gate A : exécution réelle des octets 68000 sous Unicorn, vérification des LVO, ABI, absence de fuites, nombre exact de WaitTOF et LoadRGB32, interpolation et dernier RGB24 exact, cas limites, partial count, non-modification banque/pixels, export natif strict et CI des régressions.
4. Gate B : confirmation utilisateur sous AMOS interprété/WinUAE sur le test ASCII exact. Une fois confirmé, promotion octet pour octet dans `LAST_GOOD`, archivage inchangé du test et mise à jour des deux README dans le même commit.
5. Gates C Compiler et D vrai Amiga AGA : **non testées**. Aucune autre fonction Fade To Black/White/Import/Cycling sans discussion et approbation distinctes.
