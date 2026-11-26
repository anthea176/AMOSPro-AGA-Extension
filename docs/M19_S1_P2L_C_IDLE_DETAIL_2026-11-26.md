# S1-P2l-c — distinguer le refus idle sans changer la politique DMA

Auteur « ok va y » après Gate B P2l-b et retour ERR10 en relance. Accord pour poursuivre le développement, Compiler reporté. Développement initial source-only sur main ; autorisation de bascule et résultats exacts ci-dessous. Aucune promotion.

## Base vérifiée

P2l-b HEAD 0b92f04326793727b4fdee67cdbc9400f2679c19, 149940 octets, SHA256 d9b690287c82c52a766d5ab4b015bb29d25057cbe55a630c0e30d88d46bd4ab1, 105 commandes / 214 AP20, MC68020 minimum. Gate A 496 contrôles PASS et reconstruction exacte ; B PASS 2/2 scénario affichage/quarantaine uniquement ; C reportée, D non testée. LAST_GOOD L2b et ABK inchangées. [Résultats P2l-b](M19_S1_P2L_B_DIAG_ROUTE_2026-11-26.md).

L'ancien [audit P2d r2](M19_S1_P2D_OS_AUDIT_2026-11-25.md) avait observé ActiView=0, LOF/SHF=copinit+164 après fermeture et retrait des références OS échantillonnées ; le contenu du WAIT terminal n'y a pas été vérifié. Ces observations ne sont pas transférables à P2l-b. Le retour -185 est commun à quatre prédicats et à leur relecture tardive. Il ne prouve ni référence DMA persistante ni sécurité de réemploi.

## Delta minimal

[Source](../src/native/m19_s1/M19_S1P2LC_IDLE_DETAIL_MC68020.s), [builder](../tools/build_m19_s1p2l_c_in_memory.py), [Gate A](../tools/test_m19_s1p2l_c_gate_a.py). Reconstruction obligatoire du parent exact via son builder historique. Modification source du seul retour p2l_not_idle dans une copie temporaire (BRA.W et deux NOP, même longueur), puis append du helper dans UNIT207. Tout le reste du préfixe parent, UNIT142, stubs 209/211/213 et tokens inchangés ; contrôle strict de l'écart, de l'adresse du branchement, du plafond PC16 et de la réserve 16 KiB. Détail exécuté seulement après un refus existant, dans le même emprunt et avec GfxBase validée. Aucune nouvelle API publique, aucun pointeur exporté. Aucune nouvelle attente, écriture record/Chip/Copper, ni libération. Les observations ne sont pas atomiques : pointeur copinit revalidé, relecture, aucun suivi des adresses View/LOF/SHF.

Le diagnostic hors domaine -19000 garde les autres retours P2l-b. Pour un refus idle, retour -256-MASK, MASK non nul :

| Bit | Signification | Retour si seul |
| --- | --- | --- |
| 1 | ActiView non nul | -257 |
| 2 | LOF différent de copinit+164 | -258 |
| 4 | SHF différent de copinit+164 | -260 |
| 8 | LONG terminal différent de FFFFFFFE | -264 |
| 16 | copinit non mappé selon AGSP_I_SPAN | -272 |
| 32 | base copinit changée pendant détail | -288 |

Si plusieurs prédicats échouent, les bits sont cumulés (ex. -259 = 1+2). Si le pointeur n'est pas vérifiable, les bits 2/4/8 ne sont pas évalués ; s'il change, le relevé est incomplet/instable. Si la relecture ne reproduit aucun prédicat, conserver -185 (transitoire ou indéterminé). -190 reste une compatibilité d'observations et non une preuve de libération. La garde de publication -123 n'est pas modifiée. Aucun retour de détail ne peut donner un succès.

## Qualification prévue

Gate A P2l-b héritée 496 contrôles (trois attentes privées -185 paramétrées explicitement, défaut historique préservé), plus 36 cas P2l-c : toutes les 15 combinaisons de quatre bits dans les deux modèles, pointeur absent avec View actif, changement lors du second WaitTOF, retour idle compatible. Invariants registre, record, Chip, allocations, Free, appels Sprite, état et fermeture de référence Gfx. Réserve 16 KiB, CPU/ABI et chaînes complètes héritées. Aucun PASS annoncé avant CI exacte.

[Préparation ASC](../tools/prepare_m19_s1p2l_c_campaign.py) à partir du seul ASC actif P2l-b avec SHA strict, aucune écriture dans le dépôt : plages des retours de détail, tag nouveau et noms RAM: distincts par mode et phase. Préflight strict dans la même CI. B/C/D NON TESTÉES. Aucune livraison alternative.

## Suite

Gate A et préflight exacts PASS ; bascule explicitement autorisée et paire active. Une campagne Runtime ciblée relèvera les refus détaillés ; inutile de refaire P2l-b ou de compiler ce diagnostic. À partir des observations, déterminer si l'exigence idle est trop forte ou si une réelle référence subsiste. Étudier le réemploi sans libération prématurée, puis tests 100 cycles Off/On, ouvertures/fermetures répétées sans reset et stabilité mémoire, enfin Gate C du jalon fonctionnel. Aucune garantie DMA ni réemploi déduite d'un masque.

## Qualification et activation canonique — 26/11/2026

**S1-P2l-c active (26/11/2026).** Autorisation auteur « va y ct inplicite! » après Gate A PASS. Lib 150056 octets, SHA256 `148b4d06702f84dd6de3eacd069a55c4759164bb4dd3c74f319f81e6f077f3f5`, blob `86d9497e3a2d5446001b9b41fc25d2e6a878ae50`, 105 commandes / 214 AP20, MC68020+. [Gate A complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45877952385) : 532 contrôles (496 hérités + 36 détail idle). [Reconstruction exacte et préflight strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45880559895). UNIT142 65276, marge 258 ; UNIT207 11178, PC16 max 11208, marge 21556 ; helper natif 114 octets, patch 8 octets à 10978. ASC unique 6425 octets SHA256 `25a50fd84962dcdd0a52a45d496ad3413676d37aa4b3df4c2d74391d18c4a89e`, blob `fad7c3f78a20907f25a0e8072508c5c2c9e9b409`. ABK inchangée (532 octets) et LAST_GOOD L2b protégée. B/C/D NON TESTÉES sur P2l-c ; CI post-activation à relever. Aucune libération ni réemploi DMA.

Reconstruction exacte depuis les sources du parent sur GitHub Actions en lecture seule : 98 fragments Lib et 5 fragments ASC récupérés, longueur et blob identiques aux identités CI. Les consommateurs de provenance reconnaissent uniquement cette paire exacte, reconstituent P2l-b et P2k pour les vérifications historiques (pas de synthèse de source à partir du binaire). Le nouveau test reproduit l'ASC historique avec SHA strict. Les adaptations de vérification ne changent aucun octet natif qualifié ; requalification post-activation distincte. [Campagne Runtime](../tests/current/README.md).
