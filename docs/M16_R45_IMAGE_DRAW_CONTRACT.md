# M16/R45 — Contrat proposé : `Aga Image Draw` depuis banque DATA AGAPIC

**Statut : conception prête à être discutée / implémentée, mais NON LIVRÉE.** Le conteneur [AGAPIC v1 est validé sous AMOS/WinUAE](M16_AGAPIC_WINUAE_P0_PASS.md) ; le codec et le modèle planaire ont passé leurs tests hôte. **Aucune commande `Aga Image Draw` n'existe dans R44**. Ne pas modifier `LAST_GOOD` avant Gate B du futur R45.

## 1. API candidate (une seule fonction AP20)

```amos
_OK=Aga Image Draw(Start(10),Length(10),X,Y,Mode)
```

- `Start(bank)` : adresse de la **zone DATA** d'une banque AMOS vivante AGAPIC v1 ; ne pas transmettre le numéro de banque brut ni une adresse conservée après `Load`/`Erase`/`Bank Swap`.
- `Length(bank)` : longueur DATA réelle ; **la taille interne AGAPIC doit être identique**.
- `X,Y` : coordonnées entières signées de l'origine supérieure gauche dans l'écran AGA privé ; interprétation 16/32 bits à confirmer au niveau de l'ABI 68000.
- `Mode=0` : **opaque**, écrit chaque pixel de l'image, **y compris l'index couleur 0**.
- `Mode=1` : **transparent** si masque 1 bit présent, garde les pixels masqués, mais peut parfaitement écrire **la couleur 0 sur un pixel visible**. Aucun alpha partiel.
- `_OK=1` : appel valide appliqué (même image totalement hors écran sans écriture) ; `_OK=0` : refus sans modification du back buffer, sauf éventuel effet sur l'indicateur Safe à documenter explicitement.
- Profondeur de l'image **égale** à celle du bitmap cible dans R45 ; palette séparée, gérée par les API M13. Pas d'overlay entre profondeurs différentes en v1.

**ABI AP20 à vérifier sur source R44** : `D3` reçoit le dernier argument `Mode` ; la pile `A3` livre dans l'ordre inverse `Y`, `X`, `Length(bank)`, `Start(bank)`. Cette convention est cohérente avec `Aga Draw` (R41) et `Aga Font Bank Select` (R38), mais le test natif doit la prouver pour cette signature à cinq entiers. Résultat entier `D3=1/0`, `D2=0`, registres non volatils et `A3/SP` conservés conformément au contrat R44.

## 2. Audit du chemin graphique existant

Le futur moteur doit réutiliser **sans changer la sémantique R44** :

- État privé sous `A5+$1C8` ; `State+0` Screen*, `State+8` GfxBase*, `State+12/+16/+28` largeur/hauteur/profondeur, `State+32` DBState*.
- `DBState+8` : index de l'avant ; le *back buffer* se trouve dans l'autre `ScreenBuffer`, qui expose `sb_BitMap` à l'offset 0. `BitMap+0/+2/+5/+8` : BytesPerRow, Rows, Depth, table des Plane*.
- **Contrôle Safe non bloquant**, comme R40/R43, avant chaque écriture. Ne jamais supposer qu'un Wait VBL autorise automatiquement l'ancien front buffer. Pas de Swap ni de WaitPort implicite dans la fonction.
- L'extension possède la fenêtre Intuition AGA ; ne pas utiliser les écrans AMOS normaux, `ScOnAd`, `AMOS Screen` ni le `Window.RPort`.
- La première version ne doit ni allouer de grande image décompressée en Chip RAM, ni toucher les segments R44 existants autrement que par les modifications AP20 strictement nécessaires et vérifiées.

Sources : [audit back buffer](M11_BACKBUFFER_R25.md), [Aga Plot R40](../tools/m15_plot_r40_emit.py), [Aga Draw R41](../tools/m15_draw_r41_emit.py), [Aga Circle R43](../tools/m15_circle_r43_emit.py), [codec AGAPIC v1](../tools/m16_agapic.py).

## 3. Sécurité de la banque et du décodeur

**Prévalidation complète en lecture seule avant le premier mot écrit** :

1. Refuser pointeur nul/impair/non plausible et longueurs hors limites ; contrôler via Exec `TypeOfMem` au minimum les extrémités des zones avant tout déréférencement, ainsi que la structure DATA AMOS (`Start-24`…`Start-1`) selon le précédent R30/R38. **`TypeOfMem` ne prouve pas à lui seul la propriété d'une allocation** : seuls les `Start(bank)` vivants sont contractuellement admissibles.
2. Valider `AGAPIC`, version 1, flags réservés à zéro, codec 1, dimensions/depth/group bytes, table de lignes et taille exacte, sans overflow de multiplication 32 bits.
3. Parcourir **tous** les paquets RLE (sur un premier passage **sans écriture graphique**) ; exiger nombres de groupes par ligne exacts, pas de paquets tronqués, pas de chevauchement d'offsets, zéro bourrage sur groupes finaux.
4. Vérifier le mode (mask obligatoire si Mode=1), les dimensions du back buffer, la profondeur de tous les plans, leurs pointeurs et le `BytesPerRow`. Confirmer ou refuser explicitement les bitmaps interleavés suivant leur sémantique réelle ; ne jamais supposer une organisation mémoire non prouvée.
5. Si l'image est entièrement invisible, retourner `1` sans lire/écrire les bitplanes ; garder une convention uniforme pour Safe et documenter si un appel visible peut refuser pour back buffer non Safe.

**Dessin CPU** : pour chaque groupe de 16 pixels, calculer les mots bitplanes + masque ; ne conserver que la plage de pixels visible après clipping. Si `X mod 16 != 0`, fusionner les portions gauche/droite dans **deux mots destination bornés** (sur chacun des plans) ; traitement de bord droit lorsque largeur non multiple de 16. Formule par plan :

```text
nouveau = (ancien & ~masque_visible) | (pixels_source & masque_visible)
```

En mode opaque, `masque_visible` contient les bits réellement présents après clipping, même pour un pixel de couleur 0. En mode transparent, c'est le masque de la banque AND le masque de clipping. **Ne pas utiliser le Blitter** pour lire la Fast RAM.

## 4. Plan de validation

- **Gate A / CPU 68000 + CI** : token AP20 50e commande et segment éventuel R45, ABI A3/D2/D3, HUNK/relocations, export natif strict, fonte R44 figée, refus avant écriture, Safe/Disp, lectures Fast et écritures Chip simulées. Cas 1/2/4/8 plans, mode 0/1, index 0 masqué et visible, largeurs 1/15/16/17/31/32, X = -17/-1/0/1/15/16/319/320, Y négatifs/bords, profondeur incohérente, RLE malformé, overflow, alloc/mémoire et fermeture.
- **Gate B / AMOS interprété + WinUAE** : un seul test courant pour afficher visuellement la banque 64×40×4 sur écran privé 320×256×16 couleurs. Fond géométrique contrasté, exemplaires opaques et transparents, **les pixels de couleur 0 doivent pouvoir effacer le fond là où le masque vaut 1**, clipping sur les quatre côtés, déplacements X non alignés et swaps répétés. Capturer `RESULT 1`, `CLOSE RETURNED` et observation visuelle.
- **Performances distinctes** : 68000 puis 68020/68030 sous WinUAE avec le même écran et les mêmes images ; mesurer temps de décompression, dessin, mémoire et comparaison à IFF/Blitter selon des conditions reproductibles. Pas de promesse de FPS sans chiffres.
- **Gates C/D** : AMOS Compiler et Amiga AGA physique non testés tant qu'il n'existe pas de recette spécifique.

## 5. Gel et décision

L'étape AGAPIC P0 est **PASS pour le format ABK sous WinUAE**, et pour le codec/modèle CPU **sur hôte uniquement**. Le runtime R45 n'a pas commencé. Les 49 commandes et l'archive de **R44 v0.11.5 `LAST_GOOD` restent inchangées**, de même que les versions antérieures et les tests passés. Le travail reste exclusivement sur `main`.

**Décision à enregistrer au lancement R45 :** nom exact `Aga Image Draw`, signature à cinq entiers, comportement de retour et de Safe, politique profondeur identique, aucune allocation Chip de l'image complète. Aucun contrat ici n'autorise à déclarer une Gate A/B PASS sans le code et les preuves.
