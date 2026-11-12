# Benchmark Copy — AMOS Screen Copy vs Aga Blit Copy (M17/R57)

**Source :** [`copy_32c_r57.asc`](copy_32c_r57.asc). Programme de benchmark dans `benchmarks/`, **pas** un second test actif dans `tests/current/`. La R57 déjà validée reste [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) ; **aucune modification de la bibliothèque, de LAST_GOOD, des archives ou des tests validés**.

## Utilisation

Dans AMOS Professional : ouvrir un programme **vide**, puis **Project → Merge ASCII** avec `copy_32c_r57.asc`. Exécuter en **interprété**, puis **recompiler le même source** et lancer le nouvel exécutable pour la mesure compilée. Aucune image IFF ni banque ABK n'est nécessaire. AMCAF v1.40+ est utilisé **uniquement pour `Blitter Wait`**, comme dans le benchmark V2 déjà validé.

Le programme garde les résultats affichés par `Do / Wait Vbl / Loop` : **pas de `Wait Key`**. Une capture de l'écran suffit pour relever les trios de ticks.

## Instructions comparées

```amos
Screen Copy 0,_SX,_SY,_SX2,_SY2 To 0,_DX,_DY
_OK=Aga Blit Copy(_SX,_SY,_DX,_DY,_W,_H)
```

**Point impératif :** `Screen Copy` utilise les bornes **de fin exclusives** : `_SX2=_SX+_W`, `_SY2=_SY+_H`. À ne pas confondre avec `Bar`, dont la borne finale est inclusive. AGA reçoit directement largeur et hauteur. Les deux commandes copient un rectangle sur le **même écran/bitmap** : AMOS sur écran 0 ; AGA sur son back buffer privé. `Screen Copy` utilise son mode REPLACE par défaut (minterm `$C0`, comme la Copy AGA).

## Charges, identiques pour A et G

| Cas | Source | Destination | Largeur × hauteur | Appels par passage |
|---|---|---|---|---:|
| ALIGNED | (16,24) | (176,24) | 64 × 48 | 1 200 |
| UNALIGNED | (13,32) | (197,43) | 95 × 72 | 900 |
| LARGE | (8,8) | (64,136) | 200 × 112 | 500 |
| OVERLAP | (40,40) | (56,56) | 128 × 96 | 700 |

Mode **PAL 320×256×32 couleurs = 5 bitplanes**, trois passages par test et par moteur. Les motifs sources sont identiques : fond noir 0, rectangle blanc 31, intérieur rouge 7. Ils sont initialisés **en dehors** du chronomètre, de même que les effacements, validations Safe, ouverture/fermeture, affichage et `Swap`.

`Timer` AMOS : **1 tick = 20 ms**. Le temps de la copie AMOS inclut un `Blitter Wait` final à l'intérieur de la mesure ; la routine AGA réalise son `WaitBlit` dans chaque appel. Pas de `Wait Vbl` dans les boucles chronométrées. Le benchmark affiche **3 valeurs brutes** par opération et par moteur : comparer leurs **médianes**.

## Précautions d'interprétation

Les données mesurent la **durée observable des instructions depuis AMOS**, pas un comparatif parfaitement isolé du matériel : `Screen Copy` opère sur l'écran AMOS natif, `Aga Blit Copy` sur le back buffer privé AGA, et les coûts d'appel/synchronisation peuvent différer. Le cas OVERLAP vérifie la performance en recouvrement, pas à lui seul la fidélité pixel par pixel.

`AGA ERR 0` signifie que **le dernier appel de chacune des 12 séries chronométrées** a réussi ; les milliers de retours intermédiaires ne sont pas décomptés, pour éviter un surcoût de contrôle côté AGA uniquement. En cas de refus Safe ou d'échec de préparation, le benchmark affiche une erreur et **ne doit pas être utilisé pour conclure**. Si les ticks sont trop faibles, le nombre d'appels peut être augmenté pour les deux méthodes à l'identique.

**Statut :** préparation du code et contrôle statique des dimensions, bornes et cas de recouvrement ; **non exécuté sous WinUAE** à ce stade. Les Gates A/B/C de R57 restent acquises sur le test fonctionnel précédent.

Références : [manuel AMOS Screen Copy](https://amospromanual.dev/06-02-using-screens.html) · [manuel AMCAF Blitter Wait](https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMCAFguide/manual/graphicblitter.html) · [benchmark R57 précédent](RESULTATS_32C_R57_COMPILER_2026-11-12.md).
