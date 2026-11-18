# Bobs AGA — restauration locale du décor

Une **démonstration interactive** pour AMOS Professional et l'extension AMOSPro AGA. Ce n'est **pas un benchmark** : l'écran montre un titre, un décor multicolore et **quatre Bobs mobiles**. Les anciens rectangles des Bobs sont restaurés avec le Blitter, sans effacer tout l'écran à chaque image.

**Programme :** [BOB_LOCAL_RESTORE.asc](BOB_LOCAL_RESTORE.asc) (source ASCII autonome, aucun IFF/ABK externe).

## Configuration

- **Bibliothèque :** `dist/AMOSPro_AGA.Lib` B7-m1, **102 360 octets**, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`.
- **Machine :** Amiga AGA, MC68020 minimum ; WinUAE PAL 320×256, 256 couleurs, profil fonctionnel 68030/JIT ON.
- **Banques :** 24 et 25 **libres**. Le programme refuse de les remplacer si elles existent déjà et ne fait jamais `Erase All`.
- **Mode :** AMOS Professional **Runtime uniquement** pour le moment. La Gate C avec le véritable AMOS Compiler n'est pas qualifiée sur B7-m1 : le programme la refuse volontairement.

## Lancement

1. Installer la Lib dans le slot choisi d'`APSystem`, relancer AMOS Professional.
2. Dans un programme vide : **Project → Merge ASCII** puis `BOB_LOCAL_RESTORE.asc`.
3. Exécuter en Runtime. **Une touche ou un clic quitte** ; un maximum de 2 400 images évite une boucle infinie si aucun événement n'est reçu.
4. Vérifier le retour à AMOS, le message `RESULT 1 ERR 0`, le nettoyage des deux banques, puis essayer une seconde exécution sans `Erase All`.

## Ce que montre le source

- Un **titre AGA** fixe, tracé avec `Aga Text` (zone y=0..31).
- Un **décor de tuiles** généré sans fichier externe ; sa **bande témoin immuable** occupe y=32..63, distincte du titre.
- Quatre Bobs issus de deux banques : deux rouges **masqués** et deux jaunes **opaques**, avec clipping aux bords.
- **Double buffering** : deux copies initiales du décor, puis seules les **anciennes positions des Bobs sur la page arrière correspondante** sont restaurées par `Aga Blit Copy` (découpage aux limites des tuiles de 32 pixels).
- `Aga Bob Draw` + `Aga Swap` explicites, reprises bornées uniquement sur retour `0`, fermeture AGA et effacement des seules banques créées.

**Validation :** le benchmark **source d'origine** sur décor texturé a passé sa Gate B WinUAE (720/720 frames, zéro erreur, rendu confirmé), voir le [rapport](../../docs/M19_B7M1_DECOR_BENCH_RUNTIME_2026-11-18.md). **Ce nouvel ASC enrichi d'un titre et d'une sortie interactive n'a pas encore été exécuté sous WinUAE** : préflight AMOS et test géométrique des deux pages uniquement. Gate C Compiler et Gate D matériel **non testées**.
