# M19 — Cinquième unité native AP20 V2 : Gate A MC68020 (17/11/2026)

## Objectif et contrainte

Démontrer une **cinquième unité V2 réellement appelable**, avec une entrée native **au-delà de l'offset signé 32 Kio**, sans déplacer les quatre unités déjà validées par le scénario B/C de Bob Blit. **Ne pas remplacer** la bibliothèque installable ni l'ASC actif pendant cette Gate A : aucune autorisation distincte de bascule B/C n'a été donnée.

La source est construite de manière déterministe à partir du [builder AP20 V2 à quatre îlots](../tools/build_m19_ap20_islands_in_memory.py) dont la bibliothèque canonique est **96 908 octets**, SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`. Le source natif de la nouvelle unité est **écrit explicitement**, pas reconstruit depuis une bibliothèque binaire.

## Implémentation source-only sur `main`

- [Émetteur natif](../tools/m19_ap20_unit5_emit.py), **cible déclarée MC68020/68EC020 minimum** : 41 026 octets de code + données ; source SHA256 `86a32352847145f9964ad4c1fd49e210b00a69274ef8e3613e78569a10be57bd`.
- [Builder de la candidate](../tools/build_m19_ap20_unit5_in_memory.py) : append **à la fin** des 178 entrées AP20 déjà présentes, sans toucher leurs octets. Deux stubs publics de 8 octets chacun et un groupe natif V2 supplémentaire (dispatcher 34 octets) sont ajoutés ; les tokens existants restent identiques et conservent leurs indices. Aucun `GetP` nouveau : les deux fonctions de diagnostic n'ont pas d'argument.
- [Banc MC68020](../tools/test_m19_ap20_unit5_gate_a.py) : HUNK/AP20 et token ABI, invariance des 178 sections et des quatre groupes, portée PC16, désassemblage des zones exécutables, vraie exécution Unicorn MC68020 de l'algorithme, contrôle de pile/registres, interpréteur simulé et deux relocalisations Compiler simulées.
- [Workflow Gate A M19](../.github/workflows/m19-p0a-r88-get-gate-a.yml), incluant la suite des tests historiques.

**Nouvelles fonctions expérimentales uniquement** : `Aga Unit Five Sum()` renvoie en `D3` la somme non signée de **40 960 octets réellement lus** depuis sa table privée (valeur attendue `$004FB000`, avec `D2=0`) ; `Aga Unit Five Tail()` renvoie `$005A0205` (`D2=0`), à un offset interne `$A034`. Ces commandes servent à **mettre à l'épreuve AP20/Compiler** ; elles ne sont **pas** une API graphique de production, ni un moteur de Sprites.

## Résultat de la reconstruction

| Propriété | Active : quatre unités | En mémoire : cinq unités |
|---|---:|---:|
| Taille HUNK/AP20 | 96 908 octets | **138 044 octets** |
| SHA256 | `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56` | **`967a03f7a955f295f41b9391f8743d6e081305ca96084cd907b9d7603039dbe1`** |
| Commandes publiques | 85 | **87**, dont deux probes sans argument |
| Entrées AP20 | 178 | **181** |
| Groupes natifs AP20 | 142, 153, 156, 177 | **142, 153, 156, 177, 180** |
| Anciennes unités | 4 groupes | **4 groupes octet pour octet, mêmes offsets relatifs** |
| Nouvelle unité | — | **41 060 octets** (34 de V2 + 41 026 de code/données) |
| Table contrôlée | — | **40 960 octets** (40 Kio) |
| Offset natif profond (uint16) | — | **41 012 / `$A034`** |
| Maximum des liaisons PC16 AMOS | 854 octets | **854 octets, inchangé** |
| Nouveaux `Rbsr` vers groupe 180 | — | **14 et 6 octets de portée** |

L'expression « sans déplacer » signifie ici **préfixe intégral inchangé du code AP20 concaténé** et **indices / octets des unités existantes inchangés**. Le segment de tokens HUNK s'allonge, donc les positions absolues dans le *fichier* ainsi que les adresses réelles après chargement ne sont pas prétendues fixes.

## Preuves et statut des Gates

**Gate A ciblée MC68020 : PASS**, [exécution GitHub Actions 44135037050](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44135037050). Le banc confirme :
- l'exécution réelle des deux fonctions de la cinquième unité, jusqu'au retour au faux appelant AMOS ; retour `D3` correct, type entier `D2=0`, pile et `D0/D1/D4/A0` préservés ;
- les **40 960 octets parcourus**, et un contrôle négatif dans lequel changer un octet de la table change effectivement la somme retournée ;
- l'entrée à **41 012 octets** exécutée au travers du dispatcher V2 sans interpréter ce déplacement comme signé ;
- le lien `Rbsr` AMOS simulé et le modèle de `JSR.L` Compiler à **deux adresses natives éloignées** ; contrôles négatifs (offset impair, hors limites, branchement vers mauvais groupe) refusés ;
- le respect de la limite Compiler **65 534 octets par unité**.

**Gates B Runtime et C véritable AMOS Compiler V2 de cette candidate : NON TESTÉES ; Gate D physique : NON TESTÉE.** Un test de relocation par Unicorn n'est **pas** une exécution avec le Compiler réel : les anciens B/C PASS concernent exclusivement la bibliothèque **à quatre unités** et l'ASC actif `M19_AP20_ISLANDS_01.asc`.

**Protection :** `dist/AMOSPro_AGA.Lib` **96 908 octets** inchangée ; `tests/current/M19_AP20_ISLANDS_01.asc` unique et inchangé ; `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84 **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, protégée. Aucune copie installable alternative, ZIP, archive, branche ou promotion.

## Étape suivante (uniquement après autorisation explicite de bascule)

Pour passer les vraies Gates B/C sur les **cinq unités**, basculer ensuite dans **l'unique** `dist/AMOSPro_AGA.Lib` avec SHA exact `967a03f7a955f295f41b9391f8743d6e081305ca96084cd907b9d7603039dbe1`, et préparer **un seul ASC actif** qui appelle vraiment les deux fonctions de diagnostic, puis revalide les quatre Bobs. Le SHA de la **copie installée** dans `APSystem` devra être vérifié indépendamment, les deux journaux et la capture du compilé comparés ; ne jamais proclamer une Gate C à partir de la CI Gate A.
