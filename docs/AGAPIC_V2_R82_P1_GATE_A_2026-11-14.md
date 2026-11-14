# AGAPIC v2 / R82 — P1 natif partiel, Gate A cible PASS (14/11/2026)

## Etat et preuves

**R82 n'est PAS une bibliothèque candidate installable.** La version validée reste
R81 v0.13.26, SHA256 `9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4`.
Aucun fichier `dist/`, `tests/current/`, `tests/passed/` ni archive historique
n'a été modifié. Branche unique `main`.

**CI ciblée Gate A PASS** :
[Artifact integrity / job agapic_v2_p1](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43626780469).
Le job général `verify` est une vérification distincte, à contrôler séparément.

| Test | Résultat | Limite |
|---|---|---|
| Host AGAPIC v1/v2 et palette | 168 aller-retours PASS, 23 cas négatifs | Simulation Python |
| Garde de taille Compiler | 14 PASS | Modèle indépendant, pas une compilation AMOS |
| Décodeur/dessin natif AGAPIC v1/v2 | **69 scénarios MC68020 PASS**, incluant ModeID, pixels, masques, rejets, ABI et refus CPU000 | Standalone, pas encore raccordé au .Lib installable |
| Wrappers `Bank Palette Init/Capture` | **52 exécutions MC68020 PASS**, résolution de banque simulée, `BSR.L` hors plage signée 16 bits, ABI, refus CPU000 | Pas encore de tokens publics / pas de test WinUAE |
| Constructeur `build_agapic_v2_r82_preview.py` | Structure AP20 V2, 70 commandes, 77 entrées, liens réajustés PASS | Remplace l'entrée native image en **mémoire uniquement**, pas une R82 complète |

## Limite Compiler et liens

Référence R81 : monolithe 57 034 octets, marge 8 500 octets sous 65 534.
Simulation **image seule** R82 : 57 456 octets, **marge 8 078 octets**,
croissance de l'entrée Image Draw de **422 octets**.
Bibliothèque temporaire **en mémoire seulement** : 60 416 octets,
SHA256 `b6d46a9bf8f49d13d05e9dd5d6d70614984036b6577ee89ebec0c2be873f3eda`
(ce SHA n'est pas celui d'un fichier installable dans le dépôt).
Entrées natives réajustées 20, 55, 57, 58 ; état clavier/souris et
références C2P vérifiés. Le plafond de 65 534 octets est toujours obligatoire.

Les wrappers Init/Capture utilisent `Bnk.GetAdr` index 797 et `BSR.L`
MC68020 pour joindre les anciennes routines situées au-delà de
la portée de `BSR.W`. Garde `AFF_68020` précoce.

## Corrections trouvées par la Gate A

- Dispatch `Version=1` : **BEQ**, pas BNE.
- Les deux refus `INVALID_ID = $FFFFFFFF` : **BEQ**, pas BNE.
- Les flags v2 palette/masque sont distincts : transmettre uniquement
  le bit 0 à l'ancien painter 020.
- Le test CPU000 doit utiliser `ExecBase.AttnFlags=0` sur CPU68000,
  pas annoncer artificiellement un 68020.

## Reste à faire — non qualifié

1. Développer les deux wrappers **Apply** et **Fade** qui dispatchent
   AGAPAL v1 ou palette embarquée AGAPIC v2 (index0, ModeID strict).
2. Vérifier le chemin v2 des autres opérations AGAPIC pertinentes,
   notamment `Aga Image Region`, sans casser v1.
3. Intégrer les quatre nouveaux tokens AP20 et reconstruire **la candidate
   complète**, sous le budget de 65 534 octets avec tous liens audités.
4. Exécuter Gate A complète/CI (surface publique et ABI), créer le seul
   `tests/current/*.asc` actif avec journal RAM, puis Gate B WinUAE
   interprété et Gate C Compiler en fin de chantier.
5. R81 `LAST_GOOD` reste protégée jusqu'aux validations et accord de
   promotion ; Gate D Amiga réel séparée.

**Ne pas installer ni promouvoir le constructeur image-only R82 :**
il sert de preuve structurale et ne contient pas les API palettes prévues.
