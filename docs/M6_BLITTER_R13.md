# M6 — Blitter R13 (0.7.0) : premier candidat `Aga Blit Copy`

> **Historique — R13 Copy validée sous WinUAE.** Le candidat actif suivant est désormais **R14 Fill**, voir [M6_BLITTER_R14.md](M6_BLITTER_R14.md). Les références ci-dessous à R13 en tant que Lib active décrivent le checkpoint R13, pas l'état courant.

## État du candidat R13 sur GitHub

**Bibliothèque active :** [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) = R13 0.7.0 (**9236 octets**, SHA256 `c71cab88d2294ed70c019f546d6c60ac72c278c1b625ded07d0aa6603e50a0cf`). Copie versionnée identique : [`dist/experimental/AMOSPro_AGA_M6_v0.7.0_BLIT_COPY_R13.Lib`](../dist/experimental/AMOSPro_AGA_M6_v0.7.0_BLIT_COPY_R13.Lib).

**Base figée :** archive R12 0.6.3, `LAST_GOOD` = R10 0.6.1 **inchangée**. Builder : `tools/build_m6_blit_copy_r13.py`, qui part de la R12 archivée et génère les deux fichiers R13.

**Gate A (CPU/CI) : PASS** sur le candidat actif ([run #42851646766](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42851646766)). **Gate B AMOS/WinUAE : PASS** du scénario `MYGIRL.IFF`, avec `COPY1=1`, `COPY2=1`, `BAD=0`, `SWAP=1`, `KEY=68` et fermeture. **Gate C Compiler : NON TESTÉ. Gate D matériel : NON TESTÉ.** Test archivé dans `tests/passed/M6_R13_BLIT_COPY_01.asc`.

---

**Statut : R13 0.7.0 validée en AMOS interprété/WinUAE pour le scénario Blit Copy ; compilation et matériel non testés.**
Le candidat courant est **R13 0.7.0** ; R12 0.6.3 est conservée en archive et `LAST_GOOD` reste **R10 0.6.1**.

## Portée du premier incrément

Nouvelle fonction AMOS :

```amos
_OK=Aga Blit Copy(sourceX,sourceY,destX,destY,width,height)
```

- Résultat entier : **1** si l'appel `BltBitMap` a traité au moins un plan et que `WaitBlit` est terminé ; **0** si absence d'écran/buffer, métadonnées incohérentes, rectangle nul, coordonnées hors écran ou refus de BltBitMap.
- Copie **du back buffer vers le même back buffer** uniquement ; aucune dépendance à la fenêtre AMOS ni modification du front buffer par notre code.
- Six paramètres entiers ; toutes les coordonnées sont en pixels, avec origine `(0,0)`.
- Opération synchrone (attente `graphics.library/WaitBlit` après la copie).
- Les chevauchements, shifts, modulos et masques sont délégués à la routine officielle **`graphics.library/BltBitMap`**, non réimplémentés sur registres chipset.
- Blit minterm **$C0** (copie), mask **$FF** (tous les plans de 1 à 8), `TempA=NULL` pour que graphics.library fournisse éventuellement son scratch de chevauchement.

La copie réclame `Aga Double Buffer`. L'IFF existant est chargé dans le back buffer avant la copie, puis `Aga Swap` l'affiche.

**Références AmigaOS :** [BltBitMap](https://developer.amigaos3.net/autodocs/graphics.library/BltBitMap.html) (sécurité des dimensions, 0xC0, overlap, retour et WaitBlit), [graphics.library](https://developer.amigaos3.net/autodocs/graphics.library/).

## Contrat ABI et intégrité

- Base exacte R12 : SHA256 `b4b06bedb955a23dc048ead7f2ecac8bab955591c6bcc094d4d6e6c4bad4eaec`.
- Le builder R13 **met à jour** `dist/AMOSPro_AGA.Lib` et son archive R13 à contenu identique. La R12 archivée et `dist/AMOSPro_AGA_LAST_GOOD.Lib` ne sont **jamais modifiées**.
- Entrées AP20 **0–17 identiques octet pour octet à R12**.
- Entrée 18 : uniquement ajout des quatre octets de délimitation `GetP` précédant la nouvelle entrée.
- Entrée **19** : nouveau code Blit Copy et token fonction `aga blit copy`, signature `00,0,0,0,0,0`.
- Passage AMOS : D3 = h, puis (A3)+ = w,dy,dx,sy,sx. Avancement obligatoire d'A3 de **20 octets**.
- Sortie AMOS : D3 = valeur, D2 = 0 ; toutes les autres valeurs de registres sauvées/restaurées à l'exception d'A3 et CCR ; pile CPU équilibrée.
- `BltBitMap` : A0/A1=back BitMap, A2=0, D0..D5=source/dest/tailles, D6=$C0, D7=$FF, A6=GfxBase.
- Validation bornes **avant tout DMA** : dimensions de l'écran en signés 16 bits, rectangle strictement positif, vérification par soustraction sans overflow, stride, rows, depth du Bitmap.
- Pas de `WaitPort`, pas de `Exec Wait`, pas de programmation directe de BLTCON, des modulos ou du bit descending.

## Génération et validation

Builder reproductible : `python -B tools/build_m6_blit_copy_r13.py` ; il lit **l'archive R12 immuable**, régénère **l'actif R13** et l'**archive R13**. Le contenu doit être identique à la version committée (vérification CI), et **LAST_GOOD ne doit pas être modifiée**.

Tests CPU : `tools/test_m6_blit_copy_r13.py` (Unicorn 68000 + hooks graphics.library, validité des paramètres, retour/ABI, deux orientations de front buffer, chevauchements et cas limites). Le mock valide la logique d'appel mais **ne prouve pas** le blitter matériel.

La CI **Artifact integrity** reconstruit et vérifie les binaires directement présents sur GitHub. Le test WinUAE R13 a ensuite été exécuté par l'utilisateur avec le binaire [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) et est maintenant **archivé** :

```text
tests/passed/M6_R13_BLIT_COPY_01.asc
```

Bandeau : `M6-R13-BLIT-COPY-01`. Le 10/11/2026, avec **`MYGIRL.IFF` 320×256, 8 plans**, l'utilisateur a confirmé les deux copies dont une chevauchante ; capture de sortie : `COPY1 1 COPY2 1 BAD 0`, `SWAP 1 KEY 68 CLOSE RETURNED`. Les zones noires copiées existent dans le rectangle source, ce n'est pas une régression établie. **PASS de ce scénario en interprété WinUAE**, hors compiler/matériel réel.

## Suite M6

Après ce PASS `Copy`, implémenter `Aga Blit Fill` puis `Aga Blit Clear` en gardant la même validation préalable et le bon buffer. La prise en charge d'un color index arbitraire nécessite le traitement cohérent de **chaque bitplane** ; ne pas traiter un `BltBitMap` tout-plan à minterm $F0 comme un remplissage couleur général.
