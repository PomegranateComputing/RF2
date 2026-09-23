# ASTRA -> FABLE HANDOFF

À la fin d'un batch :

1. `manifest.json` complet ;
2. SHA-256 réels ;
3. fichiers runtime présents ;
4. source modifiable présente si applicable ;
5. evidence/planche de contrôle ;
6. README indiquant limites ;
7. validation `scripts/validate_astra_batch.py` exécutée si possible.

Ne copie rien dans `src`.

Message de handoff recommandé :

`Batch <ID> prêt sous incoming/astra/<ID>. Validation structurelle: PASS/FAIL. Aucune intégration runtime effectuée. Incertitudes: ...`
