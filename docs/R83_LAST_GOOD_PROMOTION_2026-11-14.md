# R83 v0.13.28 — Promotion LAST_GOOD (14/11/2026)

## Autorisation et artefacts

**Autorisation explicite utilisateur : « promotion ok ! »** après fourniture des journaux `C2P_R83_RUNTIME(1).TXT` et `C2P_R83_COMPILED(1).TXT`. Seule la promotion R83 est autorisée : aucun tag, GitHub Release, Aminet ou nouvelle branche.

- Branche : `main`.
- `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` : **copie d'un même blob Git** `0c862abe46b0cd0c552a688eef64162903b949d9`, 64 188 octets, SHA256 `01cc389fc5d28f306e52c7e4ec29b653d56c92807289c51731e685b0d3469feb`. **Aucune recompilation ni altération du binaire**.
- R83 : 74 commandes publiques, 83 entrées AP20, trois modules natifs : C2P 5 558, IFF 2 508, AGA/AGAPIC 52 974 octets. Pas de remplissage P5.
- R82 antérieure : 64 112 octets, SHA256 `b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36`, 74 commandes / 81 entrées AP20. Binaire conservé dans l'historique Git et reconstitué à l'identique par `tools/build_agapic_v2_r82_full_preview.py`, sans remplacer ni modifier une archive historique.
- `tools/build_aga_r83_modular.py` : reconstruit désormais R83 depuis le builder R82 SHA-épinglé, **indépendamment de la version mouvante du pointeur `LAST_GOOD`** ; vérifie le SHA256 final R83.
- Test R83 unique actif : `tests/current/C2P_R83_MODULAR_01.asc`. Copie identique, figée dans `tests/passed/C2P_R83_MODULAR_01.asc`. Ancien test R82 déjà archivé.

## Gates

| Validation | Verdict | Périmètre |
|---|---|---|
| Gate A CPU/CI | **PASS** | Tests natifs et structure AP20 MC68020, 3 modules |
| Gate B Runtime | **PASS** | WinUAE, `PRG_STATE 1`, CPU Exec 68030 |
| Gate C AMOS Compiler | **PASS** | WinUAE, `PRG_STATE -1`, CPU Exec 68030 |
| Strictement interprété | **NON TESTÉ** | `PRG_STATE 0` |
| Gate D Amiga physique | **NON TESTÉE** | Matériel réel |

Les journaux B et C rapportent `RESULT 1`, `VERDICT PASS`, IFF/Palette/Chunky/C2P/Blit/Zoom validés, 14/14 pixels, appels invalides rejetés, réouverture et Échap, `ERR 0`, deltas Chip/Fast **0/0** et `CLOSE_RETURNED`. Voir [rapport des deux journaux](C2P_R83_WINUAE_RUNTIME_COMPILER_2026-11-14.md).

**Limite :** la réussite WinUAE ne prouve ni les autres profondeurs sur cette R83, ni la compatibilité matérielle physique, ni des performances mesurées. La CI du commit de promotion doit être vérifiée séparément et ne doit pas être annoncée PASS avant résultat effectif.
