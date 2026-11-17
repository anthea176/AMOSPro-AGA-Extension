# M19 P0j-b6 — fonction numérique Aga Bob Draw (source-only)

**Cible MC68020/68EC020 minimum ; Gate A EN ATTENTE.** Cette expérimentation ne modifie **aucun octet du code natif B5** et n'installe rien. Les Gates B Runtime WinUAE, C véritable AMOS Compiler et D matériel ne sont pas effectuées.

## Origine et API

- Source de vérité : [builder B5](../tools/build_m19_p0j_swap_barrier_in_memory.py), candidate AP20 en mémoire de **101 460 octets**, SHA256 `a5a08853f331b7c70d8e71eb95911bee3d8944f18feb107fda2249f10477d55e` ; source BOBS MC68020 **20 944 octets**, SHA256 `d02eb6c89863fbb769d699296a923dc2997e2b39184c2c7d51800c28c10c1b5e`.
- Nouveau **token expérimental** : fonction numérique `_OK=Aga Bob Draw` sans argument, `aga bob draw` / signature `0` / `function=180`, `instruction=1`. Aucun `GetP` requis (zéro paramètre). Le stub de huit octets est ajouté à l'index AP20 180 et pointe vers `guarded_frame_draw_entry` dans l'îlot BOBS 177.
- Signification : `1` quand le dessin synchrone des Bobs actifs (slots 1..64) réussit dans le back buffer AGA, `0` en cas de refus ; retour natif `D2=0, D3=0/1`. Pas d'allocation Chip par Bob, pas de changement de banque sélectionnée, pas de Swap implicite.
- Le token existant `Aga Swap` continue d'utiliser **le garde B5** : une frame DIRTY retourne `0` avant tout `ChangeScreenBuffer`. Seule une fermeture AGA réussie permet de lever le verrou conservateur ; les réponses Safe/Disp en attente restent un risque à valider sur matériel.
- **Un seul nouveau token** : les 85 commandes anciennes, leurs 180 sections AP20 et les quatre unités natives doivent rester identiques. Aucun ASC actif, aucune bibliothèque ou LAST_GOOD touché.

## Gate A obligatoire

[Builder B6](../tools/build_m19_p0j_public_draw_in_memory.py) et [banc CPU020 B6](../tools/test_m19_p0j_public_draw_gate_a.py) : audit strict AP20/HUNK, token et signature `0`, portée PC16 et absence de mutation des unités. Exécution MC68020 des deux relocalisations (Rbsr interpréteur / JSR Compiler simulé) puis des sources natives sur deux implantations, en vérifiant ABI numérique 0/1, rendu masqué, refus de masque avant DMA et échec SafePort après un seul Bob. Le front doit rester intact et aucun `Aga Swap` du back partiel ne doit réussir.

**Limite explicite :** un modèle de dispatch compilé ne démontre pas que le *véritable* AMOS Compiler V2 reconnaîtra la nouvelle fonction, ni que l'écran réel et Close/End/Swap seront corrects sous WinUAE. Ces Gates devront être effectuées **après autorisation distincte de bascule canonique**, avec l'unique Lib/ASC actifs du dépôt. La présente Gate A ne constitue aucune permission de promotion ni de publication.
