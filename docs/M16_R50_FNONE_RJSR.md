# M16/R50 — contrôle bénin de la liaison `Rjsr` sous AMOS

Le 12/11/2026, **R48 Gate B PASS** : `Aga Image Capture` est reconnue et ses six arguments sont correctement transmis. **R49 Gate B FAIL** : WinUAE plante après `BEFORE GETADR` lorsqu'une unique routine `Rjsr Bnk.GetAdr` est ajoutée au code.

R50 remplace uniquement le marqueur `Rjsr 297` par **`Rjsr 322`**, index source officiel de `FnOne`, qui exécute `moveq #1,d3` puis `Ret_Int` (aucun accès mémoire). Le wrapper reprend exactement la même signature, la même structure AP20, la même taille **32 012 octets** et le même nombre de commandes que R49. Il retourne `1` si l'appel est revenu, `0` pour les arguments non conformes. **Aucune capture ni allocation, aucun écran ni accès à une banque.**

[Candidate installable de diagnostic](../dist/AMOSPro_AGA.Lib), [archive immuable](../dist/experimental/AMOSPro_AGA_M16_v0.12.5_R50_RJSR_FNONE_PROBE.Lib), SHA256 `984cbd5f6485c9f1133eafe356d23c290b2e457902d4f518df3776ffbb5f5eef`, [test courant](../tests/current/M16_R50_FNONE_RJSR_PROBE_01.asc).

**Gate A CPU/CI PASS :** [run 43257098060](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43257098060) — six tests simulés. **Gate B de R50 NON TESTÉE** ; Gate C NON TESTÉE. Si `RESULT 1`, le mécanisme général de `Rjsr` fonctionne au moins pour cette routine, et le diagnostic revient à `Bnk.GetAdr` ou à sa cible. Si crash avant `AFTER`, réexaminer la relocation `Rjsr` sans utiliser d'autres entrées de banque. **R46 C1 LAST_GOOD inchangée**.

Importer le seul test `tests/current/` sous AMOS interprété. Aucune banque 11 à réserver ou vider, aucun retour au compilateur.

## Gate B : FAIL — 12/11/2026

Capture utilisateur : `R50 MAIN RJSR FNNONE PROBE`, puis `BEFORE RJSR FNON`, puis **Amiga Software Failure 80000004** (instruction illégale). Aucun `AFTER` ni `RESULT`. R49 `Bnk.GetAdr` avait fait planter le processus WinUAE ; ici, la routine `FnOne` est sans accès mémoire, ce qui implique le chemin générique `Rjsr` et/ou sa destination, **sans PC exact pour attribuer définitivement l'instruction**. R50 est FAIL en interprété et ne doit pas être retestée ni promue. Suite ciblée : une sonde R51 qui lit le marqueur `Rjsr` après chargement **sans l'exécuter**, afin de savoir si le chargeur AMOS l'a converti en `JSR` réel.
