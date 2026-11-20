# M19 P1b — Hot Spot, premier jalon natif MC68020 (source-only)

**21 novembre 2026 — branche `main` uniquement. Statut : PASS des tests de la primitive native et du modèle à double buffering ; le Safe Blitter P1a n'est pas encore raccordé.**

## 1. Contexte source vérifié

- **Lib installable active** : P1a, [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **118 816 octets**, SHA256 `165a24edcd4c00074d6ddce4a98317f720ed3236d61ba006333574743b55063a`, 92 commandes/188 entrées AP20. **Aucune modification dans P1b**.
- **`LAST_GOOD` P0 protégée** : [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../dist/AMOSPro_AGA_LAST_GOOD.Lib), **117 896 octets**, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`. **Non remplacée**.
- **Gate B P1a : PASS fonctionnel** sur deux journaux WinUAE différents et une capture à l'étape 4/9 ([rapport Gate B](M19_P1A_RUNTIME_B_2026-11-21.md)). Gates C vrai AMOS Compiler et D Amiga physique **non testées** pour P1a.
- **Format AGBO v1 existant**, sans ajout ni changement : enregistrement de **40 octets** par image, hotspots signés **16 bits** à l'offset **+28 / +30** ; le champ `generation` en tête augmente lors d'une modification `set_hotspot`. Le staging P0c vérifie déjà dimensions, plans, masques, réservés et identité/génération avant la copie des seuls pixels/masques en Chip.
- **Trajet natif existant** : `explicit_frame_draw_entry` lit le Bob et son bank/image/X/Y, prépare la source AGBO originale, appelle `explicit_safe_blit_entry` qui résout l'image et rejoint `draw_live_image_resolved` du Safe Blitter P0d. Le pinceau final reçoit les coordonnées signées de dessin et gère clipping pixel, masque, tampon arrière et `WaitBlit`. Les hotspots ne sont **pas encore soustraits** sur ce trajet.

## 2. Code livré, sans modifier P0/P1a

| Source | Fonction |
| --- | --- |
| [`m19_p1b_hotspot_origin_emit.py`](../tools/m19_p1b_hotspot_origin_emit.py) | Émet une vraie primitive **MC68020** `p1b_hotspot_origin_entry`. Lecture big-endian des deux mots signés AGBO (+28/+30), `EXT.L`, soustraction 32 bits et garde du clipping |
| [`m19_p1b_hotspot_draw_model.py`](../tools/m19_p1b_hotspot_draw_model.py) | Modèle **source-only** du rendu avec origine hotspot, conservant les positions logiques Bob et le cycle P0 `Clear → Update → Swap` sur deux pages |
| [`test_m19_p1b_hotspot_source_gate_a.py`](../tools/test_m19_p1b_hotspot_source_gate_a.py) | **258 exécutions natives** réparties sur deux implantations mémoire MC68020, plus tests de masques, clipping, pages, modifications de banque et équivalence à hotspot zéro |
| [`m19-p1b-hotspot-source-gate-a.yml`](../.github/workflows/m19-p1b-hotspot-source-gate-a.yml) | CI dédiée, contrôle CPU minimal, AST/bytecode Python, régressions AGBO P0 et Clear/Update P0, test natif M68k, protection de `dist/`, `tests/current/` et `tests/passed/` |

**Preuve :** [Gate A partielle P1b — CI 44835297656, PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44835297656), et [politique CPU / chemins 44835297650 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44835297650). Le premier essai de CI a révélé un **ordre incorrect SR/A7 dans le banc Unicorn** ; corrigé : passage en supervisor **avant** initialisation de la pile. Le correctif concerne le **banc d'essai**, non le code de hotspot, et la CI a ensuite passé les cinq tests.

## 3. Contrat interne du calcul de dessin

Entrée privée, **uniquement après validation de la banque / de l'image / des pointeurs par les helpers existants** :

- `A0` = pointeur d'entrée AGBO v1 de 40 octets **déjà validée** ; `A3` = deux longs dimensions logiques de l'écran **déjà vérifiés**.
- `D1` = X Bob logique, `D4` = Y Bob logique ; la table P0e et les getters P1a continuent à utiliser ces valeurs logiques.
- Calculs en **32 bits signés** : `Xdraw = Xbob - hotspot_x`, `Ydraw = Ybob - hotspot_y`.
- Si l'image intersecte le rectangle écran et que l'origine reste dans les limites acceptées par P0d (signed 16 bits), **`D3=1` et `D1/D4` reçoivent les coordonnées de dessin**.
- Si l'objet est **entièrement hors écran**, `D3=0`, `D1/D4` restent inchangés : le futur appelant devra traiter cette situation comme **un no-op réussi**, ne faire aucun DMA ni Swap implicite.
- `D0`, `D5..D7`, `A0..A6` et la pile sont préservés, `D2=0`. Aucun pointeur Chip n'est retenu, aucune allocation, modification AGBO, opération graphique ni interaction avec SafePort dans le helper.

**Limitation de contrat :** le helper ne sonde pas lui-même la validité des pointeurs `A0/A3` ; il ne doit **jamais** être exposé comme commande AMOS publique ou appelé avant les contrôles P0 existants.

## 4. Régressions de rendu vérifiées

Le modèle P1b conserve l'ordre croissant des IDs Bob, une image masquée conserve le décor pour les pixels transparents, un hotspot négatif déplace le dessin vers le bas/la droite, les origines négatives font un **clipping pixel exact**, et l'alternance `Update/Swap` sur deux pages ainsi que `Off` ne laissent pas de trace dans l'oracle hôte. À hotspot nul, le résultat est identique à celui du modèle historique P0. Recharger une banque AGBO avec une génération modifiée invalide les objets liés jusqu'à leur rebind ; le payload d'origine est immutable.

Les **258 cas natifs** comparent l'algèbre de coordonnées signées du code généré au modèle indépendant, sur deux placements mémoire, et contrôlent les registres AMOS préservés, la pile et l'absence de mutation du payload AGBO.

## 5. Ce qui RESTE AVANT de qualifier P1b comme rendu natif

1. Relier le **pointeur de l'entrée AGBO vérifiée** au calcul `p1b_hotspot_origin_entry` après `explicit_image_resolve_entry` ou point sûr équivalent, sans recopier le répertoire dans le cache Chip.
2. Dans le chemin privé de dessin, appeler le Safe Blitter original avec **uniquement les coordonnées de dessin ajustées**, en conservant X/Y logiques dans le registre de 64 Bobs pour `Aga X/Y Bob(N)`.
3. Traiter le cas **hors écran comme dessin réussi sans DMA**, sans déclencher faussement une trame DIRTY/échec, ni présenter un buffer qui a échoué.
4. Tester l'implantation complète MC68020 avec Blitter OS simulé : masques, plans 1..8, 64 Bobs, banque restagée après changement de génération, `Clear/Update/Swap` sur deux pages et gardes AGA/Owner/CPU/Chip.
5. Créer le **builder P1b entièrement en mémoire** puis obtenir une Gate A complète. **Aucune bascule de `dist/AMOSPro_AGA.Lib` ou de l'ASC**, et **aucune promotion de `LAST_GOOD`**, sans décision explicite distincte de l'auteur.

**Bilan :** P1b est **engagée** avec une primitive native MC68020 et un oracle de rendu à double buffering validés. **Le renderer natif P1a actuel ignore toujours les hotspots non nuls ; Gates B/C/D P1b NON TESTÉES.** La suite globale `Artifact integrity` reste rouge sur un contrôle historique de SHA active (`test_r73_last_good_promotion.py`) et ne doit pas être confondue avec cette CI P1b PASS.
