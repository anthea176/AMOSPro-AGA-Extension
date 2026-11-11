# M14 / R37 0.10.9 -- Aga Font Select (contrat et candidate)

**Statut réel (11/11/2026) : Gate A native CPU/CI et export source 68000 strict PASS** — [CI R37](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43075769541). 20 groupes R37 + 64 cas R26 + 106 scénarios R36 PASS. `dist/AMOSPro_AGA.Lib` = archive R37 : 22 328 octets, SHA256 `bc6e7535ef300551298edae1a205ffdffa38db81e4126a5a42b36a0261b5e58a`, 43 commandes AP20. `dist/AMOSPro_AGA_LAST_GOOD.Lib` = R36 conservée, SHA256 `f30882fc3d3dd86a0f30bf5c897e102a4892f992efa7e5e349184994d749d225`. **Gate B AMOS interprété/WinUAE EN ATTENTE** avec `tests/current/M14_R37_FONT_SELECT_01.asc`. Gates C/D non testées. R38/R39 restent hors périmètre de codage.


## Contrat approuve : une seule commande

```amos
_OK=Aga Font Select("topaz.font",8)
_OK=Aga Text(24,64,1,"MENU AGA")
```

- **Commande numerique AP20** : `_OK=Aga Font Select(FontName$,YSize)`, signature `02,0`. L'argument `YSize` arrive en D3 et le pointeur vers le descripteur AMOS de `FontName$` se trouve a `(A3)+`; resultat entier 1 ou 0 en D3, D2=0. La chaine AMOS est prefixee par une longueur WORD, non terminee par NUL : la routine la convertit dans un tampon local avec NUL final.
- `FontName$` : 1 a 127 octets non nuls, nom `.font` ou chemin admissible par `diskfont.library`. `YSize` : entier 1..255. AmigaOS peut choisir la taille disponible la plus proche ; la fonction valide le chargement mais ne promet pas une taille exactement identique a la demande.
- **Reinitialisation** : `Aga Font Select("",0)` restaure la fonte par defaut pour les appels `Aga Text` suivants. Elle libere la fonte selectionnee. Sans fonte prealablement choisie, l'appel est idempotent et renvoie 1 tant qu'un ecran AGA de l'extension est ouvert.
- **Echec atomique** : arguments invalides, aucun ecran AGA actif, graphics.library absente, `OpenLibrary("diskfont.library")` ou `OpenDiskFont` en echec : retour 0, aucune modification de la selection precedente. Aucun fichier image, banque ABK/AGAPAL ou palette modifie.
- **Application** : seuls les prochains appels `Aga Text` sur le back buffer de l'ecran Intuition AGA prive sont affectes. La fonte est appliquee avec `graphics.library/SetFont` sur le RastPort temporaire **avant** `TextExtent`, puis `Text`. Les rectangles de glyphes continuent d'etre refuses s'ils sortent du bitmap ; pas de clipping hasardeux. Le protocole Safe/Disp R26/R27 reste actif. La font ne s'applique pas a la fonction `Text` native AMOS ou a `Change Bank Font` AMCAF.
- **Duree de vie** : un `TextFont*` ouvert est possede par l'extension et conserve dans un etat prive de 8 octets du HUNK AP20 (`Screen*` + `TextFont*`). On libere avec `graphics.library/CloseFont` lors du changement de fonte, de la reinitialisation et de `Aga Screen Close`. La `diskfont.library` est refermee juste apres `OpenDiskFont`; aucun handle diskfont persistant. Pas de modification de `Screen.UserData` ou de l'etat graphique d'AMOS.
- **Aucune attente VBL ou tache asynchrone** : les chargements de fonte depuis disque peuvent bloquer le programme jusqu'a leur conclusion (comportement AmigaOS). Il n'y a ni sprite, ni AMAL, ni banque de fonte ajoutee dans R37.

## Construction et preservation des regressions

Base strictement figée : archive R36 `dist/experimental/AMOSPro_AGA_M13_v0.10.8_PALETTE_CYCLE_R36.Lib`, 21 836 octets, SHA256 `f30882fc3d3dd86a0f30bf5c897e102a4892f992efa7e5e349184994d749d225`. Les **42 commandes anterieures** et `LAST_GOOD` restent conserves ; R37 ajoute la 43e commande.

Empreinte de modification des segments AP20 : **8** (`Aga Screen Close`, remplacement sur 4 octets d'un `JSR CloseScreen` par un `BSR.W` vers un helper qui conserve le `CloseScreen`), **36** (`Aga Text`, reemission controlee du 68000 R26 avec selection de fonte avant `TextExtent`), **47** (ajout terminal `GetP`) et **48** (nouvelle fonction et helpers). Tous les autres segments restent strictement inchanges. Aucun autre depot ou branche n'est concerne.

Builder deterministe en memoire : `tools/build_m14_font_select_r37.py`. Emetteur 68000 : `tools/m14_font_select_r37_emit.py`. Regressions CPU 68000 : `tools/test_m14_font_select_r37.py` ; workflow `r37-candidate-gate-a.yml` puis export assembleur strict. Les tests de Gate A ne sont ni une compilation AMOS, ni une execution WinUAE.

## Plan Gate B WinUAE

1. Installer **uniquement apres Gate A PASS** la candidate directe `dist/AMOSPro_AGA.Lib` (pas de renommage utilisateur), puis charger `tests/current/M14_R37_FONT_SELECT_01.asc` dans AMOS interprete.
2. Verifier la selection visible de `topaz.font` 8 puis 9, le texte systeme apres reset et les refus pour taille 0, 256 et nom vide + taille non nulle.
3. Confirmer `RESULT 1`, `CLOSE RETURNED`, aucune erreur de memoire ni blocage. Observer le retour a AMOS, la fermeture de l'ecran et la nouvelle tentative de selection refusee apres `Close`.
4. **Uniquement apres confirmation utilisateur de Gate B**, recopier la candidate dans `dist/AMOSPro_AGA_LAST_GOOD.Lib`, archiver le test execute octet pour octet dans `tests/passed/`, puis mettre a jour les deux README. **Gate C Compiler et D Amiga physique : NON TESTEES**.

## Suite M14 -- contrats separes

`R38` compatibilite avec les banques produites par AMCAF `Make Bank Font`, puis `R39` fontes bitmap 8x8 de `Change Print Font`, **ne sont pas implementees ni approuvees pour un codage simultane**. L'etude de leur format est distincte. Les deux restent seulement planifies.
