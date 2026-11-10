# R10 — ordre de bascule AMOS / Intuition (test sans changer la Lib)

**RÉSULTAT OBSERVÉ (10/11/2026) : STRICTEMENT PAREIL.** La position de l'écran Jeff reste trop basse. Le test d'ordre `Amos To Back` est **NON CONCLUANT sur la cause** et son hypothèse est écartée. Le test a été archivé dans `tests/historical/`. Une erreur indépendante de registre A0 dans le second `OpenScreenTagList` a été identifiée ; voir `docs/R12_NEWSCREEN_A0.md`. Aucun autre essai de cet ordre n'est justifié.

Date : 10 novembre 2026. Branche : `codex/intuition-input-r1`. **Diagnostic préparé, NON TESTÉ sous WinUAE.**

## Faits conservés

- R10 0.6.1 est la **version active et LAST_GOOD**, 8 852 octets, SHA256 `e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3`.
- R10 ouvre Jeff-Flag 736×482 via repli NTSC vers PAL ; IFF Load, Double Buffer, Swap, Wait Key et fermeture fonctionnent. L'écran apparaît bas, avec le Workbench visible au-dessus ; l'utilisateur peut le remonter manuellement.
- R11 a ajouté `ScreenToFront` puis `MoveScreen` **avant OpenWindow** : l'utilisateur constate un écran gris. Cette version a été rejetée, sans diagnostic prouvant précisément la cause. Ne pas la réutiliser.
- Selon les Autodocs AmigaOS 3.1, **avec une hauteur explicite, le défaut de `SA_Top` est zéro** dans `OpenScreenTagList`. Ajouter simplement `SA_Top=0` ne corrigerait probablement rien.
- Le code officiel AMOS Professional `+W.s`, routine `TAMOSWb` (vers lignes 9727–9820), indique que `AMOS To Back` restitue le Copper/Workbench et restaure des registres matériels. Ce n'est donc **pas** simplement `ScreenToBack`. Il faut vérifier les interactions avec l'ouverture d'un nouvel écran Intuition.

Sources :
- <https://github.com/AOZ-Studio/AMOS-Professional-Official/blob/master/%2BW.s> — routine `TAMOSWb` (`Goto workbench`).
- <https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node03D3.html> — défauts `SA_Top` et `SA_Height`.
- <https://wiki.amigaos.net/wiki/Intuition_Screens> — ordre et mouvement des écrans.

## Hypothèse isolée : ordre d'AMOS To Back

Test **unique** : [`tests/current/R10_JEFF_AMOS_BACK_BEFORE_OPEN.asc`](../tests/current/R10_JEFF_AMOS_BACK_BEFORE_OPEN.asc).

Bandeau affiché : `R10-JEFF-AMOS-BACK-ORDER-01`.

Le test reprend exactement le parcours de `tests/historical/R10_JEFF_MODE_FALLBACK.asc`, sans changer les commandes AGA, **à une différence déterminante près** :

Avant :
```amos
_OPEN=Aga Screen Open(_W,_H,_COLORS,_MODE)
...
_SWAP=Aga Swap
...
Amos To Back
_K=Aga Wait Key
```

Maintenant :
```amos
Amos To Back
_OPEN=Aga Screen Open(_W,_H,_COLORS,_MODE)
...
_SWAP=Aga Swap
...
_K=Aga Wait Key
```

En cas d'ouverture échouée, le test appelle désormais `Amos To Front` avant de signaler l'échec, comme il le fait déjà sur les autres sorties anticipées.

**Mécanisme suspecté, non prouvé :** l'ancien ordre permettait à AMOS de reprendre la main au Copper **après** la création de l'écran Intuition ; le nouvel ordre rend l'affichage système à AmigaOS **avant** la création de l'écran AGA. On vérifie si cela règle le positionnement sans appel additionnel dans le binaire.

## Exécution et interprétation

1. Garder la Lib **R10 active**, ne pas réinstaller R11.
2. Charger **seulement** `tests/current/R10_JEFF_AMOS_BACK_BEFORE_OPEN.asc` dans AMOS. Choisir `Jeff-Flag.iff`.
3. Vérifier si l'image est visible au **bon emplacement dès le départ** et sans manipulation, puis appuyer sur une touche pour revenir à AMOS.
4. **Si Jeff passe**, relancer **le même test** avec Fallout.iff pour vérifier l'absence de régression PAL.

Résultats à consigner, séparément : `OPEN/DB/LOAD/SWAP/KEY/CLOSE`, position visuelle, retour à AMOS, et éventuel gel. Si le placement reste erroné, **ne pas créer une nouvelle Lib au hasard**. La prochaine mesure doit distinguer le `Screen.TopEdge` réel d'un empilement Workbench/AGA et du display clip.

## Statut des artefacts

- `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = R10 : **inchangés**.
- `dist/experimental/AMOSPro_AGA_M5_v0.6.2_JEFF_POSITION_R11.Lib` : **intact, rejeté**.
- `main` et le jalon historique M4b archivé : inchangés.
- Aucun nouveau builder, binaire ou token. PR #4 Draft ; aucune promotion avant observation WinUAE.
