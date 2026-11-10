# Correction M3b v0.0.4 R1 — OPEN = 0

**Statut : nouveau candidat corrigé, 13/13 contrôles statiques réussis, PAS encore validé sous WinUAE.**

## Retour d'essai du 31 octobre 2026

L'utilisateur a exécuté `tests/M3B_320.asc` en interprété dans AMOS Professional 365 :

```text
AGA DETECT = -1
M3B OPEN = 0
OPEN FAILED (NO SCREEN DISPLAYED)
```

La détection CPU/chipset est positive ; la fonction d'ouverture retourne faux, avant le changement de visibilité d'AMOS.

## Cause établie dans le code

AMOS Pro v2+/365 transmet **le dernier argument à D3**, puis les précédents sur `(A3)+` en ordre inverse. L'ancien code lisait D3 comme largeur ; il comparait donc `$00021000` (ModeID PAL LowRes) à la largeur maximale autorisée et rejetait le mode.

Pour `Aga Screen Open(width,height,colors,modeID)` :

```asm
MOVE.L D3,D7       ; modeID
MOVE.L (A3)+,D6    ; colors
MOVE.L (A3)+,D5    ; height
MOVE.L (A3)+,D4    ; width
```

**Différence binaire R1 : quatre octets seulement** (offsets 866, 868, 870, 872) sur 1 564. Ancienne bibliothèque : `b602f90b8cd66c701f53d83014c0723cf74cbed73bdc5ecbd300dc9d40ed2af4`. Nouvelle bibliothèque : `206da625c7bd96eda6a4f024026ca3ae1f2d73ea52500c2aef580db34ef6e1a9`. Tous les autres octets, la table AP20 et le code M3a restent inchangés.

## Télécharger et installer

- [Bibliothèque expérimentale M3b R1](../dist/experimental/AMOSPro_AGA_M3b_v0.0.4_R1.Lib)
- [Générateur déterministe R1](../tools/build_m3b_r1.py)
- [Tests de non-régression R1](../tools/test_m3b_r1.py)
- [Programme AMOS de contrôle 320×256](../tests/M3B_320.asc)

Quitter AMOS, sauvegarder l'ancien `APSystem/AMOSPro_AGA.Lib` hors de `APSystem`, puis copier **la R1** sous le nom `AMOSPro_AGA.Lib` dans `APSystem/` de la copie de test. Garder le **slot 14** et relancer AMOS.

**Premier essai uniquement :** charger `M3B_320.asc` en interprété ; attendu : `M3B OPEN` non nul, dégradé visible après `Amos To Back`, puis retour à AMOS. Si OK, essayer le même programme compilé. **Ne pas essayer les autres modes si ce premier test ne fonctionne pas.**

### Retour arrière

La **M3a v0.0.3 validée** reste inchangée : [archive/AMOSPro_AGA_M3a_v0.0.3_WinUAE_OK.Lib](../archive/AMOSPro_AGA_M3a_v0.0.3_WinUAE_OK.Lib).

### Important

Le binaire M3b R1 est une adaptation HUNK déterministe ; ce n'est **pas** un assemblage Genam natif. Les 13 contrôles statiques ne constituent pas une preuve de fonctionnement sous WinUAE. Les hooks RESET/END et la consommation Chip RAM seront à valider après le premier écran.
