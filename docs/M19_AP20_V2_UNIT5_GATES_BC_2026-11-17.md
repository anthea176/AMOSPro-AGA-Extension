# M19 AP20 V2 — vraie validation B/C de la cinquième unité (17/11/2026)

## Périmètre et provenance

Deux journaux fournis par l'auteur le 17 novembre 2026, provenant du **même ASC** `M19_AP20_UNIT5_01.asc` et de la candidate cinq unités installée pendant cette campagne :

- **Bibliothèque testée (identité annoncée dans l'ASC)** : `dist/AMOSPro_AGA.Lib`, 138 044 octets, SHA256 attendu `967a03f7a955f295f41b9391f8743d6e081305ca96084cd907b9d7603039dbe1`. 87 commandes dont deux sondes temporaires, 181 entrées AP20, cinq unités natives ; dernier offset utile `$A034` (41 012).
- **Source exacte de la bibliothèque de test** : commit [0b202d1](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/0b202d19691c4083a3325c74a37d3eb04857c6c1), builder [`build_m19_ap20_unit5_in_memory.py`](../tools/build_m19_ap20_unit5_in_memory.py) et émetteur [`m19_ap20_unit5_emit.py`](../tools/m19_ap20_unit5_emit.py). La preuve Gate A antérieure est dans [le rapport cinquième unité](M19_AP20_V2_FIFTH_UNIT_GATE_A_2026-11-17.md).
- **Runtime** : `M19_AP20_UNIT5_RUNTIME.TXT` ; SHA256 des 361 octets CRLF reçus : `7d5ab08503b183af41360898ce7dc45156135a3aecae6f997391730300801efe`.
- **Compiled** : `M19_AP20_UNIT5_COMPILED.TXT` ; SHA256 des 362 octets CRLF reçus : `ac85e8108e766fe03ea38b5a856b504550b2ac2c711940dc2438dae08d67c651`.

Le SHA écrit dans les journaux est une **chaîne littérale de l'ASC** ; il n'est pas un calcul indépendant de la copie effectivement chargée dans `APSystem`. La configuration complète et la version précise du Compiler ne figurent pas dans les TXT. L'auteur confirme avoir exécuté la version compilée.

## Résultats observés

| Ligne du journal | Runtime (Gate B) | Vrai Compiler (Gate C) |
|---|---:|---:|
| `RUN_MODE` / `PRG_STATE` | `RUNTIME` / `1` | `COMPILED` / `-1` |
| `UNIT5_SUM` | 5222400 | 5222400 |
| `UNIT5_TAIL` | 5898757 | 5898757 |
| `UNIT5_OK` | 1 | 1 |
| `RESULT` / `ERR` | 1 / 0 | 1 / 0 |
| `VERDICT` | PASS | PASS |
| `IMAGE_COUNT` | 2 | 2 |
| `BANK_LENGTH` | 1036 | 1036 |
| `MASK_FLAG` | 1 | 1 |
| `BLIT1` / `BLIT2` | 1 / 1 | 1 / 1 |
| `CLIP_LEFT` / `CLIP_RIGHT` | 1 / 1 | 1 / 1 |
| `MISSING_IMAGE` | 0 | 0 |
| `SWAP` / `CLOSE` | 1 / 1 | 1 / 1 |

**Gate A MC68020 : PASS** sur la candidate reconstruite ; **Gate B Runtime : PASS sur le journal utilisateur** ; **Gate C véritable AMOS Compiler V2 : PASS sur le journal utilisateur (`PRG_STATE -1`)** pour ce scénario. **Gate D Amiga physique : NON TESTÉE.**

### Limite de preuve visuelle

L'auteur a indiqué que l'image était **identique à celle de la précédente bibliothèque à quatre unités**, mais **n'a pas enregistré de nouvelle capture** de la cinquième unité. Cette observation est conservée en tant que retour utilisateur, pas comme une vérification indépendante des pixels de cette nouvelle version. Les journaux prouvent les valeurs et retours testés ; ils ne constituent pas une mesure pixel-exacte ni une analyse mémoire exhaustive.

## Nettoyage autorisé après les Gates B/C

La cinquième unité contient **exclusivement** deux fonctions de diagnostic et **40 Kio de données de test**. Aucune autre fonction de production ne dépend de cette unité. L'auteur a autorisé la suppression des probes après les résultats B/C.

**Décision d'intégration conservatrice :** ne pas distribuer de cinquième unité vide ni conserver un bloc de données inutile. L'unique bibliothèque active revient à la **source vérifiée à quatre unités**, exactement **96 908 octets / SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`**, avec **85 commandes, 178 entrées AP20 et quatre unités natives**. Le seul ASC actif redevient `tests/current/M19_AP20_ISLANDS_01.asc` dont les Gates B/C avaient déjà PASS pour **ce même binaire exact** ([preuve quatre unités](M19_AP20_V2_GATES_BC_2026-11-17.md)). Ce n'est pas une promotion `LAST_GOOD`.

Le **test de cinq unités, sa construction native MC68020 et ses résultats B/C restent vérifiables dans l'historique Git** au commit cité ci-dessus. Les deux tokens et leurs stubs, la table de 40 Kio et l'unité de diagnostic ne figurent plus dans la bibliothèque installable. Les sources des tests historiques restent présentes pour audit/reproduction, sans être une seconde distribution installable.

**Prochaine véritable cinquième unité :** la créer à partir d'une fonction native utile, avec une nouvelle preuve Gate A et de nouvelles Gates B/C. Ne jamais attribuer les PASS de cette unité de diagnostic à un futur code graphique.

**Protection :** R84 `dist/AMOSPro_AGA_LAST_GOOD.Lib`, 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d` et archives inchangés ; aucune promotion automatique.
