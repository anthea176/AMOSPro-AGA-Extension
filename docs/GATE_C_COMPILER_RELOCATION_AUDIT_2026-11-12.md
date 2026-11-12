# Gate C AMOS Compiler — audit des appels inter-segments AP20 (12/11/2026)

**Statut : diagnostic statique uniquement, aucun nouveau PASS WinUAE.** Dépôt `anthea176/AMOSPro-AGA-Extension`, branche **`main` exclusivement**. M16 en développement. Ne modifier ni `dist/AMOSPro_AGA_LAST_GOOD.Lib` (R44), ni les archives R45/R46, ni `dist/AMOSPro_AGA.Lib` (candidate courante R46) sans validation séparée.

## Constat expérimental déjà acquis

Sur le programme compilé [R44_COMPILER_STAGE_TRACE.asc](../tests/diagnostics/R44_COMPILER_STAGE_TRACE.asc), `Aga Probe` est revenu, `Aga Screen Open` a retourné `1`, puis l'exécution s'est arrêtée avec Guru `80000004` après `05 BEFORE AGA SCREEN CLOSE`, avant `06`. Il ne faut **pas** refaire ce test inchangé pour localiser Open/Close : sa localisation est établie. Le PC exact au moment de l'instruction illégale **n'est pas connu**.

## Identité de la bibliothèque : ce qu'on sait et ce qu'on ignore

Le compte rendu précédent indique que **R45 était installée**, mais cette information reste une **déclaration**, pas un SHA de la copie effectivement utilisée par AMOS Compiler. La capture ne contient pas de numéro de version. Depuis, la bibliothèque *du dépôt* `dist/AMOSPro_AGA.Lib` est devenue R46 ; ce changement GitHub **n'installe rien** dans WinUAE.

| Binaire du dépôt | Octets | SHA256 |
|---|---:|---|
| R44 v0.11.5 `LAST_GOOD` | 27 460 | `0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc` |
| R44 candidate Gate C expérimentale | 27 576 | Candidate séparée, **non validée** |
| R45 v0.12.0 (archivée) | 29 280 | `0d780b4648214c36e8f291d9575390462d174cd8ba22cac2188324b75bd220d7` |
| R46 v0.12.1 (candidate M16 courante) | 29 288 | `5214f444b3b6e0ed1b1d2a354da0b44fb44ed4cbbc4787634415308a4d099580` |

Sur une installation `APSystem` visible depuis Windows (répertoire monté WinUAE), récupérer **taille et SHA256 de la copie réellement référencée dans la configuration AMOS** :

```powershell
Get-Item 'CHEMIN_REEL\APSystem\AMOSPro_AGA.Lib' | Select-Object Name,Length
Get-FileHash 'CHEMIN_REEL\APSystem\AMOSPro_AGA.Lib' -Algorithm SHA256
```

Sur un volume HDF non accessible comme dossier depuis Windows, utiliser dans l'AmigaShell `List APSystem/AMOSPro_AGA.Lib` depuis le répertoire AMOS (la taille suffit à départager les quatre binaires connus). Vérifier le nom/chemin de la bibliothèque et son slot dans la configuration AMOS. Un fichier présent *aujourd'hui* ne prouve **pas rétrospectivement** quel code a été incorporé dans un exécutable déjà compilé : le compilateur copie les routines nécessaires lors de la compilation.

## Audit indépendant des quatre binaires

Lecture **sans modification** des tables AP20 et des `BSR.w` alignés aux mots, avec destination reconstruite à partir des tailles et offsets de segments. R44, R45 et R46 ont la **même liste de 14 correspondances inter-segments** :

| Source | Offset local (décimal) | Destination | Offset local cible | État R44 candidate |
|---|---:|---|---:|---|
| 0 | 398 | 54 | 222 | **Remplacé par `Rbsr`** |
| 8, `Aga Screen Close` | 140 | 48, `Aga Font Select` | 378 | **Encore `BSR.w`** |
| 8, `Aga Screen Close` | 276 | 54 | 222 | **Remplacé par `Rbsr`** |
| 17, `Aga Key` | 48 | 33 (helper interne) | 538 | **Encore `BSR.w`** |
| 17 | 204 | 54 | 222 | **Remplacé par `Rbsr`** |
| 18, `Aga Wait Key` | 48 | 33 (helper interne) | 538 | **Encore `BSR.w`** |
| 18 | 204 | 54 | 222 | **Remplacé par `Rbsr`** |
| 21, `Aga Blit Clear` | 22 | 20, `Aga Blit Fill` | 0 | **Encore `BSR.w`** |
| 31, `Aga Mouse Pressed` | 42 | 33 (helper interne) | 0 | **Encore `BSR.w`** |
| 32, `Aga Mouse Released` | 42 | 33 (helper interne) | 0 | **Encore `BSR.w`** |
| 36, `Aga Text` | 370 | 48 | 350 | **Encore `BSR.w` — cible suspecte** |
| 48, `Aga Font Select` | 108 | 49, `Aga Font Bank Select` | 920 | **Encore `BSR.w`** |
| 48 | 328 | 49 | 920 | **Encore `BSR.w`** |
| 48 | 418 | 49 | 920 | **Encore `BSR.w`** |

**Prudence :** cet inventaire repère des séquences binaires `61 00` alignées, il ne constitue pas un désassemblage complet et n'affirme pas que chaque site est exécuté. L'appel 36→48 tombe à l'offset **350**, qui est au milieu des octets de `LEA d16(PC),A1` démarrant à l'offset 348 ; **ne pas le convertir automatiquement** sans étude du chemin et de l'émetteur initial.

Le correctif initial [commit 3482075](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/3482075fdfc4cac7892e54005575038db8c3a9e7) contient **six marqueurs `Rbsr`** : les quatre appels de fermeture corrigés et les deux appels au getter d'état de curseur. **Dix appels inter-segments restent visibles dans cette candidate R44**.

## Diagnostic plus précis de `Aga Screen Close`

À l'intérieur du **segment 8**, le nettoyage de fenêtre invoque d'abord le hook de curseur (appel à l'offset 276), puis le traitement de libération des ressources peut atteindre l'appel vers le segment 48 (offset 140). Autrement dit, même si le premier hook est réparé, la candidate actuelle peut encore échouer **avant le message `06`**. Le dernier Guru peut donc être déclenché par l'un ou l'autre de ces déplacements incorrects ; impossible de les départager sans le PC fautif ou une candidate couvrant les deux chemins.

`Rbsr` est bien le marqueur officiel `$FE31,index` : [`+CEqu.s`](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BCEqu.s), [manuel extension `+Music.s`](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BMusic.s) et [chargeur de routines `+APComp.s`](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BAPComp.s). **Un simple `Rbsr(48)` ne peut pas remplacer l'appel 8→48**, car sa cible est **à l'intérieur** de la routine 48, pas à son entrée. Il faut extraire une fonction auxiliaire autonome ou réécrire proprement ce chemin, puis vérifier ses dépendances vers le segment 49.

## Ordre de poursuite, sans répétition inutile

1. **Identifier la copie réellement installée** (`APSystem` + slot + SHA ou taille). Si la copie a changé depuis la compilation, noter la limite de cette vérification.
2. **Corriger la chaîne complète du Close** : 8→54, 8→48 et appels 48→49, avec helpers relogeables et stockage d'état stable ; inventorier séparément les autres appels avant une déclaration de compatibilité Compiler.
3. Faire une **transposition structurée en mémoire** R44→R45→R46 avec vérification des SHA sources, des tokens, des segments préservés et de `Aga Image Draw` (segment 55 inchangé). Les versions déjà publiées restent gelées.
4. **Une fois la nouvelle candidate contrôlée statiquement**, refaire **une seule fois** la trace compilée déjà disponible, sous WinUAE avec cette candidate identifiée précisément. Le premier critère est le retour `06 AFTER AGA SCREEN CLOSE` sans Guru. Ensuite seulement : tests ciblés souris, texte, double buffering et Image Draw, puis Gate D machine réelle.

**Aucune Gate C PASS, aucun correctif installé, aucune nouvelle version clôturée.**
