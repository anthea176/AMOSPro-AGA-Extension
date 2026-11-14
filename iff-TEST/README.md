# Images IFF de test

Ce dossier contient des images de démonstration AGA ainsi que des **dessins ou scans de dessins personnels de HWARF**, utilisés pour les essais.

Les mires `AGA_TESTCARD_320x256_256C.iff` et `AGA_DEMO_320x256_256c.iff` permettent d'essayer un écran indexé PAL LoRes **320×256, 8 bitplanes, 256 couleurs** ; voir également `AGA_TEST_MODES/` pour les autres modes.

## Compagnon chunky C2P (R79)

Le fichier [`AGA_DEMO_320x256_256c.chk`](AGA_DEMO_320x256_256c.chk) est la **conversion hors ligne 8 bits chunky, 81 920 octets** du **même** [`AGA_DEMO_320x256_256c.iff`](AGA_DEMO_320x256_256c.iff). Le nom de base est identique ; seul le suffixe passe de `.iff` à `.chk`. L'IFF original n'a pas été modifié.

Cette paire est requise par le [programme de démonstration intégré C2P IFF](../examples/c2p_iff_showcase/README.fr.md) : écran IFF d'origine, rendu C2P de référence, Blit, Zoom, clipping, Close/ReOpen et contrôles de pixels. Le chargement avec `Bload` exige un fichier brut de **taille exactement 81 920 octets**, vérifiée avant l'écriture dans les banques 12 et 13. Le script [`tools/test_c2p_iff_showcase.py`](../tools/test_c2p_iff_showcase.py) compare les octets chunky au décodage strict du `BODY` ByteRun1 et contrôle l'image PNG [attendue](../examples/c2p_iff_showcase/EXPECTED_C2P_SHOWCASE.png). Le compagnon chunky **est une œuvre dérivée de l'IFF** : mêmes droits graphiques, **pas de licence MIT automatique**.

Les fichiers externes issus d'Aminet, `Amiga fallout.iff`, `Clown.iff`, `Clown_RAW.iff` et `harrison.iff` ne sont plus distribués ici. Les comptes rendus des anciens essais peuvent encore les mentionner : ces références sont historiques.

Certains de ces dessins sont des **fan arts d'époque réalisés à la main par HWARF**, puis scannés. Le travail graphique personnel appartient à son auteur dans la limite des droits applicables, tandis que **les personnages et univers représentés appartiennent à leurs ayants droit**. Il ne s'agit pas d'œuvres officielles, et aucune autorisation de réutilisation des personnages ou des dessins n'est accordée ici.

**© 2026 HWARF — Tous droits réservés sur ses créations originales.** Ces images ne sont **pas** sous licence MIT et ne peuvent pas être librement réutilisées ni redistribuées. Les éventuels personnages ou univers de tiers restent la propriété de leurs ayants droit.

Voir la [licence des éléments graphiques](../ASSETS_LICENSE.md).
