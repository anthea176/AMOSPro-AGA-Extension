# R10 0.6.1 — repli NTSC vers PAL sans modifier l'ILBM

## VERSION RESTAURÉE + LAST_GOOD (10/11/2026)

R10 est rétablie **octet pour octet** dans `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib`, sur demande explicite, après échec graphique R11. L'ancien M4b LAST_GOOD est déjà archivé dans `archive/`.

**R10 fonctionne avec les Jeff**, avec la réserve de la position initiale trop basse, réglable manuellement. Ne pas présenter ce jalon comme totalement validé : tests compilés R10 et positionnement initial restent ouverts. Le loader ILBM est inchangé.

---

**État archivé après essai utilisateur :** R10 ouvre et charge Jeff-Flag, avec les commandes suivantes fonctionnelles selon le retour utilisateur, mais l'écran apparaît trop bas, partiellement sous Workbench. La position peut être corrigée manuellement par glissement. **R10 n'a pas de PASS de positionnement automatique.** Ce défaut est ciblé par R11 0.6.2 dans `docs/R11_SCREEN_POSITION.md`. Branche `codex/intuition-input-r1`, PR #4 Draft. `LAST_GOOD` inchangé. Le dernier candidat validé est **R9 0.6.0**, PASS 4/4 interprété et PASS AMOS Compiler sur Fallout.

## Défaut visé

Dans le corpus réel, `Jeff-Flag.iff` (736×482×4, CAMG `$00019004`, compression ByteRun1) renvoie `Aga Screen Open=0` sous R9, sans planter. Les fichiers `Jeff-OU-3`, `Jeff-Space2` et `Jeff-Warhead3` partagent le même mode NTSC HiRes Lace. Cette famille peut ne pas être disponible dans la configuration WinUAE utilisée. Le maximum d'overscan visible classique HiRes est 724, mais la zone vidéo complète peut atteindre 736 et `SA_AutoScroll` reste actif. Ne pas recadrer la largeur.

## Correctif minimal

Builder : `tools/build_ntsc_pal_r10.py`.

- Base immuable : archive R9, SHA256 `58312880cf4096170b1361232d298e8b54f762219d22a0e5c83d41d3f1177e7c`.
- Une seule entrée AP20 modifiée : **#6 `Aga Screen Open`** ; le `JSR -612(A6)` vers `intuition.library/OpenScreenTagList` est remplacé par `BSR.W` vers un helper de **80 octets** inséré juste avant `GetP`. Les anciennes branches et instructions restent à leurs offsets ; la table AP20 est recalculée par `rebuild()`.
- Le helper appelle d'abord le **mode demandé** sans modification. Sur succès, il rend le pointeur Screen immédiatement, sans autre changement.
- Sur échec, il ne réessaie **que si le ModeID contient `NTSC_MONITOR_ID` ($00010000)**. Il recompose `ModeID + $00010000` avec les mêmes bits de mode vidéo (PAL équivalent) et interroge `graphics.library/ModeNotAvailable`, LVO **-798**.
- Si PAL est disponible, il réutilise les mêmes tags `SA_Width`, `SA_Height`, `SA_Depth`, `SA_FullPalette`, `SA_AutoScroll` ; il change uniquement la valeur de `SA_DisplayID` située à `28(A1)`, puis réessaie `OpenScreenTagList`. Sinon, retour `OPEN=0` comme auparavant.
- Le pointeur des tags est conservé dans D2 (non volatil dans l'ABI AmigaOS), D1 est recalculé après appel système, A6 est restauré après `ModeNotAvailable`, D7 ne change pas et le résultat public D2 est remis à 0 par la sortie Open d'origine.
- **`STATE_MODE` reste le ModeID logique demandé** (`$00019004` pour Jeff), même lorsque l'écran physique a été ouvert en PAL `$00029004`. Cette distinction est nécessaire : `Aga Iff Load` valide le CAMG réel du fichier contre le mode logique. Le ModeID physique doit être interrogé séparément auprès du ViewPort si une API l'expose ultérieurement.
- La Lib R10 garde les **18 autres entrées AP20 identiques à R9** : aucun changement de PicInfo/A3, du décodeur ILBM, DB, Swap, clavier, Close ou Ctrl+C.
- Limite : si l'ouverture de la **Window** échoue après l'écran, ou si PAL et NTSC échouent, l'API renvoie toujours 0 et conserve le nettoyage existant. Cette R10 n'est **pas** un correctif universel de tous les modes AmigaOS.

Taille R10 : **8 852 octets**. SHA256 :
`e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3`.

Archive : `dist/experimental/AMOSPro_AGA_M5_v0.6.1_NTSC_PAL_R10.Lib`.
Active : `dist/AMOSPro_AGA.Lib`. Binaire R9 conservé dans `dist/experimental/` comme repli.

## Validation et test unique

- Structure HUNK/AP20, signature d'appel, longueur 80 octets et delta unique : contrôlés à la génération. Le binaire a été calculé indépendamment et sa somme SHA256 figée.
- `tools/test_ntsc_pal_r10.py` : tests Unicorn du **véritable 68000** (PAL et NTSC déjà disponibles, Jeff 736/724/640, mode PAL absent, échec mémoire simulé, échec Window, non-régression Fallout, état mode logique conservé). **Non exécutés dans cette session** ; intégrés au pipeline CI.
- Test AMOS unique `tests/current/R10_JEFF_MODE_FALLBACK.asc`, bandeau `R10-JEFF-MODE-FALLBACK-01`. 1) Jeff-Flag, 2) Fallout si premier PASS. **R10 n'a aucun PASS runtime pour le moment.**
- R9 est PASS en interprété et compilé ; R10 doit repasser ses propres gates interprété/compilé. Ne pas extrapoler.

## Références AmigaOS

- `OpenScreenTagList`, `SA_AutoScroll`, `SA_DisplayID` : <https://wiki.amigaos.net/wiki/Intuition_Screens>
- `ModeNotAvailable`, Display Database : <https://wiki.amigaos.net/wiki/Display_Database>
- ModeID PAL/NTSC et valeurs LVO : `graphics/modeid.h`, `graphics_lib.fd` et documentation NDK.
- Overscan vidéo 736 en HiRes : <https://www.retroplatform.com/kb/19-115>.
