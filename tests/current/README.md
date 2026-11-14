# Test actif AMOS — R84 AGAPIC v1/v2 promue LAST_GOOD

**Unique ASC actif :** [AGAPIC_R84_V1_V2_01.asc](AGAPIC_R84_V1_V2_01.asc). Copie identique dans [tests/passed](../passed/AGAPIC_R84_V1_V2_01.asc).

**Binaire actif = LAST_GOOD :** R84 v0.13.29, **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d` ; 76 commandes / 85 entrées AP20, 3 modules natifs. R83 historique reconstructible via [builder](../../tools/build_aga_r83_modular.py) et [Git avant promotion](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/3c65fed54567d28c845979c23667585bd7cc6808/dist/AMOSPro_AGA_LAST_GOOD.Lib).

**Statut :** Gate A native CPU/CI **PASS** et Gate C AMOS Compiler **PASS** (programme compilé avec une banque ; deux passes 4/8 plans, `ERR 0`, `CLOSE_RETURNED 2`). Le journal compilé mesure Chip **0** et Fast **−11 920 octets**. Le banc conserve 4 ABK dans `RAM:` après les opérations Save/Load : ce delta n'établit pas une fuite native. Gate B Runtime corrigée **non attestée séparément** ; `PRG_STATE 0` strict et matériel réel non testés. Promotion R84 explicitement approuvée par l'auteur avec cette limite de preuve. **Aucune nouvelle exécution WinUAE n'est demandée.**

**Règle AMOS :** `Length(N)` sert aux tests d'existence de banques encore absentes. `Start(N)` sert uniquement à l'adresse d'une banque effectivement réservée (par exemple `_P11=Start(11)` puis `Leek(_P11+24)`). Remplacer ces `Start` par `Length` provoque des lectures invalides.

[Rapport de promotion](../../docs/AGAPIC_R84_LAST_GOOD_PROMOTION_2026-11-14.md) · [Gate C compilée](../../docs/AGAPIC_R84_COMPILER_GATE_C_2026-11-14.md) · [Gate A](../../docs/AGAPIC_R84_GATE_A_2026-11-14.md).
