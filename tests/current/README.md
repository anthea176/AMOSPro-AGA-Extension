# M17/R59 — test actif unique

**Candidate :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib) R59 v0.13.4, **32 984 octets**, SHA256 `00d56b03fa455c851501fe19ac98e0cea46c04a7c8c7786b94042ffcced6b08d`. **53 commandes, 60 entrées AP20, monolithe V2 30 782 octets**, aucune donnée artificielle à 40 Ko. `LAST_GOOD` R57 protégée (SHA256 `aee712c8fee75982c74421acc023fdaad733e3f390f3e143050765802c7925d0`).

**Seul ASC actif :** [`M17_R59_COMPACT_V2_01.asc`](M17_R59_COMPACT_V2_01.asc), sans ressources externes. Installer la bibliothèque R59 dans `APSystem`, redémarrer complètement AMOS et le Compiler. Importer par **Project → Merge ASCII** puis tester **en interprété (Gate B)** ; compiler **le même ASC dans un NOUVEL exécutable** et lancer ce fichier (Gate C). Ne jamais réutiliser le programme exécutable R58.

Le test exerce `Aga Probe` d'origine avant ouverture et après fermeture, écran AGA PAL 320×256×32, double buffering, Palette, Safe, Clear, Fill, Copy, Swap, retour AMOS. Attendu : `AGA PROBE RETURNED`, `AGA PROBE AFTER CLOSE RETURNED`, **`RESULT 1`**, `CLOSE RETURNED`, aucun Guru. La boucle finale `Do / Wait Vbl / Loop` est interrompue manuellement.

**R59 Gates A CPU/CI, B interprétée WinUAE et C compilée WinUAE : PASS** (deux captures utilisateur distinctes du 12/11/2026, `RESULT 1`, `CLOSE RETURNED`, sans Guru visible ; la sortie `Program interrupted` en mode interprété correspond à l'arrêt manuel de la boucle finale). **Gate D Amiga physique : NON TESTÉE.** R58 reste la preuve distincte du franchissement des 32 Ko (Gates A/B/C PASS), [test exact archivé](../passed/M17_R58_COMPILER_BRIDGE_01.asc). Ne pas promouvoir R59 sans accord explicite de l'auteur et régression complète sur son HEAD exact. `main` uniquement.
