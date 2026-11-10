# R11 0.6.2 — positionnement initial des écrans Jeff

## REJET RUNTIME (10/11/2026)

R11 provoque un **écran gris** avec Jeff, régression par rapport à R10 (image chargée et suite des commandes fonctionnelle, malgré la position initiale basse). WinUAE : PC `$00F81472`, instruction Kickstart `STOP #$2000`; ce seul PC n'identifie pas la cause de la régression. Le helper R11 appelle ScreenToFront/MoveScreen pendant l'ouverture, avant OpenWindow ; la sécurité de ce moment du cycle de vie n'est pas démontrée.

**R11 archivée et rejetée ; retour R10 en binaire actif et LAST_GOOD à la demande utilisateur.** Conserver intacte la R11 rejetée pour audit ; repartir de R10 pour tout correctif ultérieur.

---

## Constat utilisateur

Sous **R10**, Jeff-Flag 736×482 s'ouvre et l'image est chargée ; Double Buffer, Swap, clavier et fermeture fonctionnent d'après le retour utilisateur. Mais l'écran AGA apparaît **trop bas**, avec le haut du Workbench occupant l'affichage. L'utilisateur peut remettre l'écran à la bonne position par glissement. Il a expressément précisé qu'il s'agissait d'une **position verticale**, pas d'une image derrière Workbench au sens d'un problème de chargement.

R9 reste le dernier candidat dont le scénario complet Fallout a été validé à la fois sous **AMOS interprété (4/4)** et **AMOS Compiler (PASS rapporté)**. R10 est validée fonctionnellement pour Jeff avec réserve de présentation et n'est pas un jalon final.

## Contrat AmigaOS vérifié

- `intuition.library/ScreenToFront` : LVO **-252**, Screen* en A0.
- `intuition.library/MoveScreen` : LVO **-162**, Screen* en A0, dx en D0.W, dy en D1.W.
- `struct Screen.TopEdge` : champ WORD signé à l'offset **+10** (après NextScreen, FirstWindow et LeftEdge).
- `MoveScreen` applique un déplacement relatif et peut être asynchrone ; si TopEdge est positif, le déplacement est `(0,-TopEdge)`. Si TopEdge est nul ou négatif, aucun déplacement n'est nécessaire. Ne jamais écrire directement dans `Screen.TopEdge`.
- Aucun changement dans les ViewPort, Copper, palettes ou bitplans. La taille 736×482 reste intégrale.

Sources officielles : [intuition/screen.h](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node0602.html) et [autodocs intuition MoveScreen](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_2._guide/node0598.html).

## Patch ciblé

`tools/build_screen_position_r11.py` prend comme entrée immuable l'archive R10 (SHA256 `e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3`).

- **AP20 #6 uniquement**, `Aga Screen Open` ; autres segments AP20 identiques à R10.
- Dans le helper R10 (80 octets), le **deuxième** `OpenScreenTagList` (exécuté seulement après échec NTSC et vérification du PAL) devient un `BSR.W` local à l'offset **722** : `4EAEFD9C → 61000008`.
- Le helper de **44 octets**, inséré avant le marqueur `GetP`, appelle normalement `OpenScreenTagList` puis, si l'écran est obtenu, `ScreenToFront` et `MoveScreen` uniquement en cas de TopEdge positif. Le Screen* est sauvegardé sur la pile CPU et restauré en D0 malgré les registres volatils des appels OS.
- **Aucun appel de repositionnement n'est ajouté aux ouvertures natives réussies** : Fallout PAL et NTSC natif gardent exactement le code exécuté sous R10. Le repli PAL logique/physique et les tags d'ouverture restent inchangés.
- Loader ILBM, PicInfo/A3, Double Buffer, Swap, clavier, Ctrl+C, Close et toutes les fonctions hors Open inchangés.
- Taille R11 **8 896 octets**. SHA256 `0e2419965f411c4e9419b1c7c8d07debdde525f13f7b8da80e2ed9d3ee30ea7b`.
- Archive : `dist/experimental/AMOSPro_AGA_M5_v0.6.2_JEFF_POSITION_R11.Lib`, candidat actif : `dist/AMOSPro_AGA.Lib`. R10/R9 et `LAST_GOOD` préservés.

## Gates

- Structure binaire, signatures, saut local et segments inchangés : **contrôlés statiquement** lors de la création du binaire.
- `tools/test_screen_position_r11.py` : exécution **Unicorn à confirmer**, test du vrai segment 68000 : fallback 736/724/640, TopEdge positif/nul/négatif, pointeur Screen*, échec de mode, fenêtre et chemin PAL natif.
- Test AMOS unique `tests/current/R11_JEFF_SCREEN_POSITION.asc`, bandeau `R11-JEFF-SCREEN-POS-01`. **À faire :** Jeff-Flag doit s'ouvrir intégralement en haut sans déplacement manuel ; puis Fallout pour non-régression, et AMOS Compiler ensuite.
- **R11 n'a aucun PASS WinUAE/Compiler à ce stade.** Ne pas merger vers `main`, ni promouvoir `LAST_GOOD` avant validation. Branche `codex/intuition-input-r1`, PR #4 Draft.

La correction ne démontre pas que le TopEdge était effectivement positif dans le cas signalé : elle traite à la fois la priorité d'écran et son décalage vertical de manière non destructive, **uniquement dans le chemin de repli PAL**.
