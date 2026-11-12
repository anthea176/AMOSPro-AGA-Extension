# M16/R46 — Correction des flags de banque DATA AMOS chargée (12/11/2026)

**Statut : R46 v0.12.1 candidate, Gate A CPU 68000/CI PASS ; Gate B AMOS/WinUAE NON TESTÉE.** La version précédente **R45 v0.12.0 a échoué Gate B** lors des captures utilisateur : aucune image AGAPIC affichée, mais les rectangles tracés par `Aga Box` fonctionnent.

## Diagnostic établi par les deux captures WinUAE R45

```text
BANK 10 BYTES 1836 OPEN 1 DB 1
OPAQUE 0 MASK 0 SHIFT 0
CLIP 0 0 0 0
BAD 0 0 0 OUT 0
SWAP 1 BACKSAFE 0
NOSCREEN 0 CLOSED -1
NATIVE LEN 1852 WANT 1852
NATIVE NO 10 FLAGS 0
NATIVE NAME AGAPIC
HEAD AGAPIC V 1
STREAM 196 TOTAL 1836
ERRORS 0 RESULT 0
CLOSE RETURNED
```

**Cause identifiée, reproduite sur la machine 68000 émulée :** R45 exigeait `Deek(Start(bank)-12)` égal à 1 (DATA/Fast) ou 3 (DATA/Chip, bit 1 ignoré). Dans WinUAE, la vraie banque DATA chargée depuis l'ABK présente **flags natifs 0**, avec les autres champs conformes : longueur native = longueur DATA + 16, numéro 10, nom `AGAPIC  `, signature et offsets AGAPIC v1 corrects. Le garde R45 rejette donc la banque **avant** le décodage RLE, le Safe et le dessin. Même l'image entièrement hors écran (`OUT`) renvoie 0 à cause de ce refus préalable. Le programme a terminé normalement, `CLOSED -1` ; ce champ ne révèle pas d'anomalie.

**Important :** flags natifs 0 ne prouvent ni Fast RAM ni Chip RAM. Le champ est distinct des flags DATA/Fast demandés dans le fichier ABK sur disque. La position mémoire effective reste à vérifier séparément, éventuellement par `TypeOfMem` et la carte WinUAE.

## Correctif minimal R46, historique gelé

- [Émetteur CPU](../tools/m16_image_draw_r45_emit.py) : option explicite `accept_loaded_flags_zero=True` **réservée à R46**. Les flags natifs **0, 1 et 3** sont acceptés ; 2, 4, 5, 6, 7, etc. restent refusés. Le comportement par défaut et les octets R45 sont préservés.
- [Builder R46](../tools/build_m16_image_draw_r46.py) : reconstruit le binaire depuis l'**archive R45 défaillante figée**, en remplaçant **uniquement le segment AP20 55** ; même table de tokens, 50 commandes AP20 et 56 segments, même ABI 5 entiers.
- [Tests 68000 R46](../tools/test_m16_image_draw_r46.py) : reproduisent **R45 refuse flags 0**, vérifient **R46 accepte flags 0/1/3**, les modes opaque/masque, la profondeur 1/2/4/8, le clipping, les deux buffers, les erreurs RLE/en-tête et la protection mémoire contre les écritures illégales. **258 scénarios natifs CPU PASS**, plus export de source strict [CI Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43221899949).
- Binaire de référence R46 : **29 288 octets**, SHA256 `5214f444b3b6e0ed1b1d2a354da0b44fb44ed4cbbc4787634415308a4d099580`. L'[archive candidate](../dist/experimental/AMOSPro_AGA_M16_v0.12.1_IMAGE_DRAW_R46.Lib) et `dist/AMOSPro_AGA.Lib` doivent être rigoureusement identiques.
- **R44 v0.11.5 reste `LAST_GOOD`** : SHA256 `0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc`. La [R45 défaillante](../dist/experimental/AMOSPro_AGA_M16_v0.12.0_IMAGE_DRAW_R45.Lib) reste archivée à l'octet près avec son [ASC original en échec](../tests/failed/M16_R45_IMAGE_DRAW_01.asc). Aucune autre commande AGA ni aucun ancien test validé n'est modifié.

## Essai Gate B R46 attendu sous AMOS interprété / WinUAE

Installer [R46 actuelle](../dist/AMOSPro_AGA.Lib), avec la même [banque ABK](../tests/current/M16_AGAPIC_SAMPLE_BANK10.abk), puis importer [l'unique test courant R46](../tests/current/M16_R46_IMAGE_DRAW_01.asc) par **Project → Merge ASCII**. Ne pas oublier de **redémarrer AMOS après remplacement de la bibliothèque** et de vérifier que ce n'est pas encore R45 qui est chargée.

Visuel attendu : trois cadres en haut, mais **à l'intérieur une mosaïque de couleurs de 64×40 pixels** ; celle de gauche est opaque (avec index 0 rose visible), celles du centre et de droite montrent la mosaïque dans un disque masqué (avec quelques trous transparents). D'autres portions de l'image doivent être dessinées sur les bords gauche, droit, haut et bas.

Valeurs attendues : `OPAQUE 1 MASK 1 SHIFT 1`, `CLIP 1 1 1 1`, `BAD 0 0 0 OUT 1`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, `ERRORS 0 RESULT 1` et `CLOSE RETURNED`. Les métadonnées de la banque doivent encore afficher `NATIVE FLAGS 0`, `LEN 1852`, `NO 10`, `STREAM 196 TOTAL 1836`.

**Ne pas promouvoir R46 en `LAST_GOOD` avant confirmation visuelle et fonctionnelle sous WinUAE.** Le fait de passer la Gate A ne prouve ni les performances 68000 réelles, ni la Gate C (AMOS Compiler), ni la Gate D (Amiga AGA physique).
