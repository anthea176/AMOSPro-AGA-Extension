# M19 P0c — staging Chip privé MC68020 : Gate A CPU (16/11/2026)

## Portée réelle

**SOURCE NATIVE PRIVÉE ET TESTÉE SUR CPU020 (Exec/graphics simulés)** ; aucun nouveau token AP20, aucune modification de la bibliothèque installable, aucun résultat WinUAE ou AMOS Compiler pour ce code P0c. Le moteur d'affichage Bob n'est pas encore livré.

- Dépôt autorisé : \`anthea176/AMOSPro-AGA-Extension\` sur \`main\`.
- Bibliothèque P0b toujours active : \`dist/AMOSPro_AGA.Lib\` **82 376 octets**, SHA256 \`f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9\`, 82 commandes et 92 entrées AP20.
- Source : [\`tools/m19_p0c_chip_stage_emit.py\`](../tools/m19_p0c_chip_stage_emit.py), **1 304 octets de code natif déterministe** ciblant **MC68020/68EC020 minimum**.
- Banc CPU : [\`tools/test_m19_p0c_chip_stage_native.py\`](../tools/test_m19_p0c_chip_stage_native.py) ; **64 scénarios MC68020 sous Unicorn** avec deux placements de code. [CI PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43914021013).
- Modèle de géométrie ABK/planar antérieur : [\`tools/m19_p0b_chip_dma_model.py\`](../tools/m19_p0b_chip_dma_model.py), **9 scénarios HOST PASS**.
- [CI politique CPU et destinations PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43914021170) ; CI de reconstitution P0b et tests 116 scénarios également PASS sur le même HEAD.

## Contrat interne de trois points d'entrée, pas une API AMOS

| Entrée privée | Paramètres natifs | Résultat |
|---|---|---|
| \`stage_entry\` | A0 = début des seuls pixels/masques planaires AGBO contigus **déjà vérifiés** ; D0 = taille exacte en octets ; A1 = contexte interne privé zéro-initialisé ; D1 = identité du payload AMOS (paire) ; D4 = génération AGBO ; A4 = \`GfxBase\` pour tout remplacement | D3 = 1 succès / 0 refus ; D2 = 0 |
| \`release_entry\` | A1 = contexte propriétaire ; A4 = \`GfxBase\` valide si allocation active | D3/D2 identiques |
| \`lookup_entry\` | A1 = contexte ; D0 = identité actuelle contrôlée par l'appelant ; D1 = génération actuelle contrôlée | 1 uniquement si la représentation préparée appartient à cette identité/génération |

Contexte **20 octets**, à allouer dans l'état natif privé : pointeur Chip (+0), taille (+4), identité payload (+8), génération (+12), cookie propriétaire \`CHIP\` (+16). Aucune banque AMOS numérotée auxiliaire.

**Préparation :** avant modification du contexte, le noyau vérifie CPU, paramètres et alignement, plage source déclarée, cohérence de l'ancien contexte, éventuelle allocation Chip précédente ; demande ensuite un **\`AllocVec(size, MEMF_PUBLIC|MEMF_CHIP)\`**. Il vérifie \`TypeOfMem\` au premier et au dernier octet du bloc alloué, puis appelle \`CopyMem\` sur la taille exacte. Si une étape échoue, il appelle \`FreeVec\` pour libérer la nouvelle allocation, **sans écraser l'ancien contexte**. Une fois les données copiées, le remplacement passe par **\`graphics.library/WaitBlit\` avant la libération de l'ancienne source**. \`release_entry\` attend également la fin du Blitter avant \`FreeVec\`. Aucun \`Aga Swap\` ni attente Exec non bornée.

Le critère de plage complète repose sur la **garantie \`AllocVec(MEMF_CHIP)\` pour tout le bloc contigu**, plus la vérification \`TypeOfMem\` aux deux extrémités ; \`TypeOfMem\` sur deux adresses arbitraires ne prouverait pas à lui seul la continuité d'une banque inconnue. Il est interdit d'exposer au DMA une source non allouée ainsi. \`AllocVec\`/**\`FreeVec\`** évite les erreurs d'association de taille de \`AllocMem\`/\`FreeMem\`.

**Références vérifiées :**
- [AmigaOS 3.x NDK — AllocMem, MEMF_CHIP](https://developer.amigaos3.net/autodocs/exec.library/AllocMem.html).
- [Table des LVO Exec](https://arisamiga.github.io/amiga-bootcamp/14_references/exec_lvo_table/) : \`TypeOfMem=-534\`, \`CopyMem=-624\`, \`AllocVec=-684\`, \`FreeVec=-690\`.
- [Graphics — WaitBlit obligatoire avant de libérer une ressource Blitter](https://wiki.amigaos.net/wiki/Graphics_Primitives).

## Tests MC68020 de la Gate A privée

Sous Unicorn CPU modèle \`UC_CPU_M68K_M68020\`, les services système sont simulés avec destruction volontaire des registres volatils D0/D1/A0/A1 pour détecter les violations ABI. Le test couvre :

- allocation de données alignées, parité exacte des pixels/masques et canaries hors plage ;
- deux emplacements du même code natif pour vérifier les liens PC relatifs ;
- allocation impossible, refus de la mémoire non Chip sur début ou fin, restitution de toute allocation transitoire ;
- remplacement d'une allocation existante, attente Blitter et libération **après** attente ;
- refus lors de remplacement si \`GfxBase\` est absent ; état original conservé ;
- taille nulle, impaire, excessive ; pointeurs/identités nuls ou impairs ; génération nulle ; contexte corrompu ;
- \`lookup\` sur identité/génération périmées, \`release\` sûr/idempotent ; garde CPU si \`AFF_68020\` absent ;
- conservation des registres préservés et de A7, ABI D3/D2, décodage MC68020 Capstone.

**Résultat effectif : 64 scénarios PASS, code natif 1 304 octets**, logs GitHub Actions du 16/11/2026. **Ceci est une Gate A de noyau privé, non une Gate A d'instruction AMOS complète.**

## Verrous restants avant la nouvelle .Lib ou l'affichage Bob

1. Le **wrapper AMOS/public** doit valider l'intégralité de \`AGBO\` v1 (métadonnées, offsets, limites et masques), ainsi que la véritable identité de banque AMOS ; il transmettra ensuite uniquement les pixels/masques contigus au helper. Le helper n'accepte pas lui-même une banque ABK brute non validée.
2. Définir l'emplacement, le cycle d'initialisation et le cleanup de la table des **contextes par banque** dans le groupe natif BOBS. Le contexte ponctuel du test n'est pas encore intégré à l'état de la Lib.
3. Chaque dessin devra revalider l'identité et la génération de la banque sélectionnée ; après \`Erase\`/\`Load\` ou recapture, ne jamais réutiliser les anciens pointeurs. \`Poke\` direct dans AGBO non supporté.
4. Revoir la forme exacte de la commande publique \`Aga Bob Bank Free N\` et des commandes objet/rendu avant l'ajout de tokens ; pas de nouveau token dans ce jalon.
5. Gate A CPU/AP20 de la **candidate complète** puis Gates B WinUAE et C AMOS Compiler réelles sur le nouveau test exact. Le test P0b (Runtime/Compiled PASS) ne valide pas automatiquement ce code P0c.

**Protections :** \`dist/AMOSPro_AGA.Lib\`, \`dist/AMOSPro_AGA_LAST_GOOD.Lib\` R84, \`tests/current/M19_P0B_MC68020_MASK_BANK.asc\` et tous les tests/archives existants restent inchangés. Aucune promotion, aucun exécutable AMOS P0c.
