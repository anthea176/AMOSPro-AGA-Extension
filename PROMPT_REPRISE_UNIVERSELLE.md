# Prompt universel de reprise — AMOSPro AGA Extension

Tu reprends le projet [`anthea176/AMOSPro-AGA-Extension`](https://github.com/anthea176/AMOSPro-AGA-Extension) dans une nouvelle conversation.

**Ne présume jamais de la version, du build, du jalon, des tests ni de l'état d'avancement.** Ces éléments doivent être vérifiés dans le dépôt au moment de la reprise, pas dans les souvenirs d'une ancienne session. **Seul le dépôt `anthea176/AMOSPro-AGA-Extension`, branche `main`, est autorisé**, sauf instruction explicite contraire de l'auteur.

## Source d'autorité

La référence obligatoire est **`EXTENSION_SOURCE_RULES.md`, dans sa version courante sur GitHub**. Lis-la et respecte-la intégralement avant toute intervention.

Ce prompt sert uniquement à retrouver le contexte. Il **n'ajoute, ne remplace et ne modifie aucune règle**. En cas de contradiction, vérifie le dépôt et les résultats réellement observés ; signale le conflit et résous-le avant de toucher au code ou aux binaires.

## Procédure de reprise

1. **Interroger exclusivement `main`** : relever HEAD, les derniers commits (y compris ceux de l'utilisateur), fichiers réellement modifiés, résultats et éventuels échecs de CI. Ne jamais créer, changer de branche, worktree, PR ou dépôt sans autorisation explicite.
2. **Lire les références actuelles** : `EXTENSION_SOURCE_RULES.md`, `docs/NEXT_SESSION.md`, `tests/current/README.md`, `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`, puis les README et le fichier STATUS du **jalon réellement actif** s'il existe. Ne jamais traiter un ancien STATUS comme courant par défaut.
3. **Identifier le chantier réellement actif** à partir des fichiers et de l'historique récents. Distinguer les consignes actuelles des comptes rendus de builds et essais antérieurs.
4. **Vérifier les artefacts en place** : unique bibliothèque installable/de travail `dist/AMOSPro_AGA.Lib`, référence protégée `dist/AMOSPro_AGA_LAST_GOOD.Lib`, tailles, SHA256, tokens/entrées AP20, builder reproductible, base exacte et sources du jalon. Les archives historiques peuvent servir de preuves ou de bases identifiées, **jamais de seconde candidate à installer**. Ne pas supposer que `LAST_GOOD` est la base de construction courante.
5. **Examiner `tests/current/`** : zéro ou un ASC actif et ses ressources ABK/IFF nécessaires, préparées au même endroit et vérifiées par leurs empreintes. Consulter `tests/passed/`, `tests/fixtures/` et les diagnostics historiques **en lecture seule**. Aucun archivage, déplacement, copie ou modification de test validé de sa propre initiative.
6. **Distinguer les preuves et les Gates** : A = préflight/CPU/ABI/CI ; B = test réel AMOS/WinUAE en précisant `Prg State` (`0` interprété, `1` Runtime) ; C = véritable exécutable AMOS Compiler (`-1`) ; D = matériel Amiga physique. Une simulation Compiler en CI ne vaut pas Gate C. La Gate C manuelle peut être regroupée au jalon prévu, sauf risque ABI nécessitant un essai ciblé.
7. **Recouper les preuves** : règles, documents de statut, code, binaires, builder, CI et retours utilisateur. Si elles se contredisent, ne pas inventer d'état « probable » : séparer les faits vérifiés, hypothèses et tests non exécutés.
8. **Présenter brièvement l'état retrouvé** : chantier actif, binaire/version/SHA, ASC et ressources, dernier résultat confirmé, Gates manquantes, prochaine action selon la demande de l'auteur.

## Pendant le travail

Appliquer **strictement la méthode définie dans `EXTENSION_SOURCE_RULES.md`** : périmètre, `main` seule, builds reproductibles, ABI/Compiler, protection des versions validées, tests et documentation. La reprise commence **en lecture seule**. Ne pas modifier de code natif, builder, binaire, ASC ou autre dépôt sans demande explicite. Une roadmap, un diagnostic ou un PASS ne vaut pas autorisation d'implémenter ou de promouvoir.

**Livraison et promotion :** le **seul binaire de travail à installer** est `dist/AMOSPro_AGA.Lib`, à la racine de `dist`, sans renommage ni copie parallèle imposée à l'utilisateur. `dist/AMOSPro_AGA_LAST_GOOD.Lib` est une **référence protégée**, distincte de la candidate. **Aucune promotion automatique**, y compris après Gate B PASS ou Gate C PASS : une décision explicite distincte de l'auteur est obligatoire pour toute modification de `LAST_GOOD`. Chaque binaire conserve sa version, son SHA256 et ses preuves ; ne pas exiger leur égalité sans décision de promotion. En cas de FAIL, conserver les traces et **ne pas restaurer automatiquement** la candidate depuis `LAST_GOOD` ni depuis une archive.

**Tests et suivi :** conserver **un seul ASC actif** et les ressources nécessaires sous `tests/current/`. Ne pas créer de nouveau test/ZIP/candidate dans les archives, déplacer automatiquement des ASC vers `tests/passed/` ou réorganiser `tools/` ; toute exception requiert une instruction de l'auteur. Lorsqu'un résultat est obtenu, consigner sa portée réelle, les erreurs, les logs WinUAE et les benchmarks dans les documents prévus. Les README anglais/français restent des **manuels de l'API publique**, pas des chronologies de Gates ; les mettre à jour ensemble uniquement lorsque l'API documentée change.

## Pérennité de ce prompt

**Ne jamais ajouter ici** de numéro de version, build courant, SHA, commit, fichier de test actif, statut temporaire, planning ou prochaine fonctionnalité supposée : ces informations deviennent obsolètes.

L'état du projet appartient aux documents de suivi et au dépôt GitHub. **Ce prompt doit rester réutilisable d'un build à l'autre** ; le modifier uniquement pour une évolution demandée de la procédure, sans recopier les versions ou statuts historiques dans ses instructions.
