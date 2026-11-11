# M13 / R33 0.10.5 — Aga Fade To Bank

## Contrat approuvé par l'utilisateur le 11/11/2026

Fonction unique : \`_OK=Aga Fade To Bank(Start(_B),_INDEX,_VBL)\`.

- \`Start(_B)\` doit être le pointeur d'une banque DATA AMOS **vivante** et déjà initialisée AGAPAL v1. Pas un numéro de banque, pas une adresse arbitraire/stale.
- \`_INDEX\` : emplacement AGAPAL à partir de 0, valide et non vide, contenant de 1 à 256 couleurs RGB24. La banque, ses descripteurs, pixels et fichiers ABK restent inchangés.
- \`_VBL\` : entier **1 à 255 inclus**. Durée 0, négative, ou >255 refusée ; pour une application immédiate, utiliser R32 \`Aga Palette Bank Apply\`.
- Écran cible : écran AGA Intuition privé actif de l'extension, couleurs indexées 1 à 8 bitplanes. HAM/EHB/dual playfield rejetés, capacité logique et \`ColorMap.Count\` suffisantes. Aucune troncature des couleurs cible.
- **Bloquant** : \`_VBL\` appels explicites à \`graphics.library/WaitTOF\`, chacun suivi d'un \`graphics.library/LoadRGB32\` ; l'appel retourne après la dernière image. Pas de temporisation cachée supplémentaire. Ce sont des **attentes de VBL**, pas une garantie d'un délai réel strict de N/50 seconde si le calcul dépasse le temps d'une trame sur 68000.
- Interpolation linéaire RGB24 indépendante par composante, depuis les valeurs affichées capturées une seule fois via \`GetRGB32\` (si N>1), vers les octets AGAPAL. Pas de gamma, de temporal dither, ni de Copper natif. Pas de fade global des pixels.
- Optimisation : pas 8.8 signé pour les images intermédiaires ; conversion des valeurs en tables RGB32 à fractions répétées ; la **dernière image** copie exactement les octets RGB24 cibles, supprimant les erreurs d'arrondi. Pour \`_VBL=1\`, un seul \`WaitTOF\` puis application exacte.
- Palette partielle : remplacer uniquement les pens 0..(colorCount-1), conserver tous les pens supérieurs. Aucun recalcul des pens supérieurs.
- Une seule allocation temporaire Exec \`AllocVec(MEMF_PUBLIC)\` de **8+42*N octets**, 10 760 octets max pour 256 couleurs : table \`LoadRGB32\`, snapshot \`GetRGB32\`, état DDA 8.8. \`FreeVec\` après utilisation ; aucune RAM persistante ajoutée. Fast RAM utilisable selon l'allocateur OS, sans forcer Chip.
- Retour entier \`1\` au terme d'un fondu complet et \`0\` sur rejet sans modification de l'écran. Tous les contrôles de validité et l'allocation sont faits AVANT le premier \`WaitTOF\`; aucune opération potentiellement refusée après le premier \`LoadRGB32\`. Si l'écran est fermé extérieurement au milieu de l'appel bloquant, aucun mécanisme d'annulation n'est garanti ; éviter la destruction de l'écran par une tâche concurrente.

## R33 — statut de développement

**Contrat approuvé ; code/essais Gate A en préparation.** R32 0.10.4 reste **la version WinUAE validée et LAST_GOOD** :
\`dist/AMOSPro_AGA.Lib\` = \`dist/AMOSPro_AGA_LAST_GOOD.Lib\`, 19 244 octets,
SHA256 \`0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894\`.
Les Gates A (CPU et CI) et B (AMOS/WinUAE) sont **non testées pour R33** à cette étape. Compiler/Amiga physique restent non testés.

**Source R33 en développement** : \`tools/m13_agapal_fade_r33_emit.py\`,
\`tools/build_m13_agapal_fade_r33.py\`, \`tools/test_m13_agapal_fade_r33.py\`.
La future candidate (après Gate A) sera \`dist/AMOSPro_AGA.Lib\`
et son archive figée \`dist/experimental/AMOSPro_AGA_M13_v0.10.5_AGAPAL_FADE_TO_BANK_R33.Lib\`.
**Ne pas promouvoir R33 dans LAST_GOOD avant confirmation de Gate B.**

**Test AMOS prévu pour la Gate B** : [\`tests/current/M13_R33_AGAPAL_FADE_01.asc\`](../tests/current/M13_R33_AGAPAL_FADE_01.asc).
Le test écrase les banques 10 et 11 et le fichier \`RAM:R33_AGAPAL_FADE.ABK\`.
Séquence prévue : capture de palettes verte/bleue, départ rouge, fondu 12 VBL vers vert,
1 VBL vers bleu, 2 VBL sur la même palette, fondu partiel préservant pen28,
durées invalides (0/256/négatif), index absent/vide, banque invalide,
sauvegarde/rechargement ABK natif et fondu après \`Load\`,
refus après fermeture d'écran et retour propre AMOS.
Résultat attendu final : \`RESULT 1\` et \`CLOSE RETURNED\` (non encore observés).

## Contraintes de validation

1. Aucun code antérieur R32, R31 ni archives historiques ne peut changer, sauf ajout du \`GetP\` du dernier segment R32 nécessaire pour chaîner le nouveau token R33.
2. Builder reproductible en mémoire, syntaxe AP20 39 commandes, signature 3 entiers et ABI AMOS : \`D3=_VBL\`, \`(A3)+=_INDEX\`, \`(A3)+=Start(_B)\`, retour \`D3=1/0\` et \`D2=0\`.
3. Gate A : exécution réelle des octets 68000 sous Unicorn, vérification des LVO, ABI, absence de fuites, nombre exact de WaitTOF et LoadRGB32, interpolation et dernier RGB24 exact, cas limites, partial count, non-modification banque/pixels, export natif strict et CI des régressions.
4. Gate B : confirmation utilisateur sous AMOS interprété/WinUAE sur le test ASCII exact. Une fois confirmé, promotion octet pour octet dans \`LAST_GOOD\`, archivage inchangé du test et mise à jour des deux README dans le même commit.
5. Gates C Compiler et D vrai Amiga AGA : **non testées**. Aucune autre fonction Fade To Black/White/Import/Cycling sans discussion et approbation distinctes.
