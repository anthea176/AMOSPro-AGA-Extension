# M11 — R26 0.9.2 : contrat de la première fonction de texte AGA

**État : R26 0.9.2, Gate A CPU/CI PASS (64 scénarios 68000), Gate B AMOS interprété/WinUAE PASS sur le test graphique R26 archivé.** Binaire courant [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) = [archive R26 0.9.2](../dist/experimental/AMOSPro_AGA_M11_v0.9.2_TEXT_R26.Lib), **14 044 octets**, SHA256 `0fa162a9955ab317b25a0de43d6ddc07ed082dc4fac87188d744995bccb4a287`. CI complète R26 [#42922291061](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42922291061). R25 0.9.1 reste archivée, WinUAE PASS sur son propre scénario M10 ; R24 et `LAST_GOOD` R10 inchangées. Compiler et matériel réel NON TESTÉS.

## API candidate et paramètres

```amos
_OK=Aga Text(_X,_BASELINE_Y,_PEN,_TEXT$)
```

- **Fonction entière AP20** : signature `00,0,0,2`, quatre paramètres (entier X, entier Y, entier pen, chaîne), résultat `D3`, `D2=0`.
- **ABI** : `D3` contient le pointeur sur le descripteur de chaîne AMOS, les trois LONG sur `(A3)+` sont lus dans l'ordre `pen,baselineY,x` ; avance `A3+12`, SP équilibrée, tous les registres non-volatils protégés.
- `_X` : origine horizontale en **pixels**, `_BASELINE_Y` : **ligne de base** de la fonte (pas son coin haut), `_PEN` : index couleur `0..(2^Depth-1)`, `_TEXT$` : **1 à 128 caractères** d'une ligne.
- **`_OK=1`** : texte rendu dans le back buffer AGA et `WaitBlit` terminé ; **`_OK=0`** : état invalide, géométrie ou texte refusés, ou back buffer **pas encore Safe**. Ne pas boucler sans borne en cas de `0`.

## Contrat de rendu

**Aucun rendu sur l'écran AMOS :** la fonction retrouve le `ScreenBuffer.sb_BitMap` inactif via `A5+$1C8 → State+32 → DBState+8`, comme les primitives R25 déjà validées. Elle reprend le mécanisme déjà utilisé par `Aga Back Fill` : `InitRastPort` sur une structure temporaire, puis `RastPort.BitMap` défini explicitement. **La structure est sur la pile, sans allocation heap** ; `WaitBlit` termine avant sa libération.

- Fonte système standard issue de `InitRastPort`, couleur indexée par `SetAPen`, `JAM1` (fond transparent) par `SetDrMd` ; `Move` puis `Text` de `graphics.library`.
- `TextExtent` (AmigaOS V36+, compatible avec le socle AGA V39) calcule les bords **réels** du texte relativement à la ligne de base, en incluant les débords de glyphes. Rejet si un point du rectangle sortirait de l'image ; **aucun clipping supposé**.
- Toutes les dimensions physiques `BitMap.BytesPerRow`, `Rows`, `Depth` et tous les pointeurs `Planes[]` sont vérifiés avant rendu, en plus de la profondeur, largeur et hauteur logiques de l'écran.
- Les chaînes AMOS sont **préfixées par un mot de longueur**, sans NUL terminal. Le prototype se limite au texte d'une seule ligne ; les caractères de contrôle ne produisent **aucune action de contrôle** AmigaOS.

## Synchronisation Safe / Disp

`Aga Swap` met `DBState+20=3` sur un succès. Son bit 0 représente la notification Safe de l'ancien buffer. R26 applique à **son propre** dessin cette règle :

1. si bit 0 est nul, le buffer arrière courant peut être utilisé sans attente supplémentaire ;
2. si bit 0 est positionné, appeler **une seule fois** `Exec/GetMsg(SafePort)` **sans blocage** ;
3. si aucun message, renvoyer `0`, sans dessin ni attente ;
4. si une notification est disponible, vider le bit 0 **sans ReplyMsg** (ce message est une réponse déjà envoyée par le système) et préserver le bit 1 Disp ;
5. dessiner, appeler `WaitBlit`, retourner `1`.

**Important :** ce mécanisme ne sécurise **pas rétroactivement** les commandes R25 `Aga Blit Clear/Fill/Copy`. Le programme AMOS ne doit pas les appeler sur l'ancien front buffer tant que Safe ne l'autorise pas. Une synchronisation graphique **commune** reste un chantier indépendant, si nécessaire. `Aga Wait Vbl` n'est pas un accusé Safe.

## Contrôles avant mise à disposition

- **Gate A** : reproduction binaire AP20 R25→R26, 37 segments, unique segment R26 ajouté, R25 conservée strictement (sauf `GetP` terminal). Décodage Capstone 68000 et tests CPU Unicorn avec interruptions OS simulées : ABI mixte, avant/après Safe, messages Safe absents/présents, bit Disp préservé, bornes réelles des glyphes, pénalités, états invalides, rendu et `WaitBlit` ; vérifier la CI **avant** promotion d'un binaire.
- **Gate B : PASS sur ce scénario précis (11/11/2026).** Le programme [archivé sans modification](../tests/passed/M11_R26_AGA_TEXT_01.asc), bandeau `M11-R26-AGA-TEXT-01`, affiche **`AGA TEXT R26` en vert sur un panneau bleu** via le BitMap AGA, puis revient normalement à AMOS (fin programme ligne 74). Console observée : `IMAGE 320 X 256 PLANES 8`, `OPEN 1 DB 1 LOAD 1`, `CLEAR 1 PANEL 1`, `BAD 0 TEXT 1 SWAP 1`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED`. Le rejet du texte débordant (`BAD 0`) est confirmé. Ce test affiche **une seule image après un swap** : il ne valide pas la synchronisation Safe sur des alternances rapides.
- **Gate C** : AMOS Compiler, **Gate D** : vrai Amiga AGA ; tous deux non validés.

## Références

- [Audit source R25 et Safe/Disp](M11_BACKBUFFER_R25.md).
- [`graphics.library/Text` et ABI 68000](https://d0.se/autodocs/graphics.library/Text).
- [`graphics.library/TextExtent` et métriques de fonte](https://d0.se/autodocs/graphics.library/TextExtent).
- [`InitRastPort` et structure `RastPort`](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node02F7.html).
- [Double Buffer Intuition / SafeMessage](https://wiki.amigaos.net/wiki/Intuition_Screens).

**Clôture du scénario R26 : Gates A+B PASS**, [test original WinUAE archivé octet pour octet](../tests/passed/M11_R26_AGA_TEXT_01.asc) (blob Git `2cd9acd45f17a07ac77bbd1a340aa14c628a01ad`), `tests/current/` sans `.asc`. Ne pas promouvoir `LAST_GOOD` ni prétendre à une validation Compiler/Amiga AGA physique. Pas de nouvelle branche.
