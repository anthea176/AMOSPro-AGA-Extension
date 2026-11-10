# M4a v0.0.5 — Aga Wait Vbl

**Statut : VALIDÉ sous WinUAE en interprété ET en compilé le 09/11/2026. 11/11 contrôles statiques OK.**

M4a ajoute :

```amos
Aga Wait Vbl
```

La routine réutilise le `graphics.library` stocké par `Aga Screen Open` et appelle `graphics.library/WaitTOF()` (LVO -270). Sans écran ouvert, la commande est un no-op sûr.

## Validation

Le test `tests/M4A_WAITVBL.asc` a passé :

```text
WAIT WITHOUT SCREEN = OK
M4A OPEN = 1
WAIT VBL 150 FRAMES = OK
M4A CLOSED - BACK IN AMOS
```

Le même programme passe également **compilé**.

## Version figée

- binaire validé : `archive/AMOSPro_AGA_M4a_v0.0.5_WinUAE_OK.Lib`
- SHA256 : `ae4b863083e32c38e85192ac760aa143d3585c51d600449056075111da213b0e`

M4a devient la base de retour arrière pour M4b.

## Suite

[M4b](M4B_DOUBLEBUFFER.md) ajoute le double buffering Intuition, le dessin dans le back buffer et `Aga Swap`.
