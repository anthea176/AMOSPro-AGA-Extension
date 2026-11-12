# M15bis/R44 — Aga Mouse Cursor : Gates A/B PASS, clôturé et promu LAST_GOOD (12/11/2026)

**Statut final — M15bis/R44 v0.11.5 CLÔTURÉ :** contrat approuvé, 516 scénarios CPU 68000 et CI Gate A PASS, test WinUAE du curseur confirmé (`SWITCHES 500 ERR 0`, `CHIP DROP 0`, `RESULT 1`, `CLOSE RETURNED`), puis démonstration interactive [M15 + M15bis](../examples/m15_2d_cursor.asc) confirmée sous WinUAE (« ça marche super »). **49 commandes AP20 / 55 segments, 27 460 octets**, SHA256 `0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc`. `dist/AMOSPro_AGA.Lib`, `dist/AMOSPro_AGA_LAST_GOOD.Lib` et l'archive R44 sont identiques. Test d'origine archivé dans `tests/passed/` sans modification ; R43 et les versions antérieures restent archivées. [Clôture détaillée](M15_M15BIS_R44_CLOSURE.md). **Gates C/D non testées.**

## Objectif demandé

Afficher/masquer **uniquement le pointeur de la fenêtre Intuition de l'écran AGA privé** de l'extension. Ne pas masquer la souris dans Workbench, les autres fenêtres ou sur les écrans AMOS natifs. La position, les boutons, le clavier et les événements de souris doivent fonctionner même lorsque le pointeur est invisible. Par défaut, le pointeur reste visible.

## API publique validée — une seule fonction AMOS

```amos
_OK=Aga Mouse Cursor(Visible)
```

- `Visible=0` : masquer l'image du pointeur dans la fenêtre AGA de l'extension, **sans désactiver la souris**.
- `Visible=1` : restaurer le pointeur Intuition normal de cette fenêtre.
- `_OK=1` : demande acceptée et appliquée au réglage de la fenêtre, même si l'état était déjà demandé (**idempotence**). Si la fenêtre est inactive, le réglage sera visible lorsqu'elle redeviendra active.
- `_OK=0` : écran/fenêtre AGA non ouvert, pointeurs d'état invalides, valeur autre que 0/1, ou échec d'allocation de la petite image transparente Chip. Sur refus, ne changer ni l'état enregistré ni le pointeur d'une autre fenêtre.
- Aucun argument supplémentaire, pas de mode global, de forme de pointeur personnalisable, de sprite AMOS ou d'interaction avec `Ink`. Résultat entier AP20 ; index de commande envisagé **54** après Circle index 53, donc **49 commandes / 55 segments** si le contrat est accepté.

## Contrat technique

1. **API Intuition ciblée** : `SetPointer(Window*, BlankSprite*, 16, 16, 0, 0)` pour masquer ; `ClearPointer(Window*)` pour réafficher. Il s'agit du pointeur associé à la fenêtre active et non d'une désactivation du sprite global. Un déplacement du focus vers Workbench/une autre fenêtre montre son propre pointeur ; de retour sur la fenêtre AGA, le masque configuré demeure tant qu'il n'a pas été retiré.
2. **Contrôle d'appartenance** : utiliser exclusivement `Window*` du runtime AGA, historiquement à `state+36`, avec vérification du `Screen*` et de `Window.WScreen` (+46), d'`IntuitionBase` (+4) et des conditions d'écran ouvert. Ne jamais passer une fenêtre Workbench/native AMOS. Les offsets restent à revérifier contre le binaire R43 avant code.
3. **Mémoire** : sprite vide **16 × 16, deux plans de 1 bit** ; `2 + (16 × 2) + 2 = 36 UWORD = 72 octets` à zéro (contrôles et fin inclus), allocation `Exec AllocMem(MEMF_CHIP|MEMF_CLEAR)` seulement au premier masquage réussi. Les plans à zéro rendent le sprite transparent. Le buffer doit rester valide tant qu'Intuition peut le référencer.
4. **Durée de vie** : garder ce buffer unique pendant la vie de la fenêtre, même après `ClearPointer`, pour éviter des allocations répétées. Aucun re-alloc/free à chaque bascule. Sur fermeture, dissocier via `ClearPointer` **avant** `CloseWindow`, puis libérer les 72 octets seulement après que la fenêtre soit fermée / ne puisse plus référencer les données. Si le premier `AllocMem` échoue, retourner 0 et laisser le pointeur visible. L'état visible est réinitialisé à la prochaine ouverture.
5. **Chemins à vérifier/adapter** : `Aga Screen Close`, fermeture sans double buffer, écran avec double buffer, fermeture partielle après échec `OpenWindow`, cleanup Ctrl+C de `Aga Key / Aga Wait Key`, fermeture/réouverture et chemins d'erreur du runtime. **Ce chantier peut requérir des adaptations contrôlées de segments historiques de fermeture et d'initialisation**, en préservant l'ABI, le dispatcher et les comportements validés. Ne pas promettre que seule l'entrée R44 changera.
6. **Pas de manipulation globale** : ni `Sprite Off`, ni accès direct `SPR0` / DMA / Copper, ni `SetPrefs`, ni changement des bitplanes, palette, `RMBTRAP`, IDCMP, souris ou pointeur Workbench. Pas de `WaitVbl`/Swap implicite dans cette commande.
7. **State** : le pointeur Chip et le drapeau caché doivent avoir une propriété/durée de vie explicite. Vérifier la taille et le nettoyage du bloc d'état actuel avant de réserver des offsets ; ne jamais écrire au-delà des **40 octets historiques** supposés sans auditer l'allocation dans le R43 actuel.

## Gates et critères du contrat d'origine

- **Gate A CPU/CI** : ABI/token AP20, lecture des arguments LONG, seules valeurs 0/1, vérification Window/Screen, appels `SetPointer / ClearPointer` et paramètres exacts, zéro écriture hors mémoire, structure sprite 72 octets `MEMF_CHIP|MEMF_CLEAR`, OOM sans effet, appels répétés, restauration à toutes les sorties, état fermé/réouvert et Ctrl+C, non-régression des 48 commandes R43, contrôles HUNK/AP20/export strict.
- **Gate B AMOS interprété / WinUAE** : pointeur visible au démarrage ; masquer/réafficher ; souris X/Y, clics gauche/droit et clavier actifs en mode masqué ; Workbench et autres fenêtres gardent leur pointeur ; retour dans AGA toujours masqué si configuré ; fermeture pendant le masquage, réouverture, Ctrl+C ; alternances prolongées (par exemple 500) et contrôle d'absence de perte progressive de Chip RAM. Un seul test `.asc` actif à la fois et confirmation visuelle utilisateur.
- **Gates C et D indépendantes** : compilateur AMOS et Amiga AGA réel, non déduites des Gates A/B.
- **Publication éventuelle** : `R44` dans `dist/AMOSPro_AGA.Lib` + archive versionnée **après Gate A PASS** ; `LAST_GOOD` reste R43 jusqu'à Gate B utilisateur PASS ; archiver l'ASC original sans le retoucher avant promotion. Travail sur **`main` uniquement**.

## Sources et état

- [Roadmap existante — M15bis](ROADMAP.md) : demande de pointeur local à la fenêtre, nettoyage obligatoire, pas de commande engagée.
- [AmigaOS Intuition Pointer](https://wiki.amigaos.net/wiki/Intuition_Pointer) : `SetPointer / ClearPointer`, format sprite, exigence Chip RAM.
- [AmigaOS Window Structures and Functions](https://wiki.amigaos.net/wiki/Window_Structures_and_Functions) : visibilité du pointeur associée à la fenêtre active.
- [Intuition Input R3 historique](../tools/obsolete/build_intuition_input_r3.py) : `Window*` en state+36, taille ancienne 40, helpers `CloseWindow` et Ctrl+C (historique uniquement, à confronter à R43).
- **Décision reçue et appliquée** : nom `Aga Mouse Cursor`, mode `0=masqué / 1=visible`, allocation unique 72 octets Chip, restauration automatique. **Gates A/B validées, `LAST_GOOD` R44 promue.** Le test du curseur et la démo globale sont confirmés sous WinUAE ; les critères Compiler/AGA physique restent non testés.

**Retour WinUAE R44 du 12/11/2026** : capture du test curseur avec `SHOW 1 1 1`, `HIDE 1 1`, `SWITCHES 500 ERR 0`, `CHIP DROP 0`, `BIG DROP 0`, `CHIP BEFORE/END 1801928 / 1801928`, `RESULT 1`, `CLOSE RETURNED`, puis démonstration globale M15/M15bis fonctionnelle selon l'utilisateur. Ces preuves ne couvrent pas AMOS Compiler ni Amiga physique. [Rapport de clôture](M15_M15BIS_R44_CLOSURE.md).
