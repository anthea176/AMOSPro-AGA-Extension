# Tests AMOS actifs

**Seul test actif :** [`M14_R38_CHIP_RAM_STRESS_01.asc`](M14_R38_CHIP_RAM_STRESS_01.asc) — **non valide sous AMOS/WinUAE**, Gate B memoire en attente. Ce test ne change aucune commande de la bibliotheque R38 promue `LAST_GOOD`.

Copier ces trois fichiers du depot dans `RAM:` de WinUAE :

- `AMCAF_FONT9.abk` (racine ou `examples/`),
- `Hwarf1252S.abk` (dans `examples/Amcaf Fonts/`),
- `Pix3M-1252L.abk` (dans `examples/Amcaf Fonts/`).

**Attention :** le test charge et remplace les banques AMOS **10, 11, 12**. Ne pas l'executer dans un programme contenant des banques precieuses non sauvegardees. Charger ce fichier par **Project -> Merge ASCII**, dans un programme vide, sous AMOS interprete avec `AMOSPro_AGA.Lib` R38 v0.11.0. AMCAF n'est pas requise a l'execution.

Le test utilise **500 selections**, chacune suivie de `Aga Text`, sans fermer l'ecran AGA. Il affiche `Chip Free` et le plus grand bloc Chip libre pour 0/100/200/300/400/500 selections, toujours avec Hwarf active aux points de comparaison. `RESULT 1` atteste seulement les appels et la fermeture. `CHIP_WARN 1` signifie une baisse de plus de 2048 octets sur le total libre : verifier la tendance avant d'attribuer une fuite a R38. En cas d'echec, relever **SWITCHES, ERR, les six mesures et CLOSE RETURNED**.

Le test fonctionnel original R38 est conserve octet pour octet dans [`tests/passed/M14_R38_FONT_BANK_01.asc`](../passed/M14_R38_FONT_BANK_01.asc), Git blob `4d847f86bfffc9d0d062c75e6bdda97a13b623bf`. Gates C Compiler et D Amiga reel toujours non testees.
