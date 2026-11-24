# Passage 16 — Intégrité des banques et des identités de cache

**24 novembre 2026 — passage 16/21 · branche main uniquement · source figée [31455a5](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/31455a52ab497fc49131e48520642ad74899e436).**

P2d LAST_GOOD = 136 020 octets, 100 commandes / 203 entrées AP20. S1-P1e active = 142 000 octets, 102 commandes / 208 entrées AP20, gelée. Identités SHA256 documentées dans le [rapport transversal](AUDIT_TRANSVERSAL_AGA_2026-11-23.md), non recalculées lors de cette lecture. **Audit statique de la source liée : aucun rebuild, test, changement de Lib, correctif, ni nouvelle Gate.** VM = validation manquante.

## 1. AGBO : identité, validation et édition

| Chemin source lié | Constat |
|---|---|
| [M19_P0_CHECKED_REGISTRY_MC68020 L63-L338](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P0_CHECKED_REGISTRY_MC68020.s#L63-L338) | Le registre relit le vrai header AMOS DATA, numéro, flags, nom AGABOBS, AGBO v1, taille, nombre d'images borné, répertoire à entrées de 40 octets et génération non nulle. Ce n'est pas un accès arbitraire sans contrôle. |
| [M19_UNIT142_P0F_STAMP_BODY_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_UNIT142_P0F_STAMP_BODY_MC68020.s) | Le stamp compare adresse payload, génération, racine de liste des banques AMOS et taille. |
| [M19_P0J_EXPLICIT_BANK_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P0J_EXPLICIT_BANK_MC68020.s) | GetAdr, owner A5, magic, génération, cache et résidence Chip revalidés ; un hit d'identité évite une reconstruction. |
| Modules M19_P1E_EDIT_BOOTSTRAP, PREFLIGHT, PREFLIGHT_NEXT, PUBLISH, STAMPS, COMMIT et CLEANUP | Nouvelle banque détachée et staging avant publication, vérification des slots/stamps, actualisation des stamps compatibles, désactivation des images supprimées ; libération des ressources anciennes et nettoyage de la préparation en échec. Ces étapes ne constituent pas à elles seules une preuve de rollback intégral de tous les refus. |

**Risque conditionnel ABA (VM, T10/T14).** Un Erase puis Load extérieur aux commandes AGA peut théoriquement recréer à la même adresse un contenu différent avec même taille, même génération persistée et même racine. Le tuple d'identité ne comporte pas de numéro d'allocation externe indépendant ni de hash de contenu visible dans le chemin lu. La possibilité que le véritable allocateur AMOS reproduise toutes ces conditions et qu'un cache ancien soit alors accepté reste à démontrer. Ne pas conclure qu'un Save/Load normal est cassé. Un changement de génération par une édition AGA normale doit invalider les données dépendantes. Poke arbitraire n'est pas une garantie du contrat historique.

## 2. Bank Free : nouveau constat de contrôle AGA-014

Le contrat [historique P0](M19_P0_BANK_FREE_GATES_2026-11-20.md) distingue libération des ressources privées et conservation de la banque DATA AMOS ; Bank Free est une instruction sans résultat numérique public.

- [M19_P2D_PUBLIC_UPDATE_MC68020 L196-L361](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2D_PUBLIC_UPDATE_MC68020.s#L196-L361) : AP20 198, wrapper/callback Bank Free.
- [M19_B8S1_BANK_FREE_MC68020 L15-L210](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_B8S1_BANK_FREE_MC68020.s#L15-L210) : vérifications owner, contexte CLEAN, numéro de banque et parcours borné des 64 objets. Le chemin désactive les slots de la banque concernée et traite la sélection avant d'appeler le helper de libération.
- [M19_P2B_CLEANUP_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2B_CLEANUP_MC68020.s) : p2b_bank_free appelle registry_free_entry, puis purge les variantes concernées si la libération réussit et si le propriétaire correspond.
- [M19_P0_CHECKED_REGISTRY_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P0_CHECKED_REGISTRY_MC68020.s) : checked_release_entry possède des refus de cohérence (adresse, taille, cookie, résidence Chip, graphics base).

**AGA-014 : P2, ordre non atomique statiquement constaté, déclenchement en contexte normal VM.** Si le helper de libération refuse après les modifications des slots, des Bobs peuvent déjà être désactivés sans que le cache ait été libéré. Ce constat ne démontre ni corruption, ni fuite sur un appel valide. Le refus injecté est à distinguer d'une adresse arbitrairement corrompue. En particulier, ne pas libérer de force une plage non validée pour rendre l'opération apparemment atomique. Pour une correction éventuelle, séparer prévalidation, libération/purge et publication, définir explicitement le résultat en échec, préserver le contrat DATA et les autres banques. Même vigilance pour le nettoyage détaché P1E.

## 3. AGPC et FICON/FICHIP

[M19_P0_CORE_DISPATCH_MC68020 L1503-L1779](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P0_CORE_DISPATCH_MC68020.s#L1503-L1779) contrôle le chemin Cache Blit (AP20 162) : GetAdr, format/taille, coordonnées et Safe. [M19_P0_CORE_DISPATCH_MC68020 L1918-L1978](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P0_CORE_DISPATCH_MC68020.s#L1918-L1978) vérifie la plage du slot de 288 octets en Chip, prépare les huit plans de 32 octets et appelle le Blitter suivi de WaitBlit.

[M19_UNIT142_BLOCK_09C80_MC68020 L1-L210](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_UNIT142_BLOCK_09C80_MC68020.s#L1-L210) vérifie destination FICHIP effective en Chip, disposition 12+289*N, slot 288 octets, non-chevauchement, cohérence du masque et ready. Publication ready=1 seulement après copie, avec ready=0 pendant celle-ci. FICON modifié exige **Stage explicite** ; l'icône ancienne sans Stage n'est pas une régression du contrat. Le flag ABK ne remplace jamais la résidence mémoire effective.

## 4. Complément de qualification T10/T11/T14

| Variante | Oracle |
|---|---|
| Erase/Load, même adresse, même génération/taille, contenu distinct | Tracer l'identité réelle ; jamais de cache périmé accepté comme neuf. Ne revendiquer le cas ABA que si toutes les préconditions sont observées ou injectées en A. |
| Bank Free READY/DIRTY, CLEAN, autre banque, deux appels | DATA intacte, slots et ressources des autres banques intacts ; décrire l'état réel après chaque refus. |
| Refus du release après prévalidation (Gate A) | Constater slots, sélection, cache, variantes et absence de Free illégal ; tester répétition/Close. |
| FICON modifié, restaging, Cache Blit Fast puis Chip | Ready et nouveau contenu conformes ; aucun DMA Fast. |

**Bilan :** contrôles locaux substantiels ; aucune preuve nouvelle de corruption réelle ni de P0. AGA-014 et ABA doivent être qualifiés, pas corrigés à l'aveugle. [Cahier T10/T11/T14](AUDIT_AGA_MATRICE_TESTS_2026-11-23.md).
