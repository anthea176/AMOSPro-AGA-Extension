> **ARCHIVE HISTORIQUE — NE PAS UTILISER COMME STATUT ACTUEL.** Ancienne architecture R10/R12 conservée pour diagnostic. Consulter [l'architecture actuelle](../ARCHITECTURE.md), la [roadmap](../ROADMAP.md) et le [statut M7](../M7_STATUS.md).

# AMOSPro-AGA-Extension — Architecture technique

## PRIORITÉ ACTIVE — R12 0.6.3, erreur de registre NewScreen sur le repli PAL (10/11/2026)

**Échec du test précédent :** déplacer `Amos To Back` avant `Aga Screen Open` sous R10 ne change **strictement rien** au placement trop bas de Jeff. Hypothèse éliminée, test archivé `tests/historical/R10_JEFF_AMOS_BACK_BEFORE_OPEN.asc`.

**Erreur concrète trouvée dans R10 :** lors du second `OpenScreenTagList` (repli NTSC → PAL), le helper restaure A1 (TagList) mais pas A0 (NewScreen). Le premier appel initialise pourtant A0 à NULL ; le second peut hériter d'une valeur volatile après les appels système. R12 ajoute uniquement `SUBA.L A0,A0` (`91C8`) juste avant cet appel, avec les trois branchements internes correctement relocalisés. Les **18 autres segments AP20 sont identiques à R10** ; le loader ILBM, les dimensions, palettes, DB, Swap, clavier, fermeture et gestion du mode restent inchangés. Le lien avec la position verticale Jeff demeure une **hypothèse à vérifier au runtime**, bien que l'erreur ABI soit établie par les sources et la documentation officielle Intuition.

**Binaire actif :** `dist/AMOSPro_AGA.Lib` = R12 0.6.3, **8856 octets**, SHA256 `b4b06bedb955a23dc048ead7f2ecac8bab955591c6bcc094d4d6e6c4bad4eaec` ; archive `dist/experimental/AMOSPro_AGA_M5_v0.6.3_NEWSCREEN_A0_R12.Lib`. **`dist/AMOSPro_AGA_LAST_GOOD.Lib` RESTE R10 0.6.1** (SHA256 `e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3`), tel que demandé explicitement. M4b historique et R11 rejetée restent archivés.

**Test unique :** `tests/current/R12_JEFF_A0_RETRY.asc`, bandeau `R12-JEFF-NEWSCREEN-A0-01` : d'abord Jeff-Flag 736×482, vérifier position directe en haut + retour AMOS ; si PASS, Fallout PAL avec le même test. Ce programme conserve l'ordre `Amos To Back` du test R10 qui chargeait les images.

**Tests :** contrôle binaire statique effectué ; test CPU Unicorn strict sur `A0=NULL` ajouté au workflow, mais **pas encore exécuté/confirmé** ; WinUAE/AMOS Compiler R12 non testés. `tools/verify_artifacts.py` a été adapté ; les anciens builders R9/R10/R11 n'écrasent plus la Lib active.

Voir `docs/R12_NEWSCREEN_A0.md` et `tests/README.md`. Même branche `codex/intuition-input-r1`, PR #4 Draft, **`main` inchangée**. Ne pas promouvoir R12 dans LAST_GOOD avant validation.

---

## Vérification en cours — ordre AMOS To Back / écran R10 (10/11/2026)

**La R10 active et LAST_GOOD restent intactes.** Un seul test diagnostique (`tests/current/R10_JEFF_AMOS_BACK_BEFORE_OPEN.asc`, bandeau `R10-JEFF-AMOS-BACK-ORDER-01`) déplace `Amos To Back` de l'après-Swap vers **avant `Aga Screen Open`**, avec restauration `Amos To Front` sur échec d'ouverture. Aucun autre changement de logique AGA.

Ce test vise le défaut de position de Jeff observé sur R10 ; le fonctionnement correct **n'est pas encore validé** avec cet ordre. Source AMOS `+W.s` : `TAMOSWb` rend la main au Copper/Workbench. Les Autodocs indiquent déjà `SA_Top=0` par défaut si `SA_Height` est explicite : ajout de tag `SA_Top=0` non justifié. **Ne pas recréer R11** ni modifier le loader. Voir `docs/R10_AMOS_BACK_ORDER.md`.

---

## ÉTAT ACTUEL : R10 restaurée, LAST_GOOD R10, R11 rejetée (10/11/2026)

**R11 0.6.2 REJETÉE sous WinUAE :** l'utilisateur obtient un écran gris au lieu de l'image Jeff. Le débogueur affiche PC `$00F81472`, instruction ROM `STOP #$2000` en mode superviseur. Ce relevé n'établit pas la cause exacte : il ne démontre ni gel CPU ni défaut du loader. La régression graphique par rapport à R10 est en revanche confirmée. La R11 reste conservée dans `dist/experimental/AMOSPro_AGA_M5_v0.6.2_JEFF_POSITION_R11.Lib` et le test de cet échec dans `tests/historical/R11_JEFF_SCREEN_POSITION.asc`.

**Retour à la version fonctionnelle R10 0.6.1** : `dist/AMOSPro_AGA.Lib` = l'archive `dist/experimental/AMOSPro_AGA_M5_v0.6.1_NTSC_PAL_R10.Lib`. Taille **8 852 octets**, SHA256 `e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3`. R10 ouvre et charge Jeff-Flag avec repli NTSC→PAL ; les fonctions DB, Swap, clavier et fermeture fonctionnent selon l'utilisateur. **Limite connue : écran Jeff placé trop bas, repositionnable à la souris.** R9 reste validée 4/4 sur Fallout interprété et en AMOS Compiler selon le retour utilisateur.

**Exception demandée explicitement par l'utilisateur :** `dist/AMOSPro_AGA_LAST_GOOD.Lib` est également remplacé par la **copie binaire identique de R10**. Le LAST_GOOD historique M4b est déjà archivé sans perte à `archive/AMOSPro_AGA_M4b_v0.0.9_R6C_R1_WinUAE_OK.Lib` (même blob Git que l'ancien LAST_GOOD). **R10 est la dernière version M5 fonctionnelle connue, mais le défaut de positionnement et des gates non validés subsistent** : ne pas l'appeler un jalon parfaitement finalisé.

**Reprise :** analyser le cycle de vie de Screen/Window à partir de **R10**, sans modifier les fonctions IFF déjà validées et sans reproduire le helper R11 qui provoque l'écran gris. Aucun nouveau binaire ni test actif créé pour ce retour. `tools/verify_artifacts.py` et le builder historique R11 doivent respecter cette nouvelle référence.

Branche existante `codex/intuition-input-r1` ; PR #4 Draft, **main inchangée**, aucun merge.

---



## Checkpoint R9 0.6.0 — 4/4 PASS WinUAE interprété (10/11/2026)

**Candidat actif :** `dist/AMOSPro_AGA.Lib` = **R9 0.6.0**, 8 772 octets, SHA-256 `58312880cf4096170b1361232d298e8b54f762219d22a0e5c83d41d3f1177e7c`. Identique à `dist/experimental/AMOSPro_AGA_M5_v0.6.0_PICINFO_A3_R9.Lib`; R8 conservée dans `dist/experimental/`, `LAST_GOOD` inchangé.

**Runtime utilisateur :** le 10/11/2026, **4 exécutions successives sans problème** du programme identifié par le bandeau `R9-A3-REGRESSION-01`, avec `Fallout.iff` 640 × 512, 4 plans, compression ByteRun1. Capture : `OPEN=1`, `DB=1`, `LOAD=1`, `SWAP=1`, `KEY=68`, `CLOSE RETURNED`, puis boîte de dialogue AMOS `End of program at line 68`. **Gate B (ce scénario interprété) : PASS 4/4.** Ceci appuie la correction A3, sans démontrer la stabilité de tous les formats ou la qualité pixel à pixel.

**Archivage :** test exact `tests/passed/R9_PICINFO_A3_REGRESSION.asc` (SHA GitHub conservé), aucun `.asc` restant dans `tests/current/`. Le fichier n'a pas été retouché depuis le PASS.

**Restent ouverts :** Gate A — tests CPU Unicorn/CI R9 non confirmés ; Gate C — version compilée ; Gate D — vrai Amiga AGA ; Ctrl+C en cours de Swap et stress multi-IFF hors validation. **Ne pas merger la PR #4 (Draft)** et ne pas promouvoir `LAST_GOOD` avant les gates requis. Même branche `codex/intuition-input-r1`, sans nouvelle branche.

Les autres sections de ce document sont historiques lorsque leurs anciens statuts « candidat courant » ou « non testé » contredisent ce checkpoint. Voir `docs/PICINFO_A3_R9.md` et `tests/README.md`.


Implémentation expérimentale actuelle : [Generic ILBM R1](../GENERIC_ILBM.md).
Le contexte IFF est temporaire, sans changement de l'état extension partagé.
PicInfo conserve 0..5 et ajoute 6=ModeID utilisable, 7=capacité écran `2^depth`.
Le loader effectue une passe de validation complète du BODY avant toute écriture.

## Objectif

Construire une extension AGA durable pour AMOS Professional 365, utilisable en interprété et compilé, sur WinUAE et vrai Amiga AGA.

Le principe directeur est simple :

> fournir une API AMOS de haut niveau qui cache la plomberie AGA, sans devenir un nouveau moteur de jeu.

## 1. Couche ABI AMOS 365

Cette couche est la fondation et ne doit plus être modifiée au hasard.

Règles établies :

- extension AP20/HUNK ;
- table de tokens AMOS -> entrées bibliothèque ;
- données privées accessibles via l'état d'extension ;
- fonctions entières : résultat dans D3, D2=0 pour le type entier ;
- préserver les registres non documentés par l'ABI ;
- aucun blocage dans WaitPort / Exec Wait ;
- noms de commandes choisis pour éviter les ambiguïtés du parseur AMOS ;
- chaque nouvelle commande doit être vérifiée en interprété ET compilé.

Avant toute nouvelle API, vérifier :
1. signature token ;
2. ordre des paramètres ;
3. type de retour ;
4. compatibilité compilateur AMOS ;
5. absence de collision de nom avec les commandes existantes.

## 2. État runtime partagé

L'extension doit posséder un état central unique et versionné.

État minimum actuel :

- Screen* ;
- IntuitionBase ;
- GfxBase ;
- largeur / hauteur ;
- nombre de couleurs ;
- ModeID ;
- profondeur ;
- état double buffer.

À terme, ajouter explicitement :

- version de la structure d'état ;
- flags runtime ;
- mode vidéo courant ;
- profondeur réelle ;
- palette active ;
- pointeurs front/back ;
- capacités chipset détectées ;
- erreurs du dernier appel si une API de diagnostic stable est ajoutée.

Aucune commande ne doit stocker un état privé caché ailleurs.

## 3. Gestion écran AGA

API actuelle :

- Aga Screen Open
- Aga Screen Close
- Aga Wait Vbl
- Aga Double Buffer
- Aga Swap
- Aga Back Fill

Règles :

- utiliser Intuition / graphics.library pour les écrans standards ;
- utiliser SA_FullPalette pour les écrans indexed AGA qui nécessitent 256 couleurs ;
- éviter toute reconfiguration sauvage du ViewPort après ouverture ;
- conserver un cycle Open -> Draw -> Swap -> Close déterministe ;
- toujours libérer dans l'ordre inverse des allocations.

### Règle de test AMOS

Les tests visuels doivent gérer explicitement :

```amos
Amos To Front
...
Amos To Back
...
Amos To Front
```

Une mauvaise gestion Front/Back invalide toute conclusion visuelle sur palette ou affichage.

## 4. Service IFF / ILBM

Le loader IFF ne doit plus être un bloc monolithique.

Il est découpé conceptuellement en quatre fonctions internes :

1. **Inspect**
   - FORM / ILBM ;
   - BMHD ;
   - CMAP ;
   - CAMG ;
   - renvoie les métadonnées sans décoder BODY.

2. **Validate**
   - dimensions ;
   - profondeur ;
   - compression ;
   - rowBytes ;
   - tailles de chunks ;
   - compatibilité avec l'écran courant.

3. **Decode**
   - compression 0 ;
   - ByteRun1 ;
   - ligne par ligne ;
   - plan par plan ;
   - bornes strictes.

4. **Apply**
   - palette ;
   - bitplanes ;
   - nettoyage des plans inutilisés ;
   - synchronisation affichage.

### API publique prévue

```amos
_V=Aga Pic Info("image.iff",field)
_OK=Aga Iff Load("image.iff")
```

Aga Pic Info :

- 0 = largeur ;
- 1 = hauteur ;
- 2 = bitplanes ;
- 3 = couleurs CMAP ;
- 4 = compression ;
- 5 = CAMG / ModeID ;
- -1 = fichier invalide / non lisible.

## 5. Abstraction des modes vidéo

Ne pas faire dépendre les utilisateurs AMOS de FMODE/BPLCONx/DDF/DIW.

Créer une logique interne qui transforme :

- largeur ;
- hauteur ;
- profondeur ;
- CAMG ;
- flags HAM/EHB/interlace/hires ;

en configuration AmigaOS / AGA valide.

Ordre :

1. indexed LowRes ;
2. indexed HiRes ;
3. interlace ;
4. EHB ;
5. HAM6 ;
6. HAM8 ;
7. overscan / formats atypiques.

## 6. Palette AGA

API de haut niveau prévue :

```amos
Aga Set Colour index,r,g,b
```

Contraintes :

- index 0..255 ;
- RGB 0..255 ;
- cacher complètement banque AGA + LOCT ;
- rester compatible avec SetRGB32 / LoadRGB32 lorsque possible.

Le hardware AGA 24 bits reste une référence de comportement, mais l'API publique ne doit pas exposer les registres BPLCON3 nécessaires à son implémentation.

## 7. Blitter

Après stabilisation M5 :

API cible minimale :

```text
Aga Blit Copy
Aga Blit Fill
Aga Blit Clear
```

Le Blitter doit être utilisé pour les opérations où il apporte un gain réel.

Validation obligatoire :

- logique ;
- masques ;
- shifts ;
- modulos ;
- overlap ;
- descending ;
- vrai AGA / WinUAE pour les performances.

Ne jamais utiliser Alice68 comme référence de timing Blitter.

## 8. Copper

**M7 en préparation :** architecture de listes utilisateur `UCopList` rattachées au `ViewPort` Intuition, sans remplacement direct de `COP1LC`/`COP2LC`. La propriété mémoire, la dépose sûre et le cleanup lors de `Aga Screen Close` sont des prérequis à R16. Voir [M7_COPPER_DESIGN.md](../M7_COPPER_DESIGN.md). **Aucune commande Copper exécutable n'est encore livrée.**

Couche future :

```text
Aga Copper Clear
Aga Copper Move
Aga Copper Wait
Aga Copper End
Aga Copper On
Aga Copper Off
```

Cas d'usage :

- effets raster ;
- split-screen ;
- palette par ligne ;
- scrolling ;
- changement de pointeurs bitplanes.

Cette couche vient après le loader, les écrans et le Blitter de base.

## 9. Sprites AGA

Couche future :

```text
Aga Sprite Width
Aga Sprite
Aga Sprite Off
Aga Sprite Attach
```

Objectifs :

- 8 sprites matériels ;
- largeur 16 / 32 / 64 ;
- sprites attachés ;
- gestion des palettes ;
- priorité playfield/sprites.

## 10. Fonctions avancées

Après les couches fondamentales :

- scrolling matériel ;
- Dual Playfield ;
- sprites attachés avancés ;
- EHB ;
- HAM6 ;
- HAM8 ;
- SuperHiRes si pertinent.

## 11. Politique de validation

Chaque nouvelle fonction passe quatre portes :

### A. Validation statique
- structure AP20 ;
- jump table ;
- tokens ;
- tailles ;
- SHA256 ;
- absence de corruption des fonctions précédentes.

### B. WinUAE interprété
- syntaxe ;
- retour ;
- affichage ;
- cleanup ;
- répétitions.

### C. AMOS Compiler
- même test compilé ;
- même résultat ;
- pas de différence ABI.

### D. Matériel réel
Pour toute fonction sensible au chipset :
- A1200/A4000 ou équivalent AGA réel quand disponible.

Alice68 peut servir de référence comportementale supplémentaire, jamais de preuve unique.

## 12. Politique de builds

- `dist/AMOSPro_AGA.Lib` = candidat courant à tester ;
- `dist/AMOSPro_AGA_LAST_GOOD.Lib` = dernier build totalement validé ;
- `dist/experimental/` = candidats nommés/versionnés ;
- `archive/` = jalons clôturés.

Un LAST_GOOD ne change qu'après validation explicite.

Chaque candidat doit avoir :
- numéro de version ;
- SHA256 ;
- builder reproductible ;
- un seul test principal clair ;
- documentation du delta.

## 13. Discipline de développement

À partir de maintenant :

1. pas de nouveau diagnostic si une correction directe est possible ;
2. pas de modification simultanée de plusieurs couches sans nécessité ;
3. toujours partir du dernier candidat validé ;
4. documenter chaque hypothèse avant de toucher au binaire ;
5. ne jamais réintroduire un comportement déjà validé ;
6. tester le même scénario interprété puis compilé ;
7. conserver un test de non-régression pour chaque jalon clôturé.

## 14. Références externes

- AmigaOS includes / FD / autodocs : référence principale pour les API système ;
- documentation chipset AGA : référence matérielle ;
- WinUAE : validation et observation ;
- Alice68 / AGA-PiStorm : référence comportementale supplémentaire pour bitplanes, palette, FMODE, Copper, sprites, HAM/EHB et Blitter logique.

Le dépôt reste MIT : aucun code GPL d'Alice68/AGA-PiStorm ne doit être copié.


## Intuition Input — R1

Les écrans ouverts par `Aga Screen Open` possèdent désormais une Window Intuition dédiée à l'entrée clavier. Elle est attachée au `Screen*` AGA, couvre l'écran, est `BACKDROP|BORDERLESS|ACTIVATE|NOCAREREFRESH` et n'active que `IDCMP_RAWKEY`.

### État runtime partagé

Les offsets existants restent figés. R1 ajoute le pointeur Window à la fin de l'état :

| Offset | Champ |
|---:|---|
| +0 | `Screen*` |
| +4 | `IntuitionBase` |
| +8 | `GfxBase` |
| +12 | width |
| +16 | height |
| +20 | colors |
| +24 | ModeID |
| +28 | depth |
| +32 | `DBState*` |
| +36 | `Window*` |
| **40 bytes** | taille totale |

Aucun offset utilisé par Double Buffer, Swap, Generic ILBM R2 ou PicInfo n'est déplacé.

### Lecture clavier

- `_K=Aga Key` : poll non bloquant, `-1` si aucun key-down, sinon raw keycode `0..127`.
- `_K=Aga Wait Key` : même lecture, avec attente coopérative par `graphics.library/WaitTOF` lorsque le UserPort est vide.
- chaque message retiré par `GetMsg()` est répondu exactement une fois avec `ReplyMsg()`;
- key-up et classes non RAWKEY sont consommés/répondus puis ignorés;
- aucun `WaitPort()` et aucun Exec `Wait()`.

### Ctrl+C AMOS

Le raw keycode de C est `$33`; `IEQUALIFIER_CONTROL=$0008`. Sur RAWKEY C + Control, l'extension positionne le bit AMOS natif `BitControl=8` dans `T_Actualise(a5)` (offset graphique `-168`). AMOS reste propriétaire de la décision finale : `BREAK ON`, `BREAK OFF` et `ON BREAK` continuent donc à passer par son mécanisme normal.

La validation CPU prouve le chemin jusqu'au bit AMOS. Le critère final « retour effectif à l'éditeur AMOS » reste obligatoirement un test runtime et ne doit pas être déclaré PASS avant exécution de `tests/current/M5_INTUITION_INPUT.asc`.

### Cleanup

`Aga Screen Close` vide d'abord le UserPort avec `GetMsg/ReplyMsg`, ferme la Window Intuition, puis poursuit la fermeture du Screen et des bibliothèques dans l'ordre existant. Un échec d'`OpenWindow` ferme le Screen déjà créé, ferme les bibliothèques et remet l'état runtime à zéro.


### Correctif Ctrl+C R2

Le premier candidat R1 pouvait poser `BitControl` alors que les ressources AGA étaient encore actives. Comme AMOS interrompait ensuite le flot normal, `Aga Screen Close` n'était plus exécuté.

R2 impose donc la séquence suivante sur Ctrl+C :

`ReplyMsg -> CloseWindow -> cleanup Double Buffer -> CloseScreen -> CloseLibrary -> clear state -> BitControl AMOS`.

Le cleanup Double Buffer reprend la séquence non bloquante validée R6B-R4 : `WaitBlit`, libération des ScreenBuffers, suppression des MsgPorts et libération du DBState. Aucun `WaitPort` ni Exec `Wait` n'est introduit.

## Intuition Input R3 — correction CloseScreen (0.5.4)

R1 et R2 ont un défaut runtime confirmé : le BSR vers CloseWindow remplaçait
CLR.L DBState* dans un chemin sauté lorsque DBState*=0. CloseScreen recevait
alors un Screen qui possédait encore sa Window Intuition.

R3 accroche la fermeture au MOVEA.L DBState*(A2),A4 d'entrée, avant le test
conditionnel du DBState. Le helper vide/repond aux messages IDCMP, ferme
la Window, recharge A4, puis laisse le code original libérer le Double Buffer,
le Screen et les bibliothèques. Même correction dans le cleanup d'extension.

Le test Unicorn exécute le segment public Aga Screen Close complet avec
DBState nul/non nul et reproduit explicitement le défaut R2.

Candidat courant : dist/AMOSPro_AGA.Lib (identique à l'archive
dist/experimental/AMOSPro_AGA_M5_v0.5.4_INTUITION_INPUT_R3.Lib).
SHA256 : feb012b30b1adf89b3e0609e19e9a8e475be6fcd375b355c69f0d69b2d37a884.
Validation : 26 tests CPU PASS ; comportement AMOS/WinUAE encore à valider.
Ne pas merger sur main sans ce test runtime.


## Intuition Input R4 0.5.5 — Ctrl seul / Aga Wait Key

**Retour runtime R3 :** `Aga Screen Close` fonctionne en boucle simple.
**Problème R3 restant :** Ctrl seul génère RAWKEY `$63` (99) et
termine immédiatement `Aga Wait Key`, empêchant le test de Ctrl+C.

**R4 ne change que le segment AP20 18 :** `Aga Wait Key` ignore
Ctrl seul, répond à IDCMP et poursuit son polling coopératif.
`Aga Key` conserve son contrat brut : Ctrl peut retourner 99.
Le traitement de C+`IEQUALIFIER_CONTROL`, le cleanup R3 et la
propagation Break AMOS restent inchangés.

La modification est une branche vers un stub de 20 octets ajouté en
fin de segment 18 ; aucun déplacement des branches PC-relatives
précédentes. Segments 0–17 (dont Generic ILBM R2 et PicInfo) strictement
identiques au R3. Assertions dans le builder reproductible.

**Candidat courant :** `dist/AMOSPro_AGA.Lib`.
Archive : `dist/experimental/AMOSPro_AGA_M5_v0.5.5_INTUITION_INPUT_R4.Lib`.
Taille : 7896 octets. SHA256 :
`fbcaec00f30e6a7c03abc692225dac1f95dbbdb537353674fa6939c1087de9f2`.

Vérification locale des octets, du HUNK, de la table AP20 et des cibles
de branches : PASS. **Suite CPU Unicorn R4 et Ctrl+C runtime AMOS :
encore à valider.** Ne pas merger sur `main`.

## Intuition Input R5 — Break natif AMOS

Le R4 filtrait correctement Ctrl seul, mais `Ctrl+C` ne
produisait pas d'interruption AMOS (retour C=51). Le simple
`BitControl` ne déclenchait pas immédiatement le test AMOS.

R5 conserve les séquences d'entrée/sortie Intuition et toute la
fermeture R3. Le chemin Ctrl+C positionne `$8100` dans
`T_Actualise(a5)`, restaure les registres AP20 puis appelle la
routine publique AMOS `L_Test_PaSaut` (entrée #140) par le
pseudo-opcode AP20 `Rjsr`. La liaison est résolue par AMOS ;
`Test_Normal` passe à `Test_Force` qui applique
`Break On/Off` et les éventuels handlers.

Seules les entrées AP20 17/18 changent par rapport au R4 ;
loader Generic ILBM R2, PicInfo et Screen Close inchangés.
Validation runtime obligatoire. Détails :
[INTUITION_CTRL_C_R5.md](../INTUITION_CTRL_C_R5.md).

## Intuition Input R6 — restauration d'AMOS avant le Break

Le R5 est désormais **validé runtime pour l'interruption Ctrl+C**,
mais la vidéo reste sur Workbench. En R6, avant l'appel non-retournant
potentiel `L_Test_PaSaut`, l'extension effectue
`EcCalD AMOS_WB,1`. La référence officielle établit
`T_EcVect=-8(a5)` et `AMOS_WB=72` ; le gestionnaire
`TAMOSWb` restaure le Copper/écran AMOS et `T_AMOSHere`.

Les segments AP20 0–16 sont identiques à R5. Les segments 17/18
contiennent seulement un appel supplémentaire de 10 octets
au début de leur stub Ctrl+C ; tous les chemins normaux
restent inchangés.

**Restauration au premier plan à confirmer sous WinUAE.**
[Contrat source et tests](../INTUITION_CTRL_C_R6.md).
