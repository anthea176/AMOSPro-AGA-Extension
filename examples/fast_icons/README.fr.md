# Fast Icon Lab — démo visuelle AMOSPro AGA

[English](README.md) | [Tous les exemples](../README.fr.md) | [Contrat Fast Icon](../../docs/M18_FICON8_CAPTURE_DESIGN.md)

Une **démo interactive autonome** pour comprendre et observer toute la chaîne des commandes `Aga F` : génération de pixels 8 bits, création de banques AMOS, remplissage de slots `FICON8`, conversion en cache Chip `FICHIP8`, re-staging, capture d'écran et affichage CPU ou Blitter.

**Fichier :** [FAST_ICON_LAB.asc](FAST_ICON_LAB.asc). **Bibliothèque requise : commandes Fast Icon introduites avec R67, présentes dans la R68 v0.13.13 promue LAST_GOOD.** L'API R67 avait passé ses Gates A/B ; **la démo publique a été confirmée fonctionnelle en interprété sous WinUAE le 13/11/2026** (sans capture ni relevé console séparé). La Gate C Compiler intégrée de R68 a été validée, **mais cette démo n'a pas été compilée séparément**.

## Ce que l'écran montre

La scène est conçue pour **320×256 pixels, 256 couleurs, PAL LowRes**. L'interface a un fond bleu nuit, cinq lignes d'icônes et quatre colonnes de rendu, des panneaux alternés et un petit curseur lumineux animé sous le titre.

| Colonne | Fonction | Effet de l'index 0 |
|---|---|---|
| **CPU T** (X109) | `Aga F Icon(12,ID,X,Y,1)` | Masqué : l'arrière-plan coloré reste visible |
| **CPU O** (X164) | `Aga F Icon(12,ID,X,Y,0)` | Opaque : l'index 0 devient noir |
| **BLIT T** (X219) | `Aga F Blit(11,ID,X,Y,1)` | Masqué via la banque en Chip RAM |
| **BLIT O** (X274) | `Aga F Blit(11,ID,X,Y,0)` | Opaque via le Blitter |

Les cinq lignes sont **CROSS** (croix rouge/verte à cadre blanc), **GEM** (cristal recoloré puis *re-stagé*), **ELIXIR** (potion), **SPARK** (étoile) et **CAPTURE** (copie de GEM prélevée directement dans le back buffer à **X31,Y45**, non aligné sur un octet). Le cadre de CROSS utilise notamment la couleur **255**, ce qui exerce les huit plans.

La ligne GEM et la ligne CAPTURE doivent être identiques. Chaque ligne doit avoir la même forme dans les quatre colonnes ; seules les zones d'index zéro deviennent noires en mode opaque.

## Installation et démarrage

1. Installer la [bibliothèque R68 promue AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA_LAST_GOOD.Lib) dans l'emplacement APSystem habituel, **sans remplacer `LAST_GOOD`**, puis redémarrer AMOS Professional.
2. Vérifier que les **banques AMOS 11, 12 et 13 sont libres**. Le code crée 12 (source `FICON8`, 8 slots) et 11 (cache `FICHIP8`, 8 slots), puis utilise Reserve As Data 13,256 pour le tampon chunky. **Cette instruction native AMOS peut écraser la banque 13** : travailler sur un programme et une session de test vierges.
3. Dans AMOS, créer un **nouveau programme vide**, puis importer [FAST_ICON_LAB.asc](FAST_ICON_LAB.asc) avec **Project → Merge ASCII**. Ne pas utiliser le Load de programme AMOS pour un fichier texte.
4. Exécuter **en interprété**. Cliquer ou appuyer sur une touche pour quitter ; arrêt automatique après **1 200 itérations**, avec gestion des refus `Safe` et `Swap` par tentatives limitées.
5. La sortie doit revenir à AMOS et afficher `ERROR 0`, `RESULT 1` puis `CLOSE RETURNED`. Les compteurs mémoire Chip/Fast affichés sont **informatifs**, pas une mesure de performance.

**Aucun fichier requis ou écrit** : pas d'IFF, pas d'ABK, pas de police externe, pas d'extension AMCAF. Les icônes sont fabriquées en RAM par des `Poke`. L'extension AGA remplace l'écran du Workbench **uniquement par son écran privé**.

## Ordre exact des commandes montrées

```amos
_OK=Aga F Icon Bank Create(12,8)    ' FICON8 : icônes sources
_OK=Aga F Chip Bank Create(11,8)    ' FICHIP8 : cache réel Chip RAM
Reserve As Data 13,256              ' 256 octets chunky : Poke ensuite

_OK=Aga F Icon Bank Put(12,1,13,0)  ' Convertir un slot
_OK=Aga F Chip Stage(12,11,1)       ' Préparer pour le Blitter

_OK=Aga F Icon(12,1,31,45,0)        ' Dessin opaque dans le back buffer
_OK=Aga F Icon Capture(12,5,31,45)  ' Capture directe vers un autre slot
_OK=Aga F Chip Stage(12,11,5)       ' Re-staging EXPLICITE du slot capturé

_OK=Aga F Icon(12,5,109,90,1)       ' CPU : transparence
_OK=Aga F Blit(11,5,219,90,1)       ' Blitter : transparence
```

Ce fragment est **pédagogique** : les positions finales de la grille sont calculées dans le programme complet et l'écran doit être ouvert avant les appels graphiques. On ne peut pas faire du Blitter directement sur la Fast RAM : déplacer une banque `FICON8` en Chip ne transforme pas son **format** en `FICHIP8`.

Le code vérifie en outre que la capture contient exactement **288 octets** identiques au slot GEM, y compris son masque et ses huit plans. **Une modification de `FICON8` ne rafraîchit jamais automatiquement `FICHIP8`** : rappeler `Aga F Chip Stage` après Put ou Capture.

## Résultat et limites

- BANK PUT 4 / 4 et INITIAL CHIP STAGES 4 / 4 attendus ; GEM REPUT / RESTAGE 1 1 ; CAPTURE X31 / EQ288 / STAGE 1 1 1.
- `ERROR 0` et `RESULT 1` signifient que les fonctions contrôlées ont réussi lors de l'exécution de cette démo. **L'auteur confirme le bon fonctionnement de la démo en interprété sous WinUAE**, sans capture ni relevé chiffré. Cette confirmation ne constitue **pas une validation Compiler de cette démo**. La Gate C intégrée de R68 a déjà été validée séparément.
- Les formes sont générées par code : **aucun art externe et aucune licence graphique distincte**. Sources sous [MIT](../../LICENSE).
- Aucun benchmark de vitesse CPU/Blitter n'est réalisé ici. La fluidité varie selon le CPU, la Chip RAM et les réglages WinUAE. La démo n'effectue pas de sauvegarde ABK : voir [la validation R67](../../docs/M18_R67_FICON8_CAPTURE_WINUAE_GATE_B_2026-11-13.md) pour le test Save/Erase/Load d'une banque remplie.
