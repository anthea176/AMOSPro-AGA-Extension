# Prompt universel de reprise — AMOSPro AGA Extension

Tu reprends le projet [`anthea176/AMOSPro-AGA-Extension`](https://github.com/anthea176/AMOSPro-AGA-Extension) dans une nouvelle conversation.

**Ne présume jamais de la version, du build, du jalon, de la branche, des tests ou de l'état d'avancement.** Tous ces éléments doivent être retrouvés dans le dépôt **au moment de la reprise**, pas dans ce prompt ni dans les souvenirs d'une ancienne session.

## Source d'autorité

La référence obligatoire est **`EXTENSION_SOURCE_RULES.md`, dans sa version courante sur GitHub**. Lis-la et respecte-la intégralement avant toute intervention.

Ce prompt sert uniquement à retrouver le contexte. Il **n'ajoute, ne remplace et ne modifie aucune règle**. En cas de contradiction, vérifie le dépôt et les résultats réellement observés ; signale le conflit et résous-le avant de toucher au code ou aux binaires.

## Procédure de reprise

1. **Interroger le dépôt réel** : branche de travail, HEAD, derniers commits (y compris ceux de l'utilisateur), modifications récentes, résultats et éventuels échecs de CI.
2. **Lire les références actuelles** : `EXTENSION_SOURCE_RULES.md`, `docs/NEXT_SESSION.md`, le fichier STATUS correspondant au chantier en cours, `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`, ainsi que les README utiles.
3. **Identifier le chantier réellement actif** à partir des fichiers et de l'historique récents. Distinguer les consignes actuelles des comptes rendus de builds et essais antérieurs.
4. **Vérifier les artefacts en place** : binaire candidat, version de secours, archives, tailles et SHA256, builder reproductible, sources et tests associés. Lire le builder réel avant de proposer un changement.
5. **Examiner `tests/current/`**, les validations consignées dans `tests/passed/` et, seulement si nécessaire, les anciens diagnostics. Distinguer explicitement validation statique/CI, test AMOS interprété, test compilé et matériel réel.
6. **Recouper les preuves** : règles, documents de statut, code, binaires, CI et retours utilisateur. Si elles se contredisent, ne pas inventer d'état « probable » ; identifier ce qu'il faut vérifier ou corriger.
7. **Présenter brièvement l'état retrouvé** : chantier actif, dernier résultat confirmé, points non validés, candidat et test pertinents, prochaine action selon la demande de l'utilisateur.

## Pendant le travail

Appliquer **strictement la méthode définie dans `EXTENSION_SOURCE_RULES.md`** : périmètre des modifications, politique de branches et commits, builds reproductibles, protection des versions validées, tests, validations et documentation. Ne pas créer sa propre procédure de livraison, de test ou de promotion.

**Livraison et promotion :** la bibliothèque candidate utilisable doit toujours être `dist/AMOSPro_AGA.Lib`, directement à la racine de `dist`, sans renommage demandé à l'utilisateur ni sous-répertoire arbitraire. Lorsqu'un candidat est **validé sous AMOS/WinUAE (Gate B confirmée par l'utilisateur)**, il devient obligatoirement **`dist/AMOSPro_AGA_LAST_GOOD.Lib`** par copie binaire identique ; ne jamais promouvoir un candidat Gate A/CI seulement. Protéger les archives versionnées et vérifier le SHA256 des deux binaires. Cette règle est rappelée ici sans figer de numéro de version ; la définition complète figure dans `EXTENSION_SOURCE_RULES.md`.

Ne pas entreprendre de chantier supplémentaire sans demande. Lorsqu'un résultat est obtenu, actualiser les **documents de suivi du projet** et les classements de tests prévus par les règles.

## Pérennité de ce prompt

**Ne jamais ajouter ici** de numéro de version, build courant, SHA, commit, fichier de test actif, statut temporaire, planning ou prochaine fonctionnalité supposée : ces informations deviennent obsolètes.

L'état du projet appartient aux documents de suivi et au dépôt GitHub. **Ce prompt doit rester identique d'un build à l'autre** ; ne le modifier que si l'utilisateur demande une évolution de la procédure de reprise elle-même.
