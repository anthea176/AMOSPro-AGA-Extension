# M18 — audit F 16 Icon / F Paste Icon et atlas indexé P0

**13 novembre 2026 — main uniquement.** Statut : audit et prototype hôte. Aucun nouveau token AP20 ni bibliothèque R61. **Référence : R60 v0.13.5 LAST_GOOD**, 35 056 octets, SHA256 00b884ec34e6c30ab6a8f194dc3882aa8ac7e5e53697604089d04f2f8c7ad0c8. Gates A/B/C et régression complète R60 PASS. Gate D physique non testée.

## 1. Ce qui est réellement documenté

- **AMOS Professional : Paste Icon x,y,number**. Les icônes résident dans la **banque Icon 2**, et sont dessinées par le Blitter, normalement en remplacement opaque. En double buffering, AMOS peut dessiner sur les deux écrans ; Autoback 0 permet de limiter au logique. Notre extension AGA doit **toujours cibler le back buffer privé sans Swap/VBL implicite**. Source primaire : https://amospromanual.dev/07-07-icons-and-blocks.html
- **AMOS Turbo / Turbo Plus : F Paste Icon**. Des utilisateurs AMOS citent cette commande comme accélération de Paste Icon, utile aux jeux avec scrolling par briques. Des discussions signalent également les coûts des recherches dans les banques d'objets d'AMOS, sans documenter de façon complète les paramètres de Turbo. Sources : https://www.amigaimpact.org/forums/topic/amos-professional-x-devient-unity/ et https://www.amigafrance.com/forums/topic/amos-professional-x-aga-cest-reparti/
- **Le nom demandé F 16 Icon demeure NON VÉRIFIÉ.** Rien ne prouve à ce stade que F 16 Icon soit exactement F Paste Icon : sa syntaxe, sa banque, ses conventions de palette/transparence et son alignement d'origine ne sont pas établis. Ne pas prétendre à une compatibilité binaire, ni reprendre le nom/token sans preuve.

**Écart R60 :** Aga Image Region sélectionne un rectangle source AGAPIC v1 mais ne sait pas résoudre un numéro d'icône depuis un catalogue, ne lit pas la banque Icon 2 classique et n'offre pas de backend Blitter. C'est une brique graphique, **pas** une implémentation complète de F Paste Icon ou F 16 Icon.

## 2. Modèle host P0 : icônes numérotées, format AGAPIC v1 inchangé

- **Code :** tools/m18_icon_atlas_model.py
- **Tests :** tools/test_m18_icon_atlas_model.py

Le modèle gère une **image AGAPIC v1 existante en banque DATA** et un répertoire d'icônes en mémoire **Python uniquement**. Chaque entrée porte un identifiant positif **1 à 65535** et son rectangle exact de dimensions variables. Les IDs peuvent être non contigus ; l'index est prévalidé à sa création et adressable directement par numéro, sans recherche séquentielle à chaque dessin. Le choix de numérotation 1-based vaut pour ce prototype hôte seulement, **aucune ABI publique n'est fixée**.

L'affichage délègue entièrement à render_region_cpu_model, afin de conserver le même rendu opaque/masqué (couleur 0 opaque), clipping aux quatre bords, pixels non alignés, profondeur 1–8 plans et validation RLE AGAPIC v1 que le moteur d'atlas P0 de M18. Erreur de numéro, de masque, de profondeur, d'index ou de rectangle => refus avant écriture. L'autre back buffer, la palette et les gardes mémoire restent inchangés.

**Il n'y a pas de nouveau format de banque, de nouvel ABK, de code 68000 ni de backend Blitter dans ce prototype.** Les bancs CPU/Blitter réels devront vérifier les mêmes sorties et mesurer staging Fast->Chip, préparation Blitter, attente, rendu et temps total.

## 3. Préalables à la vraie fonction native

Avant de figer une signature R61, il faut encore vérifier dans la documentation ou les binaires Turbo d'origine : si F 16 Icon est F Paste Icon ou une autre instruction, les paramètres exacts, la banque Icon 2 et son encodage, les modes remplacement/masque, l'origine XY, le clipping, la palette et le comportement double buffer.

Deux voies envisageables à évaluer : convertir les icônes AMOS en AGAPIC v1 avec **table de correspondance d'ID** (Fast RAM possible, CPU->Chip), ou dessiner depuis une banque classique après conversion explicite/staging Chip. Éviter un nouveau moteur RLE concurrent. Le Blitter ne peut **pas** lire la Fast RAM directement. Aucun choix AUTO avant mesures. L'identité fonctionnelle sera jugée **image par image** face à Paste Icon/F Paste Icon sur données témoins et positions identiques, pas seulement par valeurs de retour.

Le futur builder de R61 devra partir de R60 LAST_GOOD Compiler V2, conserver les 54 signatures existantes, faire passer Gate A native CPU/ABI puis Gates B/C sous WinUAE avec un seul ASC actif. R60 reste intouchée pendant cette étude.

## 4. Ordre confirmé

**Terminer M18** : icônes numérotées / équivalent rapide F Paste Icon ou F 16 Icon après audit, puis CBlock AGA pixel exact (chemin aligné 16 pixels et chemin général). **Seulement ensuite** : optimisation native 68020+, puis c2p.library, conformément à la dernière demande de l'auteur du 13/11/2026.

**P0 hôte seulement — aucune Gate A/B/C/D nouvelle n'est revendiquée pour les icônes indexées.**
