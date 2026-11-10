# M7 / R18 0.8.2 — Copper Wait / Move / End : premier raster

**Statut : R18 PASS pour le scénario raster sous AMOS interprété/WinUAE le 10/11/2026 — Gate A CPU 68000 PASS (26 scénarios), CI complète PASS** (#42870412601 (archive CI privée)) ; **Gate B AMOS/WinUAE : PASS sur les deux captures (raster et console).** Ne pas extrapoler ce résultat à l'AMOS Compiler ni au matériel physique. Le périmètre est celui de la première démonstration raster **RGB4 12 bits, COLOR00 à COLOR31**, sans accès arbitraire aux registres matériels.

## Fichiers et référence exacte

| Élément | Fichier / valeur |
|---|---|
| Bibliothèque candidate | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **R18 0.8.2**, 11 480 octets |
| Archive bit à bit identique | [`dist/experimental/AMOSPro_AGA_M7_v0.8.2_COPPER_RASTER_R18.Lib`](../dist/experimental/AMOSPro_AGA_M7_v0.8.2_COPPER_RASTER_R18.Lib) |
| Empreinte SHA256 | `600b8c2c38486004adef8c0e7924df877f7dd7829e1c622a89bbdc0db9f9808a` |
| Base **R17 validée WinUAE 3/3** | `dist/experimental/AMOSPro_AGA_M7_v0.8.1_COPPER_ON_OFF_R17.Lib`, SHA256 `cfd73961d6cf75a6c57ed529b2bacc11908cd96a0aad615e325597d5bfb0a02a` |
| Binaire global LAST_GOOD | R10 0.6.1, **protégé et inchangé** |
| Builder reproductible | [`tools/build_m7_copper_raster_r18.py`](../tools/build_m7_copper_raster_r18.py) |
| Contrôle CPU | [`tools/test_m7_copper_raster_r18.py`](../tools/test_m7_copper_raster_r18.py) |
| **Test AMOS validé** | [`tests/passed/M7_R18_COPPER_RASTER_01.asc`](../tests/passed/M7_R18_COPPER_RASTER_01.asc) (correction de syntaxe documentée ; `tests/current/` vide) |

La génération doit rester reproductible depuis la **R17 archivée**, et aucun ancien binaire ni archive de test déjà validée ne doit être écrasé.

## API disponible sur le candidat R18

```amos
_OK=Aga Copper Clear
_OK=Aga Copper Wait(40,0)
_OK=Aga Copper Move($180,$F00)
_OK=Aga Copper Wait(128,0)
_OK=Aga Copper Move($180,$00F)
_OK=Aga Copper End
_OK=Aga Copper On
' Affichage / Aga Swap / Aga Wait Key
_OK=Aga Copper Off
```

Toutes ces fonctions retournent **1** pour succès, **0** pour rejet/échec. Elles sont des **fonctions entières** et non des instructions graphiques AMOS natives :

- **Clear** : initialise une liste Copper propre sur l'écran Intuition privé, avec un `CEND` terminal. R18 accroît la capacité intermédiaire `CINIT` de **2 à 64 emplacements** ; un second `Clear` immédiat est idempotent tant que la liste n'a pas été activée.
- **Wait(v,h)** : valeurs entières `0 ≤ v ≤ 255`, `0 ≤ h ≤ 222`, coordonnées relatives au haut du ViewPort. Les WAIT successifs doivent être **strictement croissants** (comparaison lexicographique vertical/horizontal). Les positions invalides et les retours en arrière sont rejetés.
- **Move(register,value)** : seuls les registres couleur matériels pairs **`$180,$182,…,$1BE`** sont acceptés, avec `$000 ≤ value ≤ $FFF` (RGB4). La routine transmet le pointeur matériel `$DFF000 + register` à `graphics.library/CMove`. **BPLCON3, FMODE, DMA, bitplane pointers et autres registres sont interdits.**
- **End** : finalise le plan déjà `CEND`-terminé, uniquement s'il contient au moins une vraie instruction et s'il n'a pas déjà été finalisé. Un second `End` retourne 0.
- **On** : n'autorise pas la liste contenant des instructions raster si `End` n'a pas réussi ; appelle `MakeScreen` et `RethinkDisplay` par Intuition, puis empêche toute modification de la liste active.
- **Off** : détache, reconstruit l'affichage, synchronise et libère seulement les allocations possédées par l'extension. Les appels répétés `Off` restent acceptés.

**Capacité conservatrice du premier raster :** au plus **62 instructions utiles + CEND**, avec un emplacement supplémentaire conservé en réserve. Refuser une insertion avant un dépassement, ne jamais compter sur une réallocation automatique de `CopList`.

## Stratégie mémoire / état

Le `UCopList` reste un bloc **12 octets**, comme en R16/R17. R18 utilise **deux bits d'état dans le champ privé `Screen.UserData`** (pointeur au moins aligné sur 4 octets), et compare uniquement sa partie pointeur avec `ViewPort.UCopIns` :

- Bit 0 : liste activée, y compris si le système a échoué pendant la reconstruction (retrait `Off` requis).
- Bit 1 : plan finalisé par `End`, donc non modifiable.
- Les deux bits à zéro identifient la liste initiale/en préparation.
- Les instructions `Wait` et `Move` rejettent les listes scellées ou activées ; aucun autre endroit du programme ne doit considérer `Screen.UserData` comme un pointeur brut sans le masque `$FFFFFFFC`.

**Delta volontaire et justifié vis-à-vis de R17 :** les anciennes entrées AP20 **0 à 21 restent octet pour octet identiques**. L'entrée **22 `Copper Clear`** change exclusivement l'immédiat `CINIT(2)` en `CINIT(64)`. Les entrées **23 `On`** et **24 `Off`** sont adaptées au suivi des états et au rejet des listes non terminées ; les nouvelles entrées **25, 26 et 27** implémentent `Wait`, `Move` et `End`. Ce delta est contrôlé par la CI et ne modifie pas les archives R16/R17 validées.

Le `CopList` intermédiaire provient de `graphics.library` ; ses offsets utilisés sont confirmés dans `graphics/copper.h` : `CopIns=+12`, `CopPtr=+16`, `Count=+28`, `MaxCount=+30`. Pour ajouter un `Wait` ou `Move`, R18 vérifie la dernière instruction `CEND`, rembobine un seul `CopIns` de **6 octets**, appelle `CWait` ou `CMove` puis `CBump`, et réinsère `CEND` avant de retourner à AMOS. **Le code ne modifie pas la liste une fois activée.** Les demandes invalides ne modifient pas l'état du CopList.

Les paramètres AMOS suivent la convention du dépôt : sur une fonction à deux arguments, **D3 est le deuxième**, et le premier est lu dans `(A3)+` (**A3 avance de 4 octets même lors d'un rejet**). Le résultat entier est placé en D3, D2 vaut 0 ; SP reste équilibrée et les registres ordinaires sont conservés.

**Attention :** ce code utilise les structures intermédiaires NDK sous la responsabilité de `graphics.library` ; seuls les tests sous WinUAE, puis vrai Amiga, peuvent qualifier le résultat visuel, les interactions avec la palette et le cycle DMA. Le test CPU ne mesure pas les fuites ni les transferts Copper matériels.

## Test unique AMOS/WinUAE

1. Test effectué sous AMOS Professional interprété/WinUAE avec **R18** et `MYGIRL.IFF 320×256×8`. Programme archivé : [`M7_R18_COPPER_RASTER_01.asc`](../tests/passed/M7_R18_COPPER_RASTER_01.asc).
2. Le premier écran doit montrer un effet **raster horizontal rouge / vert / bleu** dans les zones de couleur index 0. **Faire une capture de cet affichage** avant d'appuyer sur une touche. L'image IFF doit rester reconnaissable.
3. Après une touche, `Off`, `Close`, `Reopen`, `Clear/On/Off` et seconde fermeture, le programme doit revenir normalement à AMOS.

**Retour numérique attendu :** `W1=W2=W3=W4=M1=M2=M3=M4=END=ON=SWAP=OFF=OFF2=REOPEN=CLEAR2=ON2=OFF3=1`; `BADREG=BADRGB=BADWAIT=END2=AFTER=0`; `KEY ... CLOSE X2 RETURNED`. Ces résultats numériques ne remplacent **pas** la capture de l'effet.

**Gate A : PASS.** CPU 68000 **26 scénarios réussis** (CI préparatoire (archive CI privée, run #42869523014)) ; HUNK/AP20, SHA, builder reproductible, tests ILBM et non-régression M5/M6/R16/R17 **PASS** (CI complète #42870412601 (archive CI privée)). **Gate B WinUAE : PASS (une exécution observée). Gate C Compiler et Gate D matériel : NON TESTÉES.**

## Résultat utilisateur et correction de syntaxe

Deux captures du 10/11/2026 confirment les **bandes raster rouges, vertes et bleues** (index 0, image IFF conservée mais certains pixels COLOR00 recolorés), puis les retours attendus : `W/M=1`, `BADREG/RGB/WAIT=0`, `END=1 END2=0 AFTER=0`, `ON/SWAP/OFF/OFF2/REOPEN/CLEAR2/ON2/OFF3=1`, `KEY 68`, `CLOSE X2 RETURNED`, fin AMOS **ligne 95**. La commande isolée `Aga Copper Off` du chemin d'échec dans le test de dépôt provoquait initialement une erreur de syntaxe AMOS ; l'utilisateur l'a remplacée localement par une affectation `X=Aga Copper Off`. L'archive corrige cette même ligne. **Le contenu octet pour octet du fichier local exécuté n'a pas été fourni**, mais les captures attestent son comportement. Une vérification statique de la syntaxe des appels Copper a été ajoutée à la CI.

## Suite

Le **noyau Copper M7 RGB4 est validé dans le périmètre des tests WinUAE R16–R18**. Conserver R18 comme référence du jalon, sans promotion automatique de `LAST_GOOD`. Les fonctions avancées (24 bits et 256 entrées AGA, raster complexes), l'absence de fuites mémoire, la compilation AMOS et le matériel réel restent non validés. **Prochain chantier prévu : M8 souris**, puis zones cliquables M9 et collisions M10.

Références : [`gfxmacros.h`](https://d0.se/include/graphics/gfxmacros.h), [`copper.h`](https://d0.se/include/graphics/copper.h), [Autodoc CWAIT](https://d0.se/autodocs/graphics.library/CWAIT), [Autodoc CMOVE](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node02C6.html), [Autodoc UCopperListInit](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node02BE.html).
