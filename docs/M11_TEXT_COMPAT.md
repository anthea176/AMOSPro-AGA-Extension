# M11 — compatibilité graphique AMOS / écran Intuition AGA

## Décision d'architecture

**Correction de conception (11/11/2026) : ne pas tester `Text` natif AMOS sur l'écran Intuition AGA indépendant.** L'expérience `M11_R25_AMOS_TEXT_01.asc`, préparée mais **jamais exécutée sous WinUAE**, partait d'une hypothèse déjà invalide : les primitives AMOS ciblent les écrans et données graphiques **propres à AMOS**, pas notre écran Intuition, qui n'est pas enregistré comme écran AMOS courant. Le Copper participe à la présentation des écrans/bitplanes ; il ne redirige pas les appels de dessin d'AMOS vers un autre RastPort.

Le diagnostic sans valeur ajoutée est classé dans [`tests/historical/M11_R25_AMOS_TEXT_01.asc`](../tests/historical/M11_R25_AMOS_TEXT_01.asc) **sans aucune modification de son contenu**, comme exemple de piste écartée **avant test**. Il ne figure pas parmi les tests PASS et **aucun programme de test actif** n'est demandé à l'utilisateur. Ni ce diagnostic ni son retrait n'établissent un résultat de compatibilité M11.

La bibliothèque **R25 0.9.1** (30 commandes AP20) est conservée sans modification. Les Gates A+B R25 restent validées **pour le scénario R25 archivé**, mais il n'existe **aucune nouvelle Gate M11**. R24, `LAST_GOOD` R10, les tests passés et `examples/` sont protégés.

## Mécanisme à examiner avant de développer

- **AMOS Professional** : `Text`, `Bar`, `Screen Copy` et les outils AMCAF associés utilisent les écrans/banques/états de dessin gérés par AMOS ; ne pas rediriger ses pointeurs privés (`ScOnAd`, `Ec_RastPort`) par hypothèse. Une compatibilité *directe* avec notre écran Intuition ne peut pas être présumée.
- **Notre extension** : l'écran est créé par Intuition ; son `ViewPort`, sa palette et ses bitplanes/buffers sont gérés par l'extension. Il faut identifier dans **la R25 actuelle** le `BitMap` du back buffer utilisé par `Aga Blit Fill/Clear/Copy` et le mécanisme de `Aga Swap`.
- **Texte natif AmigaOS** : `graphics.library/Text(rp,string,count)` rend dans le **RastPort fourni** ; `SetFont`, `SetAPen`, `SetDrMd` et `Move` contrôlent fonte, encre et position. L'option à étudier consiste à disposer d'un `RastPort` **associé au back buffer AGA**, distinct du `Window.RPort` si celui-ci pointe vers le buffer affiché. Sa création/association et son cycle de vie doivent être vérifiés dans notre runtime, pas supposés. Documentation AmigaOS : [Graphics Library and Text](https://wiki.amigaos.net/wiki/Graphics_Library_and_Text), [Intuition Screens](https://wiki.amigaos.net/wiki/Intuition_Screens).
- **Double buffering** : tout rendu (blitter ou texte) doit cibler le même **back buffer** avant `Aga Swap` ; le changement de buffer ne doit ni effacer les glyphes immédiatement ni dessiner dans le buffer déjà affiché. Évaluer la synchronisation, le clipping et la gestion des ressources.
- **Fontes AMOS/AMCAF** : `Change Bank Font` et `Scrn Rastport` n'apportent pas automatiquement un `RastPort` AGA. Étudier séparément les structures de fonte et les licences/données des banques si une importation ou conversion est réellement utile. Ne pas recréer un moteur de fonte sans analyse.

## Prochain travail technique pertinent

1. **Inspection source en lecture seule** : localiser la sélection du back buffer R25, sa `BitMap`, le `RastPort` applicable, la séquence `Swap/Wait Vbl` et les règles mémoire. Documenter ces pointeurs/offsets à partir du code réellement généré et des AmigaOS Autodocs ; éviter toute hypothèse sur les écrans AMOS.
2. **Contrat d'une primitive éventuelle** : décider si un rendu texte natif vers le back buffer est utile, définir les paramètres (position, couleur indexée, chaîne, fonte), la durée de vie de la fonte, les échecs et le clipping. **Aucune nouvelle commande, signature ou R26 n'est encore approuvée.**
3. **Validation distincte** : préflight CPU/ABI, puis un véritable test AMOS/WinUAE de texte rendu **par l'extension sur son propre back buffer** ; Compiler et Amiga physique séparément. Un simple `Text` AMOS ne doit plus être utilisé comme test de faisabilité.
4. **Autres fonctions M11** : palette indexée/RGB AGA pour ne plus charger une mire IFF dans `collide.asc`, copies inter-buffers, Bob/Icon/transparence et primitives Turbo, chacune après un contrat spécifique.

**État : étude d'architecture uniquement, `tests/current/` sans `.asc`. Aucun test M11 exécuté, aucune nouvelle bibliothèque produite.**
