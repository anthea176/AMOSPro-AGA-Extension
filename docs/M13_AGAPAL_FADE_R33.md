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

## R33 — Gates A et B fonctionnelle PASS ; démo visuelle confirmée sous WinUAE

**Gate A :** 51 scénarios CPU natifs 68000 PASS, source 68000 strictement exportée, [CI complète 35/35 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43045308067), 39 commandes AP20, ABI 3 paramètres validée, tests d'interpolation, rejets et conservation mémoire.

**Gate B fonctionnelle PASS — capture de l'utilisateur sous AMOS interprété/WinUAE :** `INIT 1 OPEN 1 DB 1`, `CAP0 1 CAP1 1`, `FADE0 1 GREEN 65280`, `FADE1 1 BLUE 255 SAME 1 255`, `PART 1 PEN3 660510 PEN28 16711680`, `BAD0 0 BAD256 0 BADNEG 0`, `BADINDEX 0 EMPTY 0 BADSIZE 0`, `AFTERBAD 16711680 SENTINEL 99`, `ABK AGAPAL SIZE 6224`, `COUNT0 4 COUNT1 256`, `RELOAD 1 BLUE 255`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin normale **ligne 141**.

**Limite importante :** la capture confirme les valeurs finales et le retour propre, mais ne vérifie pas la fluidité du fondu. Le programme original dessinait en back buffer, lançait les transitions (12/1/2 VBL), puis exécutait `Aga Swap` et `Amos To Back` seulement **après les fades**. Les rectangles ne pouvaient donc pas servir d'observation visible pendant les transitions.

**Démo visuelle complémentaire confirmée par l'utilisateur sous WinUAE (11/11/2026), fondu visible et fonctionnel :** [`examples/fade_to_bank.asc`](../examples/fade_to_bank.asc). Trois bandes, rouge → vert → bleu → rouge. Elle appelle `Aga Swap` puis `Amos To Back` **avant** les fondus, utilise 150 VBL par transition et attend entre les changements pour observer les couleurs. **Elle écrase la banque DATA AMOS 12**. Ne pas confondre la démo avec le test de Gate B archivé.

**Promotion binaire R33 :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.5_AGAPAL_FADE_TO_BANK_R33.Lib`, 20 208 octets, SHA256 `e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f`. Toutes copies utilisent exactement le même blob binaire, aucune recompilation.

**R32 figée :** archive `dist/experimental/AMOSPro_AGA_M13_v0.10.4_AGAPAL_BANK_APPLY_R32.Lib`, 19 244 octets, SHA256 `0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894`.

**Test fonctionnel archivé :** [`tests/passed/M13_R33_AGAPAL_FADE_01.asc`](../tests/passed/M13_R33_AGAPAL_FADE_01.asc), Git blob inchangé `ed8446f6b1c89852768df8585e592501e7d5ebc3`. Aucun ASC actif dans `tests/current/`.

**Gates C Compiler / D vrai Amiga AGA NON TESTÉES ; démo visuelle réussie, mais fluidité mesurée, cadence/FPS et durée effective du fondu non quantifiées.** Aucune nouvelle fonction Fade Black/White, Import ou Cycling sans discussion et approbation préalables.

## Contraintes de validation

1. Aucun code antérieur R32, R31 ni archives historiques ne peut changer, sauf ajout du `GetP` du dernier segment R32 nécessaire pour chaîner le nouveau token R33.
2. Builder reproductible en mémoire, syntaxe AP20 39 commandes, signature 3 entiers et ABI AMOS : `D3=_VBL`, `(A3)+=_INDEX`, `(A3)+=Start(_B)`, retour `D3=1/0` et `D2=0`.
3. Gate A : exécution réelle des octets 68000 sous Unicorn, vérification des LVO, ABI, absence de fuites, nombre exact de WaitTOF et LoadRGB32, interpolation et dernier RGB24 exact, cas limites, partial count, non-modification banque/pixels, export natif strict et CI des régressions.
4. Gate B fonctionnelle **PASS utilisateur** sous AMOS interprété/WinUAE sur l'ASC exact ; promotion et archivage sans modification de contenu. **Observation visuelle positive** : la démo distincte de 150 VBL a été exécutée avec succès sous WinUAE ; les performances temporelles ne sont pas mesurées.
5. Gates C Compiler et D vrai Amiga AGA : **non testées**. Aucune autre fonction Fade To Black/White/Import/Cycling sans discussion et approbation distinctes.
