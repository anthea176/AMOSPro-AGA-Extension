# M5 R9 0.6.0 — PicInfo restaure A3 par erreur

## Checkpoint actif R10 0.6.1 — compatibilité modes Jeff (10/11/2026)

**R9 0.6.0 :** Fallout 640×512×4, **4/4 PASS interprété WinUAE** et **PASS AMOS Compiler rapporté par l'utilisateur** pour le scénario complet. Ces validations restent attachées à R9 et son test archivé `tests/passed/R9_PICINFO_A3_REGRESSION.asc`. Pour Jeff-Flag, R9 a renvoyé `OPEN=0` et terminé proprement sans exécuter le loader. R9 est préservée comme repli `dist/experimental/AMOSPro_AGA_M5_v0.6.0_PICINFO_A3_R9.Lib`.

**R10 candidate active, non validée WinUAE :** `dist/AMOSPro_AGA.Lib` et archive `dist/experimental/AMOSPro_AGA_M5_v0.6.1_NTSC_PAL_R10.Lib`, 8 852 octets, SHA256 `e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3`. **Seul segment AP20 #6 (`Aga Screen Open`) modifié**, avec BSR local remplaçant l'appel OpenScreenTagList et helper de 80 octets. D'abord l'ouverture originale ; si échec sur ModeID NTSC étendu, `ModeNotAvailable` contrôle l'équivalent PAL, puis réessai **avec mêmes largeur/hauteur/profondeur**, sans couper l'image. Si le mode ou le réessai échoue, `OPEN=0` comme R9. `STATE_MODE` conserve le ModeID **logique demandé**, car `Aga Iff Load` doit comparer au CAMG du fichier. Le ModeID physique réel peut donc être PAL après repli ; ce point est documenté et non exposé par l'API.

**Test actif unique :** `tests/current/R10_JEFF_MODE_FALLBACK.asc`, bandeau `R10-JEFF-MODE-FALLBACK-01`, même chemin que le test R9 validé. Commencer avec Jeff-Flag 736×482 ; si ouverture et rendu valides, vérifier Fallout pour non-régression. **Aucun PASS R10 tant qu'AMOS/WinUAE n'a pas été exécuté.** Tests CPU Unicorn ajoutés dans `tools/test_ntsc_pal_r10.py`, résultats d'exécution non confirmés.

**Statut :** `main` et `LAST_GOOD` inchangés ; branche existante `codex/intuition-input-r1`, PR #4 Draft. Interdiction de merger R10 avant Gate A CPU et Gate B runtime ; Gate C AMOS compilé R10 non testé. Références : `docs/R10_NTSC_PAL_FALLBACK.md`, `docs/R9_JEFF_MODES.md` et `tests/README.md`.

---

**Statut historique : R9 0.6.0, PASS 4/4 interprété WinUAE et PASS AMOS Compiler signalé le 10/11/2026 ; R10 est maintenant candidate active.** Branche unique `codex/intuition-input-r1`, PR #4 Draft. `dist/AMOSPro_AGA.Lib` est R9, identique à son archive expérimentale. R8 archivée comme repli ; `LAST_GOOD` et `main` inchangés. Pas de merge avant validation des autres gates.

## Retour runtime R9 — Fallout.iff, 4/4 PASS

Test source : `tests/passed/R9_PICINFO_A3_REGRESSION.asc` (bandeau unique `R9-A3-REGRESSION-01`), repris sans modification du dossier `tests/current/`.

Sur **quatre lancements consécutifs** dans WinUAE, retour utilisateur : aucun incident. Capture reçue : `SIZE 640 X 512 PLANES 4`, `CMAP 16 COMPRESSION 1`, `MODE 167936 COLORS 16`, `OPEN=1`, `DB=1`, `LOAD=1`, `SWAP=1`, `KEY 68 - CLOSE RETURNED`. L'interface AMOS affiche ensuite `End of program at line 68`.

**Gate B (AMOS interprété, ce scénario) : PASS 4/4.** La disparition du blocage est cohérente avec la correction A3. Elle ne permet pas encore de valider la fidélité graphique, la compilation, Ctrl+C en Swap ni un enchaînement de formats différents. Gate A (tests CPU/CI R9) non confirmé, Gate C compilé non testé, Gate D matériel non testé.

## Preuve source AMOS Professional

Source officielle : [AOZ-Studio/AMOS-Professional-Official/+ILib.s](https://github.com/AOZ-Studio/AMOS-Professional-Official/blob/master/%2BILib.s)

- `Ent_2` prépare une fonction à deux paramètres. `FEnt_2` évalue le premier, puis
  `MOVE.L D3,-(A3)` le pousse sur la pile AMOS ; le deuxième reste en D3.
- `LGoto` (ligne ~2795, saut interne d'un `IF` faux / `ELSE` / GOTO)
  parcourt les structures de boucles via `ADD.W (A3),A3` puis `BRA.S .Loop`.

Dans le source R8 `tools/build_m5_generic.py`, `routine(info=True)` :
1. `MOVEM.L` prologue `48E7 EFFE` sauvegarde A3 ;
2. `MOVE.L (A3)+,D3` (opcode `261B`) consomme le premier argument ;
3. `MOVEM.L` épilogue `4CDF 7FF7` **restaure A3**, annulant le dépilement.

**Violation de contrat paramètre :** une valeur obsolète peut rester sur la pile
AMOS, que `LGoto` peut interpréter comme un enregistrement de boucle.

## Preuve WinUAE (10 novembre 2026)

Registres : PC=`$4019CAB8`, A3=`$403DFA96`, D0=`$403E39F0`.
WinUAE décode exactement `ADDA.W (A3),A3` à ce PC et indique
`(A3)=$0000`. Instruction suivante : `BRA.B $4019CAA8`, qui correspond
au parcours de `LGoto`. L'addition de zéro ne fait pas avancer A3 et
la condition de sortie (`A3 >= BasA3`) n'est pas satisfaite.

Cela démontre le blocage dans la gestion de la pile de contrôle AMOS.
Le lien avec le dépilement incorrect de PicInfo est **fortement étayé** par la violation ABI et par le PASS R9 4/4, sans démonstration exhaustive pour les autres scénarios.

## Correctif minimal R9

Source : `tools/build_picinfo_a3_r9.py`.

- Segment AP20 **n°14 uniquement** (`Aga Pic Info`) ;
- `48E7 EFFE` → `48E7 EFEE` (ne plus sauvegarder A3) ;
- `4CDF 7FF7` → `4CDF 77F7` (ne plus restaurer A3) ;
- autres registres préservés, taille de pile symétrique ;
- tous les autres segments AP20 strictement identiques à R8 ;
- titre/version mis à jour, code de longueur identique et aucun saut à déplacer.

Archive R9 : `dist/experimental/AMOSPro_AGA_M5_v0.6.0_PICINFO_A3_R9.Lib`.
Taille : **8772 octets**.
SHA256 : `58312880cf4096170b1361232d298e8b54f762219d22a0e5c83d41d3f1177e7c`.
R8 source SHA256 : `112dce3e7945a235430a0263e309126061639de0d8dcc0d9c319431b0f2f27a2`.

**Candidat courant :** `dist/AMOSPro_AGA.Lib` (identique à l'archive R9).
La R8 reste archivée dans `dist/experimental/AMOSPro_AGA_M5_v0.5.9_DB_SYNC_R8.Lib`.
Le builder R9 écrit les deux sorties et `verify_artifacts.py` contrôle cette égalité.

Le binaire R9 a été calculé par une **vérification binaire indépendante**
sur le blob GitHub R8 (deux changements de masque, titre uniquement).
Le builder Python et les tests Unicorn sont présents ; **l'exécution CI R9 n'est pas encore confirmée**.

## Portes de validation — état au 10 novembre 2026

1. **Gate A — statique et CPU :** le contrôle indépendant des octets AP20 et du SHA-256 est acquis. Exécution de `tools/test_picinfo_a3_r9.py` sous Unicorn/CI **non confirmée** ; à effectuer avant de déclarer cette porte complète.
2. **Gate B — interprété :** **PASS 4/4** sous WinUAE pour `Fallout.iff`, séquence complète PicInfo/Open/DB/Load/Swap/Wait Key/Close ; retour à l'éditeur.
3. **Gate C — AMOS Compiler :** **NON TESTÉ**. Reprendre le même programme `tests/passed/R9_PICINFO_A3_REGRESSION.asc` compilé, sans lui ajouter de nouvelle logique.
4. **Gate D — matériel AGA :** **NON TESTÉ**. Les tests multi-formats, visuels et Ctrl+C en Swap restent à prévoir selon les exigences du jalon.

**Une seule branche et une seule PR Draft.** Ne pas modifier `LAST_GOOD` ni merger sur `main` sur la seule base de ces quatre succès.
