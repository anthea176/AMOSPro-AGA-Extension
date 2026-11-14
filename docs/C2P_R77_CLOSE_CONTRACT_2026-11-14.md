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
