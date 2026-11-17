# M19 P0i — rendu privé de Bobs persistants multi-banques

**Cible MC68020+ ; code source sur `main`, Gate A à vérifier.** Cette étape reprend exactement P0h (SHA256 `2c5c371754a3b54c797c7b413769ef2536db92cdad7eba3db8185bb88dea7782`), les routines P0c de préparation/cache Chip, le Blitter P0d Safe/WaitBlit et P0f/P0g d'identité des banques.

## Raccordement

Une routine privée `routed_paint_all_entry` lance d'abord **P0h sur tous les 64 objets**. Pour chaque Bob actif dans l'ordre 1..64, `routed_paint_one_entry` revalide la banque enregistrée, effectue `Bnk.GetAdr` sur **cette banque** plutôt que sur le choix courant, la prépare dans le cache Chip indépendant par banque si nécessaire, arme le callback End et peint synchroniquement dans le **back buffer Safe** via `safe_bank_blit_entry`, puis restaure la sélection privée originale. Ni nouvelle banque AMOS, ni `Aga Swap` implicite.

**Attention :** la route P0i expérimente une **projection temporaire du shadow privé `bank_active_state`**, restaurée sur tous les chemins de sortie. Le choix de banque utilisateur n'est pas changé de manière persistante, mais la méthode est **non réentrante** : aucun appel BOBS concurrent/interruption pendant la projection. Ce n'est pas encore le contrat définitif de `Aga Bob Draw`. Il faudra soit prouver l'absence de réentrance, soit fournir un chemin explicite par banque sans projection.

## Gate A ciblée

[Émetteur](../tools/m19_p0i_multibank_draw_emit.py), [builder source-only](../tools/build_m19_p0i_multibank_draw_in_memory.py), [test MC68020 pixel-exact](../tools/test_m19_p0i_multibank_draw_gate_a.py). Le banc doit exécuter deux vrais placements natifs V2 simulés, source bank10 puis bank11 avec sélection laissée à 11, vérifier ordre d'affichage, Chip cache sans copies inutiles, front non touché, absence Swap, refus des générations périmées, SafePort et libération Close.

**Statut :** Gate A en cours ; Gates B/C/D **NON TESTÉES**. En cas d'échec d'un dessin après le premier Bob, le back buffer peut être partiellement modifié : le code renvoie un refus et ne fait aucun Swap. Un futur Draw public exige une politique explicite de frame atomique et la gestion des images invalides avant DMA. La solution P0i n'est PAS une publication de commande.

**Protections :** seule `dist/AMOSPro_AGA.Lib` demeure la version 4 îlots **96 908 octets**, SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`, ASC `M19_AP20_ISLANDS_01.asc`, R84 LAST_GOOD et archives inchangés. Aucun WinUAE demandé avant autorisation distincte de la bascule canonique.
