# M19 P0j-b6 — fonction numérique Aga Bob Draw : Gate A PASS

**Cible MC68020/68EC020 minimum ; Gate A PASS : 52 contrôles sur deux implantations natives V2.** [GitHub Actions 44183835343](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44183835343), commit `6cd3329`. Candidate AP20 source-only **101 476 octets**, SHA256 `3843a3ea3fac05365d7773ed803ca4ab2c288db6fcecce0210b966151c6d2b91` ; **86 commandes, 181 sections AP20, 4 îlots natifs**, PC16 maximal **28 000 octets**. Cette expérimentation ne modifie **aucun octet du code natif B5** et n'installe rien. Les Gates B Runtime WinUAE, C véritable AMOS Compiler et D matériel ne sont pas effectuées.

## Origine et API

- Source de vérité : [builder B5](../tools/build_m19_p0j_swap_barrier_in_memory.py), candidate AP20 en mémoire de **101 460 octets**, SHA256 `a5a08853f331b7c70d8e71eb95911bee3d8944f18feb107fda2249f10477d55e` ; source BOBS MC68020 **20 944 octets**, SHA256 `d02eb6c89863fbb769d699296a923dc2997e2b39184c2c7d51800c28c10c1b5e`.
- Nouveau **token expérimental** : fonction numérique `_OK=Aga Bob Draw` sans argument, `aga bob draw` / signature `0` / `function=180`, `instruction=1`. Aucun `GetP` requis (zéro paramètre). Le stub de huit octets est ajouté à l'index AP20 180 et pointe vers `guarded_frame_draw_entry` dans l'îlot BOBS 177.
- Signification : `1` quand le dessin synchrone des Bobs actifs (slots 1..64) réussit dans le back buffer AGA, `0` en cas de refus ; retour natif `D2=0, D3=0/1`. Pas d'allocation Chip par Bob, pas de changement de banque sélectionnée, pas de Swap implicite.
- Le token existant `Aga Swap` continue d'utiliser **le garde B5** : une frame DIRTY retourne `0` avant tout `ChangeScreenBuffer`. Seule une fermeture AGA réussie permet de lever le verrou conservateur ; les réponses Safe/Disp en attente restent un risque à valider sur matériel.
- **Un seul nouveau token** : les 85 commandes anciennes, leurs 180 sections AP20 et les quatre unités natives doivent rester identiques. Aucun ASC actif, aucune bibliothèque ou LAST_GOOD touché.

## Gate A exécutée : PASS

[Builder B6](../tools/build_m19_p0j_public_draw_in_memory.py) et [banc CPU020 B6](../tools/test_m19_p0j_public_draw_gate_a.py) : audit strict AP20/HUNK, token et signature `0`, portée PC16 et absence de mutation des unités. Exécution MC68020 des deux relocalisations (Rbsr interpréteur / JSR Compiler simulé) puis des sources natives sur deux implantations, en vérifiant ABI numérique 0/1, rendu masqué, refus de masque avant DMA et échec SafePort après un seul Bob. Résultat **PASS (52 vérifications)** : le front reste intact, la corruption du masque fait renvoyer 0 et interdit toute permutation, et le refus SafePort après le premier Bob ne permet pas de présenter le back partiel. Le dispatch AP20 de la fonction index 180 atteint l'entrée BOBS 177 offset 27 286 dans les deux modèles, et son retour conserve l'ABI numérique (`D2=0`, `D3=0/1`). [Journal CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44183835343).

**Limite explicite :** un modèle de dispatch compilé ne démontre pas que le *véritable* AMOS Compiler V2 reconnaîtra la nouvelle fonction, ni que l'écran réel et Close/End/Swap seront corrects sous WinUAE. Ces Gates devront être effectuées **après autorisation distincte de bascule canonique**, avec l'unique Lib/ASC actifs du dépôt. La présente Gate A ne constitue aucune permission de promotion ni de publication.


## Diagnostic complémentaire : notification Safe/Disp et End (B6)

[Test natif CPU020](../tools/test_m19_p0j_pending_close_end_gate_a.py) exécuté en CI [44185013731](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44185013731) : pas de FreeScreenBuffer/DeleteMsgPort quand une réponse Safe ou Disp est absente, WaitTOF borné, puis fermeture possible après réponse tardive. **Défaut documenté de B6 : le callback End historique ne remet pas à zéro le verrou DIRTY après une fermeture réussie**. Ce défaut impose le jalon B7, avant toute bascule vers `dist/AMOSPro_AGA.Lib`. Le nouveau wrapper End est décrit dans [M19 P0j-b7](M19_P0J_END_LIFECYCLE_GATE_A_2026-11-17.md).


## Après B6 — sécurisation End P0j-b7

Le diagnostic B6 (`GetMsg` Safe/Disp différé, fermeture native réelle) reproduit un `End` qui ne réinitialisait pas `DIRTY`. Le correctif [P0j-b7](M19_P0J_END_LIFECYCLE_GATE_A_2026-11-17.md) a **PASS 88 contrôles Gate A MC68020** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44185874211)). Candidate B7 en mémoire 102 072 octets SHA256 `f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b`. Le token `Aga Bob Draw` garde sa signature numérique 0/1, l'ancien `Aga Swap` garde son verrou. **Le vrai Runtime WinUAE et AMOS Compiler V2 de B7 restent non testés**, tout comme la fermeture d'un processus lorsqu'une réponse OS manque définitivement.
