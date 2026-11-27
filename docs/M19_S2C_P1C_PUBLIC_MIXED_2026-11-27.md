# M19 S2c-P1c — intégration publique mixte et Close/End (27-11-2026)

Statut : source et banc de qualification engagés, **pas de Lib installée**. La S2r-P1 qualifiée reste active. LAST_GOOD inchangée.

- Parent P1a reconstruit et identifié par SHA256 exact. Capture 2/4 plans, mêmes arguments publics.
- Même sélection locale de banque dans l'îlot Sprite. Les trois couples GetP/RBSR d'affichage passent avant l'îlot, qui passe de 207 à 213 ; les deux stubs capture gardent 204/206. Les cinq RBSR ciblent 213. Les trois mots de token concernés changent d'index, aucune commande ajoutée. Réserve 16384 octets testée par extension fictive de l'îlot ; aucun emplacement de code persistant.
- UNIT142 réassemblée avec retraite mixte et registre v5 dans l'espace S2r libéré ; preuve byte-exacte hors du trou et des quatre dispatchs déjà autorisés ; ancre et taille identiques.
- Public Sprite choisit la profondeur du répertoire validé, prépare l'allocation correspondante, insère le reçu v5, acquiert les canaux et publie via graphics.library. Le Move/Change attaché réutilise P0c/P0d. Le Change revalide la sélection et le snapshot AMOS après les deux WaitTOF avant staging. Pas de conversion de profondeur en cours d'affichage : Off puis Show.
- Palette : aucune écriture ColorMap. Les 15 couleurs attachées occupent les pens 17..31 ; les simples doivent correspondre à leur sous-palette de paire. Hotspot nul, largeur 16, hauteur 1..256, limites d'écran et génération de banque inchangées.
- Off, Bank Free, Close, End utilisent la même retraite v5. Deux fences ne constituent pas une preuve DMA réelle. Les tests CPU/OS modélisés ne remplacent ni WinUAE ni le vrai Compiler.
- CI : reconstruction exacte, capture, régressions historiques et combinaisons 2/4 plans, animation, Move, Off, Bank Free et Close/End. Les bancs hérités résolvent maintenant l'index AP20 depuis le stub et le stride depuis les métadonnées (défauts historiques conservés).
- Avant livraison : Gate A intégrée PASS, campagne ASC dédiée source vérifiée et préflight, autorisation explicite de bascule. Puis Gates B/C et test DMA. Aucun changement de branche.

## Future campagne B/C (sans activation)

Le générateur `tools/prepare_m19_s2c_campaign.py` dérive l'unique ASC de l'exact S2r et construit le futur AGSP_S2C_MIXED.ABK dans RUNNER_TEMP. Trois écrans : 3 simples, 2 simples + 1 attaché, 3 attachés. 450 Change et 450 Move, trois Off ciblés/recréations, trois Close avec objets actifs, six captures AGAPIC, six captures AGSP 4 plans (dont trois de 1 ligne) et trois refus 16 couleurs ; égalité des mémoires finales et contrôle inter-écrans. Préflight et CI à relever avant proposition de livraison.

Premier assemblage P1c : erreur VASM 2029 sur `bra.s s2c_active_failed`, corrigée par `5efc907`. Aucun binaire installé.

## Candidate assemblée — identité exacte

Commit source corrigé `5efc907baadd7c736345a97464023e2695e15c6b`, campagne générée sur `f4c16dbe7d8cbb64fa763269d53840842e888f76`. [Gate A intégrée 46072322336](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46072322336) en cours au relevé. AGAPIC 392 contrôles, Pattern, SafePort et chaîne DB/IFF/Swap/capture PASS. [Préparation de campagne 46072461473](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46072461473) PASS, préflight strict sans avertissement AMOS, deux générations identiques. Aucune exécution WinUAE ni Compiler.

| Objet futur | Octets | SHA256 | Blob Git calculé |
| --- | ---: | --- | --- |
| AMOSPro_AGA.Lib | 159844 | `00cdcc0de1f9f79aa1d7aac14b920875b5ed822521f7c30c223ea83f88f6a8bb` | `7e8b5320c4098db053afb2bf8ce9f16bf611ff39` |
| SPRITE_PUBLIC.asc | 15459 | `48b9d1e47d63dd401482cfb0ecc8db0646aba68f173154c26ef2b5051f0496ec` | `6b9b4ec84b390c9041126a5231d029d126468ec3` |
| AGSP_S2C_MIXED.ABK | 1460 | `6f9a65305ca2a3ff7a65d8fc3af02afd75bc45810c94392733141bea434bc246` | `649788aaf7343b67797d4d0c3fae46b850c4a3c4` |

AP20 : 105 commandes, 219 entrées, UNIT142 63350, racine 63334, delta 62884. Îlot Sprite 213 de 19246 octets (19212 natifs hors dispatch), marge WORD 46288, PC16 max 3658 même après extension fictive de 16384 octets. Quatre cibles Close/End : 52974, 53030, 54250, 54274. Ne pas confondre la marge WORD calculée avec une preuve que n'importe quel futur code/relocation est valide.

Attente obligatoire de la Gate A intégrale avant une éventuelle activation. L'empreinte Git des quatre fichiers canoniques S2r/LAST_GOOD/ASC/ABK a été revérifiée après les commits. Pas de changement d'installation.
