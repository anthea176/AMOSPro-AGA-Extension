# M18/R60 — test AMOS actif unique

**Candidate :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), R60 v0.13.5, **35 056 octets**, SHA256 `00b884ec34e6c30ab6a8f194dc3882aa8ac7e5e53697604089d04f2f8c7ad0c8` ; 54 commandes, 61 entrées AP20. **R59 `LAST_GOOD` inchangée.**

**Seul ASC actif :** [`M18_R60_IMAGE_REGION_01.asc`](M18_R60_IMAGE_REGION_01.asc), avec **`M16_AGAPIC_SAMPLE_BANK10.abk`** déjà présent ici. Copier ces deux fichiers dans le répertoire courant AMOS. **ATTENTION : le `Load` écrase la banque 10** ; tester en WinUAE jetable.

**Procédure :** installer la Lib R60 dans APSystem, redémarrer AMOS et Compiler, `Project → Merge ASCII`, lancer en interprété (Gate B), puis **compiler le même ASC dans un nouveau fichier exécutable** et lancer ce fichier (Gate C). Ne pas réutiliser l'exécutable R59.

Le test dessine quatre frames sources 32×20, un rectangle source décalé, clipping quatre côtés, hors écran, refus source/numéro/mode invalide, vérification de la commande R59 `Aga Bank Image Draw`, double buffer, Swap et fermeture. **Attendu :** `FRAMES 1 1 1 1 SHIFT 1`, `CLIP 1 1 1 1 OUT 1`, `BAD BANK/X/Y/W/M 0 0 0 0 0`, `LEGACY 1`, `RESULT 1`, `CLOSE RETURNED`, aucun Guru. Interrompre manuellement la boucle finale `Do / Wait Vbl / Loop` : `Program interrupted` est normal.

**Gate A native CPU PASS 86 cas ; B/C WinUAE en attente ; D Amiga physique non testée.** Aucune promotion sans B/C, régression complète et accord de l'auteur. [Rapport R60](../../docs/M18_R60_IMAGE_REGION.md).
