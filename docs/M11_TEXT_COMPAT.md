# M11 — compatibilité graphique AMOS / écran Intuition AGA

**Mise à jour 11/11/2026 :** cette note décrit la décision **antérieure à R26** d'abandonner le test `Text` natif AMOS. L'extension a depuis obtenu **Gate A CPU/CI et Gate B WinUAE PASS sur le test R26 `Aga Text`**, [archivé sans modification](../tests/passed/M11_R26_AGA_TEXT_01.asc). Voir le [rapport de validation](M11_TEXT_R26.md). Les phrases historiques « non implémenté » qui suivent concernent l'état au moment de l'étude, pas l'état courant.

## Décision d'architecture

**Correction de conception (11/11/2026) : ne pas tester `Text` natif AMOS sur l'écran Intuition AGA indépendant.** L'expérience `M11_R25_AMOS_TEXT_01.asc`, préparée mais **jamais exécutée sous WinUAE**, partait d'une hypothèse déjà invalide : les primitives AMOS ciblent les écrans et données graphiques **propres à AMOS**, pas notre écran Intuition, qui n'est pas enregistré comme écran AMOS courant. Le Copper participe à la présentation des écrans/bitplanes ; il ne redirige pas les appels de dessin d'AMOS vers un autre RastPort.

Le diagnostic sans valeur ajoutée est classé dans [`tests/historical/M11_R25_AMOS_TEXT_01.asc`](../tests/historical/M11_R25_AMOS_TEXT_01.asc) **sans aucune modification de son contenu**, comme exemple de piste écartée **avant test**. Il ne figure pas parmi les tests PASS et **aucun programme de test actif** n'est demandé à l'utilisateur. Ni ce diagnostic ni son retrait n'établissent un résultat de compatibilité M11.

La bibliothèque **R25 0.9.1** (30 commandes AP20) est conservée sans modification. Les Gates A+B R25 restent validées **pour le scénario R25 archivé**, mais il n'existe **aucune nouvelle Gate M11**. R24, `LAST_GOOD` R10, les tests passés et `examples/` sont protégés.

## Audit source R25 effectué — point d'entrée validé

**11/11/2026 :** [audit technique détaillé du back buffer R25](M11_BACKBUFFER_R25.md), fondé sur la lecture des builders, du 68000 reconstruit et une **comparaison des octets AP20 R23/R25**. Les segments 10 (`Double Buffer`), 11 (`Swap`), 12 (`Back Fill`), 19 (`Blit Copy`) et 20 (`Blit Fill`) sont **identiques** entre les deux binaires.

Le chemin `A5+$1C8 → State+32 → DBState+8 → ScreenBuffer inactif → sb_BitMap(+0)` est connu. `Aga Back Fill` relie **déjà** ce `BitMap` à un `RastPort` temporaire via `InitRastPort` et `RastPort.BitMap(+4)`. **Nouveau point de vigilance :** `Aga Swap` pose `DBState+20=3` (Safe/Disp en attente), tandis que `Aga Wait Vbl` ne consomme pas ces notifications. Le futur rendu texte devra respecter l'accusé **Safe** avant d'écrire sur le back buffer.

**Proposition non approuvée :** une unique fonction texte utilisant `graphics.library/Text`, après validation de la chaîne AMOS et du clipping. **Aucun binaire R26 et aucun test M11 n'ont été créés.** Le détail de la synchronisation, des pointeurs et des gates se trouve dans la [note d'audit](M11_BACKBUFFER_R25.md).

## Prototype R26 en préparation

Un [contrat de première API texte](M11_TEXT_R26.md) et trois scripts de construction/validation en mémoire ont été préparés depuis l'archive figée R25 ; **Gate A R26 confirmée : 64 cas CPU/CI PASS** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42921696298)), **candidate R26 0.9.2 publiée** ([archive](../dist/experimental/AMOSPro_AGA_M11_v0.9.2_TEXT_R26.Lib)). La Gate B WinUAE n'a pas encore été testée. Le verrou Safe est traité **dans la nouvelle primitive seulement** ; les anciens Blitters R25 restent tels quels.

## Mécanisme à examiner avant de développer

- **AMOS Professional** : `Text`, `Bar`, `Screen Copy` et les outils AMCAF associés utilisent les écrans/banques/états de dessin gérés par AMOS ; ne pas rediriger ses pointeurs privés (`ScOnAd`, `Ec_RastPort`) par hypothèse. Une compatibilité *directe* avec notre écran Intuition ne peut pas être présumée.
- **Notre extension** : l'écran est créé par Intuition ; son `ViewPort`, sa palette et ses bitplanes/buffers sont gérés par l'extension. Il faut identifier dans **la R25 actuelle** le `BitMap` du back buffer utilisé par `Aga Blit Fill/Clear/Copy` et le mécanisme de `Aga Swap`.
- **Texte natif AmigaOS** : `graphics.library/Text(rp,string,count)` rend dans le **RastPort fourni** ; `SetFont`, `SetAPen`, `SetDrMd` et `Move` contrôlent fonte, encre et position. L'option à étudier consiste à disposer d'un `RastPort` **associé au back buffer AGA**, distinct du `Window.RPort` si celui-ci pointe vers le buffer affiché. Sa création/association et son cycle de vie doivent être vérifiés dans notre runtime, pas supposés. Documentation AmigaOS : [Graphics Library and Text](https://wiki.amigaos.net/wiki/Graphics_Library_and_Text), [Intuition Screens](https://wiki.amigaos.net/wiki/Intuition_Screens).
- **Double buffering** : tout rendu (blitter ou texte) doit cibler le même **back buffer** avant `Aga Swap` ; le changement de buffer ne doit ni effacer les glyphes immédiatement ni dessiner dans le buffer déjà affiché. Évaluer la synchronisation, le clipping et la gestion des ressources.
- **Fontes AMOS/AMCAF** : `Change Bank Font` et `Scrn Rastport` n'apportent pas automatiquement un `RastPort` AGA. Étudier séparément les structures de fonte et les licences/données des banques si une importation ou conversion est réellement utile. Ne pas recréer un moteur de fonte sans analyse.

## Prochain travail technique pertinent

1. **Inspection source R25 : TERMINÉE.** Accès exact au BitMap, RastPort temporaire déjà existant et suivi Safe/Disp documentés dans [l'audit M11](M11_BACKBUFFER_R25.md). Reste à spécifier **la synchronisation sûre** d'une nouvelle routine après `Aga Swap`.
2. **Contrat d'une primitive éventuelle** : décider si un rendu texte natif vers le back buffer est utile, définir les paramètres (position, couleur indexée, chaîne, fonte), la durée de vie de la fonte, les échecs et le clipping. **Aucune nouvelle commande, signature ou R26 n'est encore approuvée.**
3. **Validation distincte** : préflight CPU/ABI, puis un véritable test AMOS/WinUAE de texte rendu **par l'extension sur son propre back buffer** ; Compiler et Amiga physique séparément. Un simple `Text` AMOS ne doit plus être utilisé comme test de faisabilité.
4. **Autres fonctions M11** : palette indexée/RGB AGA pour ne plus charger une mire IFF dans `collide.asc`, copies inter-buffers, Bob/Icon/transparence et primitives Turbo, chacune après un contrat spécifique.

**État : étude d'architecture uniquement, `tests/current/` sans `.asc`. Aucun test M11 exécuté, aucune nouvelle bibliothèque produite.**
