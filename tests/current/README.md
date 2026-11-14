# R76 C2P Convert — test actif ; Gate B WinUAE PASS (14/11/2026)

**Candidat :** [R76 v0.13.21](../../dist/AMOSPro_AGA.Lib), 54 144 octets, 66 commandes, 73 AP20. **Gate B RPG PASS** (programmes M0), **Gate B C2P Convert PASS** sur captures + fichier RAM utilisateur. **Gate C Compiler non testee**, Gate D Amiga physique non testee ; R73 LAST_GOOD demeure protegee.

**Un seul ASC actif :** [C2P_R76_CONVERT_01.asc](C2P_R76_CONVERT_01.asc). Le test a produit `RAM:C2P_R76_RUNTIME.TXT` sur la session WinUAE rapportee, et termine normalement avec `End`. La valeur réelle `PRG_STATE 1` signifie **RUNTIME**, pas Compiler. Le CPU signale par Exec etait **68030**.

## Resultat confirme

- Ecran AGA 320x256, profondeurs 16/32/64/128/256 couleurs, deux conversions + swaps explicites, bande sur la deuxieme frame.
- `RESULT 1`, `VERDICT PASS`, `PASS_DEPTH 5`, `FAIL_DEPTH 0`, `CLOSE_COUNT 5`, `ERR 0`, `NOS 0`.
- Chip Free : 1 799 064 avant/apres, delta 0. Fast Free : 138 134 008 -> 138 215 952 (+81 944 octets libres ; ecart a documenter, pas une fuite).
- **Attention au focus :** sur le dernier ecran 256 couleurs, l'ASC attend `Aga Key=69` (Echap). Si AMOS est au premier plan, Echap ne sort pas du test AGA. Dans la session validee, l'auteur a utilise **Amiga+A** pour retrouver le focus du rendu AGA, puis Echap ; Ctrl+C auparavant avait seulement interrompu le programme AMOS, sans Guru.

## En cas de nouvel essai

Garder `LIBS:c2p.library` v1.9 et la banque DATA 12 libre, utiliser R76 dans le slot AGA habituel et importer le seul ASC courant par Merge ASCII. Ne pas relancer une Gate C Compiler sans decision explicite. Le rapport RAM porte le nom `RAM:C2P_R76_<MODE>.TXT` avec le mode annonce par `Prg State`. Copier le journal hors de RAM: avant reboot ou nouvel essai du meme mode (fichier volatile, ecrase par `Open Out`).

[Rapport C2P R76 Gate B](../../docs/C2P_R76_CONVERT_WINUAE_GATE_B_2026-11-14.md) · [Protocole RAM](../../docs/AMOS_RAM_TEST_LOGGING.md) · [Rapport RPG R76](../../docs/C2P_R76_RPG_REGRESSION_2026-11-14.md).
