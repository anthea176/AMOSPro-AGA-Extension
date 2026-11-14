# C2P-3 / R77 - contrat approuve : Aga C2P Close

**Decision auteur, 14/11/2026 :** contrat Close approuve. Implementer R77 avant R78 Blit, puis une seule Gate C Compiler en fin de chantier C2P. R73 reste LAST_GOOD; R76 v0.13.21 est la base qualifiee A/B.

## Signature

~~~amos
_OK=Aga C2P Close
~~~

Fonction entiere sans parametre. Retourne **1** lorsque le contexte a ete libere, **0** si aucun contexte C2P n'est actif ou si ses champs sont incomplets. La banque chunky AMOS n'est jamais effacee.

## Effets et securite

- Ne ferme pas l'ecran AGA, ne modifie ni la palette, ni le front/back, ni le double buffer.
- Utilise le DBState de R74/R76 : State+32 -> DBState; +24 LibraryBase, +28 Context, +32 Bank, +36 Depth, +40 cookie C2P1.
- Sur un contexte valide : capturer LibraryBase/Context, effacer **tous** les champs d'appartenance avant les appels destructifs, puis WaitBlit (si graphics.library disponible), DestroyContext et CloseLibrary. Le contexte SDK possede le bitmap Chip : ne pas le liberer separement.
- Eviter toute double liberation par un second C2P Close, un Screen Close ou End. Convert retourne 0 apres Close; Open peut reinitialiser sur le meme ecran.
- La routine automatique de R74 n'est pas modifiee : la nouvelle entree native applique ses memes conventions de propriete sans inserer de code avant les donnees statiques clavier/souris. Les sept LEA de R76 doivent rester pointes sur $2F26.

## Retours attendus

| Situation | Retour |
|---|---|
| Open -> Close | 1 |
| Second Close | 0, sans effet |
| Close sans contexte | 0 |
| Convert apres Close | 0 |
| Open apres Close sur le meme ecran | 1 |
| Screen Close / End apres Close | Pas de deuxieme destruction SDK |

## Validation

- Gate A native : vrais octets M68000/020, ABI D3/D2/A3, registres et pile, cookie, nettoyage, double Close, ouverture apres Close, Convert apres Close, canaries, preserve buffers, liens AP20 V2 et audit des sept LEA.
- Gate B WinUAE : **un seul ASC actif**, fichier texte RAM avec mode, CPU Exec, 5 profondeurs, Close x2, Open apres Close, Convert apres Close, memoire stable, retour End sans boucle finale.
- Gate C Compiler : une seule qualification a la fin des fonctions C2P; Gate D Amiga physique distincte.
- Ne pas promouvoir R73 LAST_GOOD sans nouvelle autorisation explicite.

[Gate B R76](C2P_R76_CONVERT_WINUAE_GATE_B_2026-11-14.md) | [Regles](../EXTENSION_SOURCE_RULES.md)

## Implementation native et Gate A (14/11/2026)

La candidate R77 v0.13.22 porte **67 commandes / 74 AP20**, **54 360 octets**, SHA256 `81940e4950f8c21237fb3a9a033f3df0fee4ffaae0d959231ecb20df0d51af11`, base R76 strictement append-only. `tools/build_c2p_r77_close.py` genere les octets de maniere deterministe ; `tools/test_c2p_r77_close_gate_a.py` valide **12 scenarios CPU natifs**. L'ancienne panne R74/R75 est controlee : sept LEA clavier/souris inchanges, cible `$2F26`.

**Gate A native PASS ; Gate B fonctionnelle WinUAE PASS** (journal auteur : 5/5 profondeurs, `C2P_CLOSE_OK 5`, `EMPTY_CLOSE_OK 5`, `REOPEN_OK 5`, `ERR 0`, Chip Free delta 0). Fast Free +81 944 octets, coherent avec une banque chunky encore presente apres un Ctrl+C sur un essai precedent ; detail des 24 octets supplementaires non prouve. **Gate C Compiler et D physique NON TESTEES.** [Rapport R77 WinUAE](C2P_R77_CLOSE_WINUAE_GATE_B_2026-11-14.md). La premiere version du banc de test faisait ecrire le bitmap simule dans le corps du code Open a 7 plans ; la simulation a ete isolee sans alterer l'implementation native ni supprimer le test de reouverture. Ne pas deduire une Gate B du seul test CPU.

## Correction de l'ASC apres Gate B

Le programme de test ne faisait pas `Amos To Back` avant `Aga Key` : Echap n'etait plus recu sur l'ecran AGA lorsque AMOS etait au premier plan. L'auteur a explique un Ctrl+C sur l'essai precedent, expliquant plausiblement la banque de 81 920 octets liberee au lancement suivant. `tests/current/C2P_R77_CLOSE_01.asc` contient maintenant `Amos To Back` avant la pause et conserve `Amos To Front` apres `Aga Screen Close`. Le preflight verifie cet ordre, mais **la correction ASC n'est pas encore passee sous WinUAE**. Aucune modification de la library R77 n'a ete necessaire.
