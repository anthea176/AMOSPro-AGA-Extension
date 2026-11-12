# M16/P0 — Validation du conteneur AGAPIC sous AMOS/WinUAE (12/11/2026)

**Statut : PASS pour le chargement ABK et la lecture de l'en-tête AGAPIC v1.** Ce résultat valide le format de stockage sous AMOS interprété, **pas le dessin CPU** ni les Gates A/B du futur runtime R45.

## Preuve utilisateur : M16

Le programme [`M16_AGAPIC_ABK_PREVIEW_01.asc`](../tests/design/M16_AGAPIC_ABK_PREVIEW_01.asc), exécuté sous WinUAE/AMOS Professional avec le fichier [`M16_AGAPIC_SAMPLE_BANK10.abk`](../tests/current/M16_AGAPIC_SAMPLE_BANK10.abk), affiche :

```text
M16-AGAPIC-ABK-PREVIEW-01
BANK 10 BYTES 1836
MAGIC AGAPIC V 1
MASK 1 CODEC 1
W 64 H 40
DEPTH 4 GROUP 10
TABLE 32 STREAM 196
ROW0 196 END 1836
ABK FORMAT RESULT 1
10 - AGAPIC S: $40413010 L: 1836
NO IMAGE DRAW COMMAND YET
```

La banque est une enveloppe DATA **AmBk de 1 856 octets sur disque**, contenant 1 836 octets AGAPIC. Signature/version/flags/dimensions/profondeur/offsets et `Length(10)` concordent avec le fichier hôte. Le programme ne réalise **ni dessin d'image, ni mesure de décompression**, et la sortie ne démontre pas la conformité de flux arbitraires : ces cas sont couverts seulement par les tests du modèle Python.

**Nuance mémoire :** sur la capture, `S: $40413010` est l'adresse **Start** affichée par `List Bank` ; il n'y a **pas de marqueur explicite F/C**. L'adresse `$40413010` est compatible avec une région Fast dans certaines configurations WinUAE, mais ne prouve pas à elle seule son type. La banque ABK demande DATA/Fast ; la localisation effective doit être vérifiée avec la carte mémoire WinUAE ou `exec.library/TypeOfMem` lors du futur moteur natif. Ne pas déduire la mémoire physique de l'en-tête `AmBk` uniquement.

## Comparaison utilisateur : R30 / AGAPAL

Un second écran fournit le contrôle croisé du mécanisme de banques DATA natif AMOS :

```text
R30-AGAPAL-ABK-PREVIEW-01
BANK 10 PALETTES 8 BYTES 6224
HEADER AGAPAL V 1
OFFSET0 80
OFFSET7 5456
ABK SAVE/LOAD RESULT 1
10 - AGAPAL S: $4041DA88 L: 6224
END OF R30 FORMAT PREVIEW
```

Ce second test était déjà validé historiquement ; il constitue ici un comparatif de la mécanique AMOS `Save/Load`, **pas une deuxième validation du codec AGAPIC**. Les deux ressources sont bien chargées comme banques DATA 10 dans leurs essais respectifs ; l'utilisateur ne les stocke pas simultanément dans la même banque.

## Gates et état des fichiers

- **P0 — modèle hôte/CI PASS :** 432 roundtrips ABK, 1 344 rendus planaires de référence, 31 rejets d'entrées invalides ; [CI PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43214342325).
- **P0 — chargement AMOS/WinUAE PASS :** capture utilisateur du test AGAPIC, `ABK FORMAT RESULT 1` ; le test source original reste **inchangé** dans `tests/design/`, ainsi que l'ABK échantillon (**1 856 octets**, SHA256 `56443d5ed29527a21d043b845e70c545402648ef35fa590943cd62818499edaf`).
- **R45 — Gate A native 68000 NON TESTÉE ; Gate B rendu AMOS/WinUAE NON TESTÉE.** Aucun binaire ni token R45 livré.
- **R44 v0.11.5 `LAST_GOOD` préservée :** `dist/AMOSPro_AGA.Lib`, `dist/AMOSPro_AGA_LAST_GOOD.Lib` et archive R44 restent identiques (**27 460 octets**, 49 commandes AP20). Gates C Compiler et D Amiga physique non testées.

**Suite :** [contrat technique proposé pour R45](M16_R45_IMAGE_DRAW_CONTRACT.md). Priorité au dessin CPU 68000 sur le vrai back buffer AGA ; valider opaque et transparent (pixel d'index zéro **visible** avec masque actif), clipping non aligné, Safe/Swap, fermeture et intégrité mémoire avant toute promotion.
