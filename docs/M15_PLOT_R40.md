# M15/R40 v0.11.1 — Aga Plot(X,Y,Pen)

**Version R40 v0.11.1 promue `LAST_GOOD` le 12/11/2026 : Gates A CPU/CI et B AMOS interprété / WinUAE PASS.** Capture de l'utilisateur : `CORNERS 1 1 1 1`, `DIAG 192 ERR 0`, `BADXY 0 0 0 0`, `BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, `RESULT 1`, `CLOSE RETURNED` (fin ligne 99) ; rendu visuel confirmé. [Test original archivé](../tests/passed/M15_R40_PLOT_01.asc), Git blob `6ab9cf4a91cca9f8097ffba40a32e2b85b049c38`. La bibliothèque `dist/AMOSPro_AGA.Lib`, l'archive R40 et `LAST_GOOD` sont identiques : SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`, 23 840 octets. **Gates C Compiler et D Amiga physique NON TESTÉES.** Le contenu des sections de préparation ci-dessous décrit l'état avant l'essai final.

**État validé le 12/11/2026 : Gate A CPU/CI et export strict PASS ; Gate B AMOS interprété/WinUAE PASS après essai utilisateur.** Première fonction du chantier M15 dessin 2D, approuvée explicitement par l'utilisateur. R39 bitmap 8×8 non développée.

## Interface publique

```amos
_OK=Aga Plot(X,Y,Pen)
```

- `X`, `Y`, `Pen` sont **trois entiers**. `0 <= X < Width`, `0 <= Y < Height` (le dernier pixel `319,255` est donc valide en 320×256). L'index `Pen` doit être dans `0..2^Depth-1` pour un écran AGA indexé de 1 à 8 bitplanes.
- `_OK=1` uniquement si `graphics.library/WritePixel(-324)` renvoie **0** (succès AmigaOS). `_OK=0` pour tout refus de paramètres, écran fermé, bitmap non valide, `Safe` non reçu ou retour `WritePixel=-1`. Ce refus n'implique pas qu'un fichier ou écran AMOS classique ait été modifié.
- La cible est **strictement le back buffer AGA privé** (`ScreenBuffer.sb_BitMap` inactif). Les écrans historiques AMOS ne sont jamais concernés. `Aga Swap` et `Aga Wait Vbl` sont laissés au programme appelant.
- **Pas de clipping implicite :** tout pixel hors écran retourne 0 sans tentative d'écriture. Pas de palettes RGB24 en paramètre, pas de transparence ni épaisseur, pas d'allocation persistante.

## Réalisation native 68000

- Émetteur : [`tools/m15_plot_r40_emit.py`](../tools/m15_plot_r40_emit.py), nouvelle entrée AP20 **50**, jeton `aga plot` à trois paramètres numériques (`00,0,0`). `D3=Pen`, `(A3)+=Y`, `(A3)+=X`; résultat `D3=0/1`, `D2=0`, `A3` avance de **8 octets**, pile équilibrée, autres registres préservés selon l'ABI des étapes précédentes.
- Validation préliminaire complète du `State`, `GfxBase`, `DBState`, dimensions logiques, `BitMap.BytesPerRow*8 >= Width`, `Rows >= Height`, profondeurs identiques, pointeurs de tous les plans valides. **Aucun appel de dessin avant ces vérifications**.
- Garde `Safe` de R27 sans attente bloquante : si le bit0 de `DBState+20` est positionné, un seul `Exec/GetMsg(-372)` sur le `SafePort`. Si aucun message, retour 0 sans dessin. Si reçu, seul le bit0 est effacé ; bit `Disp` préservé. Aucun `ReplyMsg`.
- `InitRastPort(-198)` sur une structure temporaire de **128 octets sur la pile**, `RastPort.BitMap=backBitMap`, `SetAPen(-342)`, `SetDrMd(-354)` en mode JAM1/copie, `WritePixel(-324)`, puis `WaitBlit(-228)` pour laisser le RastPort temporaire hors danger avant sa libération. Pas de heap.
- [Builder déterministe](../tools/build_m15_plot_r40.py) : **R38 archivée** est la seule base `dist/experimental/AMOSPro_AGA_M14_v0.11.0_AMCAF_BANK_R38.Lib` (SHA256 `09b23a6cd1b8f8eb91b836b43a98ede4da2b16e0b6fb2173ac43ab54d684f366`). Les **49 premières entrées R38 sont identiques**, et l'entrée R38 BankFont est strictement inchangée à l'exception de l'ajout du séparateur `GetP` final. Le texte, les fontes, les palettes et les autres commandes restent intacts.

## Artefacts et gates

| Artefact | État | Empreinte |
|---|---|---|
| [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) | **Candidate R40 v0.11.1** — 45 commandes AP20, 23 840 octets | SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231` |
| [`dist/experimental/AMOSPro_AGA_M15_v0.11.1_PLOT_R40.Lib`](../dist/experimental/AMOSPro_AGA_M15_v0.11.1_PLOT_R40.Lib) | Archive de la **candidate non encore validée WinUAE** ; strictement identique au fichier courant | SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231` |
| [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../dist/AMOSPro_AGA_LAST_GOOD.Lib) | **R40 v0.11.1** WinUAE-PASS, identique à candidate et archive, 23 840 octets | SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231` |

**Gate A CPU 68000 + CI : PASS** — [221 scénarios](../tools/test_m15_plot_r40.py) : profondeur 1/2/4/8, deux buffers, cas limites `(0,0)` / `(319,255)`, couleur 0/max, bitmap physique/logique, plan absent, index invalide, gestion `Safe` (dont bit `Disp`), ABI/registre/pile, retour de `WritePixel`, byte-level vérification des pixels et absence d'écriture parasite. [CI GitHub](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43128576279) **PASS**, export source 68000 strict **PASS**. Les 44 commandes et le `LAST_GOOD` R38 sont protégés par les contrôles d'intégrité.

**Gate B AMOS interprété / WinUAE : PASS** — [`tests/passed/M15_R40_PLOT_01.asc`](../tests/passed/M15_R40_PLOT_01.asc). Aucun matériel réel, rendu écran, absence de fuite sur le vrai Amiga ni compatibilité Compiler ne sont inférés des tests CPU.

**Gates C/D :** AMOS Compiler et Amiga AGA physique **NON TESTÉES**.

## Recette WinUAE prévue (Gate B)

1. Installer uniquement la **candidate R40** `dist/AMOSPro_AGA.Lib` dans `APSystem` et **redémarrer AMOS** sans changer son slot. Préserver l'ancienne Lib et l'archive `LAST_GOOD`.
2. Importer [le test](../tests/passed/M15_R40_PLOT_01.asc) dans un programme AMOS vide via **Project → Merge ASCII**. Aucun IFF ni ABK externe n'est nécessaire.
3. Vérifier à l'écran AGA un **X de deux diagonales colorées**, quatre pixels aux coins, et les textes, avant le retour AMOS.
4. À la console, attendre `CORNERS 1 1 1 1`, `DIAG 192 ERR 0`, `BADXY 0 0 0 0`, `BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `RESULT 1`, `CLOSE RETURNED`. Les paramètres invalides doivent tous retourner zéro.
5. **Seulement après confirmation explicite de ce scénario par l'utilisateur**, déplacer le test original sans modification vers `tests/passed/`, copier exactement le binaire validé vers `dist/AMOSPro_AGA_LAST_GOOD.Lib`, puis publier le statut et les empreintes.

Ne pas commencer `Aga Draw`, `Aga Box` ni `Aga Circle` sans décision distincte. Travail uniquement sur la branche `main` du dépôt `anthea176/AMOSPro-AGA-Extension`.
