# M19 S1-P1g — correction de la signature AP20

**24/11/2026.** Auteur : capture AMOS « Syntax error. » sur Get Aga Sprite, puis accord « GO ». S1-P1f est en échec de syntaxe (Gate B bloquée avant exécution). Aucune preuve de capture Runtime. Correctif livré sur main après Gate A AP20 ciblée PASS.

## Cause et correction

Le token get aga sprite a une entrée instruction 206 et une entrée fonction 1 (absente), mais une signature de fonction numérique `00,0,0,0,0,0`. Le contrat d'une instruction est `I0,0,0,0,0,0` ; le témoin Get AGA Bob utilise déjà `I0,0,0,0,0`. Aucun changement des six arguments, des piles ou des routines MC68020. L'ASC historique reste byte-exact.

Le [builder S1-P1g](../tools/build_m19_s1p1g_l2b_get_sprite_ap20.py) reconstruit P1f depuis ses sources, puis régénère ses déclarations Sprite à partir du socle L2b. Le contrôle strict `token_role_issues` vérifie la cohérence entrée instruction/fonction et signature pour toutes les commandes mono-rôle ; les anciennes signatures P1e/P1f sont conservées uniquement comme oracles historiques. Le [test](../tools/test_m19_s1p1g_token_gate_a.py) exige exactement une anomalie sur P1f, aucune sur P1g, et le même code dans les 208 unités.

| Identité | P1f historique (rejet syntaxe) | P1g correctif |
| --- | --- | --- |
| Taille | 142684 | 142684 |
| SHA256 | `dffe70c5550a4387b99901a2431892a2a7d6fe67328ab7cff8f69afd7ad91931` | `29788993d299c47d923ddce45ae2c9ae2cc3c98e510989a6975db3a3d10c6f66` |
| Blob | `3aa3fff1d5715d671e55abf2795c65b9345a1527` | `b45ea91d9d2133ed90704305a8da34cbee339507` |
| API | 102 / 208 | 102 / 208 |

Le delta est exactement 3 octets : 1 octet de signature et 2 octets de titre. Code et table AP20 identiques. LAST_GOOD L2b protégée, 136708 octets, blob `2809b4b409eea9e234df1b96bf2b08bd393d8c85`. Aucun changement ASM, ASC, archive ou release.

## Validation

Vérification indépendante du delta et des rôles en mémoire effectuée ; [Gate A AP20 ciblée PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45470002173) sur la source 085dd37130cef8f61853b5c398dae5a34ec04e7f. [Requalification native complète](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45470002362) séparée. La Gate A native P1f historique ne démontre pas la syntaxe réelle dans AMOS ; le prochain essai B doit être fait en réimportant le même GET_AGA_SPRITE.asc après redémarrage AMOS sur la Lib corrigée. C/D non testées. Ne pas lancer P1f.
