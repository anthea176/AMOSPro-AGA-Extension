# C2P R74 — bitmap intermédiaire (14/11/2026)

**Statut : architecture acceptée, modèle hôte 16/16 PASS. Aucun code natif C2P intégré, aucune nouvelle Lib ou Gate B C2P réalisée.** Le diagnostic GDB P2 est abandonné. Aucun essai PowerShell/WinUAE spécial n'est demandé.

## Chaîne de conversion prévue

1. Lire un tampon chunky 8 bits depuis une banque AMOS DATA/WORK valide, taille minimale **81 920 octets** pour **320×256**.
2. Créer une fois un contexte de **c2p.library 1.9** : type **C2P_CONTEXT_TYPE_BITMAP = 1**, largeur 320, hauteur 256, format 8 plans, et **CHUNKY** pointant vers la banque. Le SDK alloue **un bitmap interne de 80 Kio en Chip RAM**. Il est récupéré par **GetContextParameter(BITMAP)**.
3. Avant chaque frame, revérifier identité et longueur de la banque (elle peut être Erase/Load/Reserve et changer d'adresse). Après initialisation, le SDK permet de mettre à jour le paramètre **CHUNKY**. Convertir en planar : **Chunky2Planar renvoie 0 si succès**.
4. Attendre la disponibilité **Safe** du véritable back buffer de l'extension, sans attente bloquante et sans jamais écrire au front. Copier depuis le bitmap interne par **BltBitMap(source,0,0,back,0,0,320,256,0xC0,0xFF,NULL)**. Exiger un retour **8 plans**, puis **WaitBlit** avant tout Swap.
5. L'utilisateur déclenche séparément **Aga Swap**. Palette et écran AGA classiques inchangés.

**Pourquoi cela évite GDB :** graphics.library/BltBitMap sait copier les huit plans d'un BitMap vers un autre en se servant de leurs structures, sans exiger que le bitmap Intuition *destination* possède des plans physiquement contigus. Documentation officielle : https://developer.amigaos3.net/autodocs/graphics.library/BltBitMap.html. La copie et sa synchronisation native restent à tester sous AMOS/WinUAE.

## Mémoire et contraintes

- Chunky source : **80 Kio** dans une banque AMOS. Bitmap C2P : **80 Kio Chip** supplémentaires.
- Le SDK alloue également un tampon **Scrambled de 80 Kio** en mémoire système et des structures. S'il manque un pointeur CHUNKY lors de InitializeContext, il peut allouer **encore 80 Kio**. Toujours fournir le pointeur externe avant l'initialisation.
- CPU **68020 minimum**, écran 8 bitplanes (256 couleurs), 320×256 uniquement au premier jalon, double buffering actif. Vérifier ces conditions *avant* les appels C2P.
- La bibliothèque externe doit exister dans **LIBS:c2p.library** ; elle ne rentre pas dans le monolithe AP20.
- Un bitmap en mode **TYPE_BITMAP** appartient au contexte : **DestroyContext** le libère. Ne pas appeler **DestroyBitMap** séparément ; celui-ci sert aux bitmaps custom.
- La R73 actuelle (**51 608 octets**, SHA256 **c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407**) est inchangée.

## Première fonction à contractualiser individuellement

**_OK=Aga C2P Open(Bank)** — une fonction AMOS entière, retour **1 succès / 0 échec**.

Proposition précise : Bank est un numéro positif de banque AMOS DATA/WORK vivante. L'extension contrôle type, taille >= 81 920, écran et CPU puis OpenLibrary, CreateContext, SetContextParameter(TYPE=BITMAP, WIDTH=320, HEIGHT=256, PLANAR_FORMAT=8, CHUNKY=pointeur), InitializeContext. Aucun pixel ne change. Un second Open alors qu'un contexte est actif renvoie 0 sans l'altérer. Tout échec libère immédiatement les allocations partielles. Aga Screen Close devra libérer le contexte automatiquement, y compris après interruption. Le pointeur de banque devra être revérifié avant Convert.

**La règle du dépôt impose un contrat validé explicitement pour chaque fonction avant de coder cette fonction.** L'accord sur l'architecture ne préjuge pas des commandes suivantes.

Commandes envisagées ultérieurement, avec contrats et autorisations séparés :
- **Aga C2P Convert** : revalidation source, conversion + BltBitMap vers le back Safe, WaitBlit, résultat 1/0 ; pas de Swap implicite.
- **Aga C2P Close** : libération propre et réutilisable ; résultat 1/0 ; auto-cleanup sur Screen Close.

## Vérifications hôte disponibles

- **tools/c2p_intermediate_model.py**
- **tools/test_c2p_intermediate_model.py** : 16 tests déterministes PASS, source 8 bits complète, couleurs 0..255, bords non alignés, destinations standard/entrelacées/paddées, refus si buffer non Safe, front inchangé, Swap/Close.
- Exécution de contrôle : **python -B tools/test_c2p_intermediate_model.py**.

**Attention :** c'est un modèle de référence Python, ni le vrai c2p.library, ni une Gate A CPU68020, ni une Gate B WinUAE. Le seul test manuel demandé à l'auteur après génération native sera un **ASC interprété**, sans GDB.

SDK exact étudié : archive utilisateur **c2p.library-main.zip**, **sdk/C/c2p_context.h**, **sdk/fd/c2p.fd**, **sdk/docs/c2p.autodoc**, **src/c2p_context.c**. Provenance technique vérifiable ; le SDK ne valide pas à lui seul notre intégration AP20.
