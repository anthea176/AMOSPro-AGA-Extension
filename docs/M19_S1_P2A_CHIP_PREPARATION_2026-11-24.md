# S1-P2a — Préparation Chip indépendante du Sprite (24 novembre 2026)

Base active S1-P1i (142968 octets, SHA256 2f3cb4adf56121f62aeccf9916d680ba3e2857c9bdbe0fda777d1d7eaed7ffc3) ; [Gate B capture PASS](M19_S1_P1I_RUNTIME_PASS_2026-11-24.md) et ABK originaux validés. Auteur « ok va y » : figer P1i et préparer l'affichage. Pas d'autorisation de bascule ou promotion. MC68020+.

## Etape livrée en source, non intégrée

- [Routine](../src/native/m19_s1/M19_S1P2A_CHIP_PREPARE_MC68020.s) : A0 payload AGSP stable et validable, D0 longueur d'allocation exacte, D1 ID ; sortie D0 bloc privé Chip ou 0, D1 longueur ou 0, autres registres préservés. Appel synchrone avec source dont le propriétaire garantit la durée de vie et l'étendue. TypeOfMem contrôle l'appartenance à une région mémoire, pas l'étendue d'une allocation arbitraire. Réutilisation exacte du validateur AGSP P1i.
- Recherche ID trié, largeur 16, profondeur 2, hauteur 1..256, 0..3 couleurs opaques. Allocation Exec AllocVec MEMF_PUBLIC|MEMF_CHIP|MEMF_CLEAR. Vérifier les deux extrémités en Chip ; erreur libère uniquement une allocation non publiée. Aucun pointeur d'AMOS ni de l'IFF conservé.
- En-tête privé 48 octets : SimpleSprite 12 octets (posctldata=0, hauteur, X=Y=0, canal -1), longueur, ID, couleurs, génération, hotspot, 4 triplets RGB24, offsets image/blank. Pour H=16, deux blocs de 72 octets : 192 octets au total ; pour H=256, 2112 octets. Le tampon image contient contrôle nul, paires de WORDs entrelacées, terminaison nulle ; blank de même hauteur, nul. La structure ne peut pas être publiée comme API tant que le cycle de vie n'est pas qualifié.
- [Banc MC68020](../tools/test_m19_s1p2a_chip_prepare_cpu.py) : 5 images des véritables ABK, hauteurs 1/16/255/256, transparence seule et noir opaque, hotspot signé, IDs sparse, refus des largeurs et modes S2, banque invalide, OOM, fausse allocation Chip, registres volatils et conservation des données. La CI assemble avec VASM et exécute sur Unicorn MC68020. Résultat à relever après le run, ne pas anticiper PASS.

## Verrou avant S1-P2b (affichage)

La sonde S0d [historique B/C](AGA_HARDWARE_SPRITES_S0_INTEGRATION_2026-11-21.md) a rendu un Sprite mais n'a pas prouvé le détachement. La [documentation GetSprite](https://d0.se/autodocs/graphics.library/GetSprite) confirme que l'OS attribue le canal ; [ChangeSprite](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_2._guide/node0427.html) exige la mémoire Chip et la hauteur correcte, [MoveSprite](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node0302.html) place les mots de contrôle ; [FreeSprite](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_2._guide/node05A6.html) rend le canal disponible, sans garantie explicite de cessation des références DMA. Aucune inférence de détachement par un compteur de VBL. La préparation n'appelle donc aucun de ces LVO.

Palette : utiliser les GET de [VideoControl](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node0338.html) (SPEVEN/SPODD_BASE et SPRITERESN), comparer au contexte réel et aux indices effectivement utilisés ; conflit avec fond/cursor ou autre canal = refus. Ne pas écrire BPLCON4/FMODE, ne pas déduire la base actuelle de S0d. Avant intégration, mesurer les références Sprite/Copper en WinUAE, distinguer l'image active et le blank ; aucune FreeVec si doute, y compris lors d'un Off, Close, erreur, Ctrl+C, fin de programme. Ne pas fermer en détruisant un ViewPort encore référencé par une future routine. Une preuve sur émulateur ne vaut pas Gate D.

## Etat

Aucune nouvelle commande AMOS, aucun nouveau binaire de Lib, aucun ASC changé. P1i et LAST_GOOD L2b restent inchangées. Pas de DMA actif, pas de PASS Runtime S1-P2a ni Compiler. Qualification CPU du composant en CI et étude du cycle OS/palette requises avant installation.

## Qualification du composant et sonde suivante

[Gate A composant](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45497634775) PASS : 44 scénarios, SAVED 2 images, FINAL 3 images, SHA256 du code VASM `e2eea0ba260089e2fbf80dc076dce45999fc85027ea5da031067dd3ebc1cb348`. [CPU/delivery](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45497634909) PASS. Les deux Lib passent le contrôle SHA256. Nouveau [banc palette](../tests/proto/sprite_s1_palette/README.md) source-only et préflight strict PASS, pas de nouvelle Lib. Le banc mesure le contexte V39 avant et après DB/cursor. Runtime de la sonde et preuve DMA toujours à établir.

## Sonde palette et étape P2b

**Sonde palette Runtime PASS (25/11/2026).** Journal original [1105 octets CRLF](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/main/docs/evidence/M19_S1P2_PALETTE_RUNTIME_2026-11-25.TXT), SHA256 `dc332e6c6a17e05c9960bd65d3e3b75f07a7c5dc4483bb1da63876402b7b1b50`, blob `362878799bcaae3b1a70fe84ea34b0d81904de2d`. PRG_STATE 1, RESULT 1, ERR 0, SAMPLES 4, CLOSE_RETURNED 1. V40, VP Modes $5000, bases EVEN/ODD 16, résolution demandée 255, défaut 1, PF1_PRI 4. Les quatre états mesurés sont identiques. Attribution à P1i par contexte ; pas de SHA installé dans le log. Aucun transfert de PASS vers l'affichage ou le retrait DMA.

[Affichage AGSP P2b préparé](M19_S1_P2B_AGSP_DISPLAY_PROBE_2026-11-25.md) : préflight PASS, Runtime NON TESTÉ. Pas de nouvelle Lib.
