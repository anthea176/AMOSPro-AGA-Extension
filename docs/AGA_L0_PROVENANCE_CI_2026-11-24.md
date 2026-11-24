# L0 — Fiabilisation provenance P2d / S1-P1e et CI

**24 novembre 2026 · main exclusivement · point de départ [5df1f67](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/5df1f675fb2479df46233b9fbe4467e6203dd77f).**

Autorisation : « super allons y » après le plan de correction de l'audit transversal. Lot L0 limité aux outils et workflows, sans nouveau code natif ni nouvelle bibliothèque. Aucun remplacement de dist, de l'ASC actif, des archives ou des preuves. Aucun transfert de Gates B/C historiques, Sprite toujours gelé.

## Échec constaté et périmètre
Le [dernier échec Artifact integrity](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45275935053/job/138047605608) du 23 novembre est un rejet dans test_compiler_bridge_v2_probe.py : "Current must be an exact SHA-pinned V2 library". Le contrôle ne reconnaît pas S1-P1e, déjà identifiée par verify_active. L'audit a également constaté la confusion active/LAST_GOOD dans les builders/sondes d'assemblage, le contrôle des sept LEA et certains workflows historiques. Le changement ne rend pas les anciennes versions artificiellement valides.

| Fichier canonique | Taille | SHA256 attendue |
|---|---:|---|
| dist/AMOSPro_AGA.Lib | 142000 | 1491ad72712bdee3761f0eb74818220db5daa8aaa5be0a526dc4d0888f252106 |
| dist/AMOSPro_AGA_LAST_GOOD.Lib | 136020 | ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f |

## Changements
- [774330b](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/774330bf849f77cff5d1cf50f4f1276eb2c92b66) : test_compiler_bridge_v2_probe.py ajoute S1-P1e à la liste strictement épinglée, branche spécifique avec verify_active, reconstruction P2d, comparaison des 203 entrées héritées et déplacements PC16. Les autres cas historiques restent inchangés. test_current_input_state_offsets.py vérifie P2d reconstruite et protégée, S1 doit conserver les 203 entrées dont UNIT142 ; contrôle historique R82 des sept LEA et huit mutations conservé, displacement 12070 attendu. Workflows P1b, P2b/c/d : contrôle historique de leur propre builder, LAST_GOOD P2d et active via verify_active.
- [948ad10](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/948ad100abed05888852c03da287263d8b334876) : build_m19_p2d_editable_asm.py et huit sondes UNIT142 : entrée = LAST_GOOD P2d, taille et SHA strictes conservées. Le workflow editable ASM contrôle les deux identités sans exiger leur égalité. Aucun changement natif ou binaire.
- Exporteur audit P2d : même cible LAST_GOOD et préservation des deux empreintes. Workflow d'export désormais en lecture seule, retrait de l'auto-commit des archives de migration, pin vasm au commit déjà utilisé par le workflow editable ASM. L'artefact historique de source ASM/JSON reste uniquement un résultat d'audit, jamais une bibliothèque installable.
- Précision de limite : compiler_bridge_v2_probe.MAX_UNIT_BYTES=65534 ; 60928 octets BOBS laissent 4606 octets arithmétiques, et non 4608 sur une limite de 65536. Cela ne garantit pas qu'une extension arbitraire reste relogeable.

## Contrôles attendus après publication
Les CI déclenchées par ces commits doivent exécuter les tests existants, notamment la policy CPU/delivery, l'intégrité, la relocation Compiler simulée, les sept LEA, et la reconstruction P2d. Consulter les résultats par SHA exacte. **Pas de PASS annoncé avant exécution.** Pas de build local complet : le conteneur n'a pas d'accès réseau au clone GitHub. Pas de Gate B/C/D. Le dernier PASS historique de P2d reste limité au banc intégré exact.

L0 n'efface pas AGA-001/002/010 ni les autres points du bilan. AGA-005 : correctifs de ciblage enregistrés, qualification CI restante. AGA-012 (README tests/current et éventuelles mentions historiques) non modifiée dans ce lot pour conserver toute la campagne intacte. La régression de référence B/C nécessite WinUAE réel et une décision distincte d'installation. **L1 : IFF Load / Back Fill SafePort, après retour CI et vérification de l'autorité source.** Aucun changement natif, aucune nouvelle Lib, aucune promotion autorisée par ce document.

## Retour CI intermédiaire et correction documentaire

Les politiques CPU/delivery des trois commits L0 sont PASS (45396953234, 45396999222, 45397073540). Les régressions P2b Flip et P2c Planes sont PASS (45396953245, 45396953569). Le [workflow docs 45397073541](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45397073541) a vérifié les 102 commandes des deux README, les 17 exemples et le préflight statique ASC, mais échoué sur la taille de ROADMAP.md (9211 caractères > 9000). Correction : condenser l'historique des passages en renvois aux rapports conservés, sans relever la limite ni modifier le test. Les autres jobs étaient encore en cours lors de ce relevé ; aucun résultat final n'est anticipé.

## Retour CI final du premier lot et complément L0

PASS : [ASM éditable 45396999267](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45396999267), [P2d Bob 45397073925](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45397073925), [export ASM 45397073844](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45397073844), [docs 45397242933](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45397242933). Artifact integrity 45396999217 a passé le premier bloc relocation V2 puis échoué au test d'export monolithique : S1-P1e doit être explicitement **refusée par l'ancien exporteur** tout en vérifiant sa filiation P2d. Correction ciblée du test et des seeds historiques ; aucun changement du refus fail-closed de l'exporteur. Nouvelle CI à lire ; L0 pas encore globalement PASS.

Le test historique R88 (run 45398721032) exigeait encore active==LAST_GOOD==P2d dans son workflow, bien que le test source R88 préalable soit PASS. Le workflow vérifie désormais le SHA R88 historique, la SHA P2d protégée et l'identité active via verify_active. vasm épinglé au même commit que l'ASM P2d. Pas de changement R88 ou Lib. Nouvelle CI à lire.

[CI R88 45399258873](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45399258873) PASS après correction de la cible. La reconstruction source P2d-L1 est PASS indépendamment. Artifact integrity globale encore en cours au dernier relevé (45399337115) ; ne pas assimiler L0 à une validation globale.
