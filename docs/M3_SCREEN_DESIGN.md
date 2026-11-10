# M3 — Premier écran AGA 320 x 256 / 256 couleurs

**Statut : prototype M3a v0.0.3 validé en interprété sous WinUAE avec `Amos To Back` / `Amos To Front` ; `AGA DEMO RETOUR = 1`. La même démonstration fonctionne également en compilé, confirmé le 31/10/2026.** Voir [M3A_PROTOTYPE.md](M3A_PROTOTYPE.md).

## Objectif

Dans la même extension AP20 (slot 14), ajouter un écran 8 bitplanes / 256 indices couleur, **sans modifier le moteur ECS d'AMOS Professional 365 ni ses fichiers**. Cible : 68020+, AGA Alice/Lisa, Kickstart 3.0+, 2 MiB Chip RAM recommandés.

## Décision architecturale provisoire

**Privilégier l'API Intuition/graphics.library de Kickstart 3.x** pour créer une `Screen` autonome à 8 bitplanes et laisser l'OS gérer le Copper, l'allocation Chip et les registres AGA. Ne pas reprendre globalement les procédures de Copper/écrans de l'interpréteur Unity (elles dépendent de structures internes AMOS modifiées).

- Ouverture pressentie : `OpenScreenTagList()` avec `SA_DisplayID` = PAL/LORES, `SA_Width` 320, `SA_Height` 256 et `SA_Depth` 8.
- Palette : `LoadRGB32` ou `SetRGB32` via le `ViewPort` Intuition, dans une deuxième sous-étape, plutôt que programmer directement BPLCON3.
- Dessin du motif : `graphics.library` dans le `RastPort` appartenant à l'écran ouvert. Éviter tout accès brut au bitmap d'AMOS.
- Fermeture : `CloseScreen()` sur le pointeur qui **appartient à l'extension**, une seule fois. Réinitialiser l'état interne et restaurer l'affichage avant de rendre la main.

**Risque majeur à investiguer avant une livraison :** AMOS 365 manipule son propre affichage/Copper, et un écran Intuition peut ne pas passer au premier plan ou interférer avec la vue AMOS. Il faut vérifier le comportement réel d'AMOS en interprété **et** en compilé, sans supposer que l'ouverture Intuition suffit à l'afficher.

## API proposée (pas encore implémentée)

```amos
If Aga Detect<>0
   Aga Screen Open
   Aga Test Pattern
   Wait Key
   Aga Screen Close
End If
```

Le **prototype M3a** est historiquement fixe (320×256×8), mais **M3b devra avoir une API paramétrable dès le départ** pour accepter largeur, hauteur, nombre de couleurs/profondeur et ModeID. L'implémentation sera validée progressivement sur les modes PAL, HiRes, entrelacé, NTSC, SuperHiRes et modes spéciaux EHB/HAM8. Les combinaisons doivent être vérifiées par la base des modes AmigaOS, pas acceptées aveuglément. Voir [M3B_PLAN.md](M3B_PLAN.md).

## Contraintes de conception

1. `Aga Detect` doit être vrai avant toute allocation AGA. Refuser proprement le mode sur ECS.
2. Ne pas écrire dans les registres DMA/Copper d'AMOS, ne pas appeler directement LoadView sans conservation/restauration démontrée.
3. Protéger les ressources : ouverture de libraries, pointeur `Screen`, mémoire Chip, et traitement de tous les échecs.
4. Conserver la **même sémantique entre interpréteur et compilateur**, avec source Genam relogeable et une table AP20 correcte.
5. Autoriser `Aga Screen Close` après échec d'ouverture ; prévenir ouverture multiple.
6. Empreinte théorique du seul bitmap : 320×256×8/8 = **81 920 octets** Chip RAM, hors Copper, structures, sprites, buffers et surcoûts d'alignement.
7. Ne pas modifier les commandes AMOS `Screen Open`, `Colour`, `Bob` avant d'avoir une preuve d'isolation.

## Ordre des tests

- M3a : ouverture/fermeture d'un écran AGA en interprété (retour à AMOS et Workbench propre).
- M3b : même scénario compilé, puis contrôle de non-régression sur l'affichage AMOS et le retour au Workbench.
- M3c : palette 256 couleurs et motif permettant de distinguer explicitement les indices 0, 31, 32, 127, 128, 255.
- M3d : boucle ouverture/fermeture, mémoire Chip avant/après, double appel `Close`, échec simulé par manque de mémoire, et comportement ECS.
- M4 seulement : double buffering, VBL, banques/objets.

La v0.0.2 R1 validée est figée dans `archive/AMOSPro_AGA_v0.0.2_R1_M2_OK.Lib`. **Toute expérimentation graphique doit être une nouvelle version**.

## Références utiles

- [AMOS Unity — Screens](https://github.com/AmiDARK/AmosProfessionalUnity-SourceCode/blob/main/src/AmosProUnityAGA_Library/Screens.s), [CopperListSystem](https://github.com/AmiDARK/AmosProfessionalUnity-SourceCode/blob/main/src/AmosProUnityAGA_Library/CopperListSystem.s) : analyse et lecture seule, pas d'importation brute.
- [AmigaOS : Custom Screen Type](https://wiki.amigaos.net/wiki/Custom_Screen_Type) : `OpenScreenTagList` et `CloseScreen`.
- [AGA 320x256 / 256 couleurs](https://arisamiga.github.io/amiga-bootcamp/01_hardware/aga_a1200_a4000/aga_display_modes/) : mode PAL/LORES, 8 bitplanes.


## Après M3a

Le test `AGA_DEMO_VISIBLE.asc` est confirmé fonctionnel en interprété et compilé. Le prochain jalon est [M3b — commandes d'écran persistantes](M3B_PLAN.md). Ne pas modifier le binaire M3a validé.


## Prototype expérimental M3b-1 v0.0.4

Un premier HUNK de 1564 octets a été produit. L'écran est conservé entre trois commandes, et l'ouverture prend largeur, hauteur, nombre de couleurs (2–256 indexées) et ModeID. La bibliothèque conserve les anciennes routines M3a, mais remplace le cold init par une zone d'état avec hooks RESET/END. **Ce prototype ne dispose pas encore de retour WinUAE.** Voir [M3B_V004_TEST.md](M3B_V004_TEST.md) avant tout essai.
