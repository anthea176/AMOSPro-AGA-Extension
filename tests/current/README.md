# Tests courants — aucun ASC actif après validation P2

**La campagne M19 P2a–P2e est terminée et promue en exemple, sur demande explicite du 21 novembre 2026.** Il n'y a actuellement **aucun programme ASC de campagne sous `tests/current/`**. Il est inutile de relancer l'ancienne source depuis cet emplacement ; cela évite de confondre exemple public, source de régression figée et prochaine campagne.

- [**Exemple public P2 ALL IN ONE**](../../examples/bob_p2_all_in_one/README.fr.md) · [ASC identique de 25 056 octets](../../examples/bob_p2_all_in_one/M19_P2_ALL_IN_ONE.asc).
- [**Source de test figée dans `tests/passed/`**](../passed/M19_P2_ALL_IN_ONE.asc), octets strictement identiques à l'exemple, Git blob `c48d334fd4508d402d28399bffdfec08d4cb4acb`.
- [Rapport B/C](../../docs/M19_P2_ALL_IN_ONE_2026-11-21.md) et [journaux exacts](../../docs/evidence/M19_P2_ALL_IN_ONE_RUNTIME_PASS_2026-11-21.TXT) ([Compiler](../../docs/evidence/M19_P2_ALL_IN_ONE_COMPILED_PASS_2026-11-21.TXT)).
- Bibliothèque courante P2d `dist/AMOSPro_AGA.Lib` **inchangée**, 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`; `LAST_GOOD` P1e protégée.

**Résultat constaté sous WinUAE : Gates B Runtime et C AMOS Compiler PASS** sur l'ASC identique (`RESULT 1`, `ERR 0`, 240 cycles AMAL, 252 Swaps, 8 collisions, 20 pixels Flip, 10 pixels Plans, fermeture OK). **121 refus de Swap récupérés** après un VBL chacun dans les deux modes ; ne pas les masquer. Gate D physique et interprété strict non testés.

Les fichiers binaires de ressources qui restent dans `tests/current/` sont des artefacts historiques d'autres campagnes, pas un programme actif. La prochaine campagne créera son **unique ASC** ici lorsqu'elle sera effectivement décidée. **Ne pas inventer ou restaurer un ancien ASC simplement pour satisfaire un contrôle CI.**
