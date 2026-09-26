"""Build the handoff report from final engine logs and measured evidence."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[3]
def main():
    q=json.loads((ROOT/'art_pass/evidence/verification.json').read_text())
    films={n:json.loads((ROOT/f'build/dev/film/{n}/film.json').read_text()) for n in ['weapons_final','combat_final','corpses_final','rf01_final']}
    for name,r in films.items():
        assert 'error' not in r,(name,r)
        deficit=r['frames_requested']-r['frames_written']
        assert r['clipped_samples']==0 and (deficit==0 or (name=='rf01_final' and deficit==1)),(name,r)
    assert films['combat_final']['shots']>=30, 'Stress clip must contain sustained actual firing'
    corpse=(ROOT/'build/dev/logs/after_corpses.txt').read_text(encoding='utf8')
    positions=re.findall(r'RF_DEV_CORPSE class=.*',corpse);assert len(positions)==12
    assert all('dz=0.00' in s and 'tics=-1' in s and 'vel=0.00' in s for s in positions)
    for name in ['after_weapons_1080','after_weapons_1440','after_weapons_1610']:
        log=(ROOT/f'build/dev/logs/{name}.txt').read_text(encoding='utf8')
        assert 'RF_ART_EMPTY_RELOAD mag=20 reserve=0' in log
        assert 'RF_ART_PARTIAL_RELOAD mag=20 reserve=10' in log
        assert 'pistol=0' in log
    forbidden=r'Script error|Invalid data encountered|Unknown texture|Unable to load|Could not find'
    for name in ['after_corpses','film_combat_final','film_corpses_final','film_weapons_final','film_rf01_final','norun_hidden']:
        assert not re.search(forbidden,(ROOT/f'build/dev/logs/{name}.txt').read_text(encoding='utf8')),name
    rows='\n'.join(f'| {name} | {r["frames_written"]} | {r["segment_peak_dbfs"]} dBFS | {r["clipped_samples"]} |' for name,r in films.items())
    text=f'''# RF2-ART-01 — livraison de la candidate, 26 septembre 2026

**CANDIDATE_ART_COMPLETE — OWNER_REVIEW_REQUIRED**

La candidate couvre les deux armes, les trois familles ennemies et leurs 320 sprites, trois modèles terminaux, le sang et 66 sons RF01. Elle est produite et testée dans `C:\\PROJECTS\\RF2_UZDOOM_ART`. Le dépôt actif reste sous la responsabilité d'Opus ; aucune intégration dans son arbre n'a été effectuée.

## Accès

- `JOUER_CANDIDATE.cmd` lance le PK3 figé dans `review/`, avec sa configuration et ses sauvegardes séparées. Ce PK3 contient les cartes de la base pour jouer la revue ; **ce n'est pas un remplacement du PK3 actif**.
- `evidence/index.html` rassemble comparatifs, films et son isolé. Les PNG natifs sont dans `evidence/raw/`.
- `MANIFEST.json` décrit les imports, empreintes, formats et modèles à installer explicitement. `files/` ne contient aucune map.
- Sources, prompts exacts et crédits : `files/art/rf2_art_01/`.

## Résultat et couverture

| Famille | Produit / intégré dans la revue | Traitement |
|---|---|---|
| Browning | 7 poses + flash indépendant | Nouvelle vue depuis l'arrière ; mains et manches continues ; culasse rigide ; volume réduit ; vide et sélection conservés, aucune recharge inventée |
| FAL | 20 poses + flash, réexport identique vérifié | Calques Astra conservés, cadrage moins envahissant et son refait ; recharge vide et partielle exercées |
| RFOrderly | 13 états × 8 rotations | Corps, tête, plis, matériaux ; sangle buccale et tenue institutionnelle conservées |
| RFBrancardier | 15 états × 8 rotations | Porteur et brancard ; charge, impact, récupération, douleur et chute couverts |
| RFPorteRegistre | 12 états × 8 rotations | Silhouette d'archives, asymétries, lancer, récupération et chute ; PRGS A/B conservés |
| Cadavres | 3 OBJ + skins ; quatre bindings MODELDEF | ORDY M, RFOrderlyCorpse, BRCD M et PREG K seulement ; les vivants et transitions restent des sprites |
| Sang | 3 frames RGBA | Remplace le sang pixelisé de l'IWAD via RFArtBlood |
| Audio | 66 exports mono PCM16/48 kHz + masters PCM24 | Tirs, mécanismes, variantes d'impacts, voix, pas, chutes, portes, treuil et ambiances |

La source conserve 58 enregistrements sélectionnés, dont quatre ambiances du projet. Les 66 exports audio ont été reconstruits à l'identique sans téléchargement. Les 21 images FAL se reconstruisent à l'identique depuis les calques. Les exports ennemis et Browning sont exécutés, avec leurs paramètres et masters livrés. L'IA n'est pas rappelée pour reproduire les exports : les masters sont figés.

## Base et code partagé

Base immuable : `6e1a31b79a38099f8121e8ac0b53fe7b169cad6f`. Complément Opus consommé : `844b50f`, après `48e2019`. Le delta artistique recommandé est `patch/production.patch`, contre 844b50f. Le diff historique demandé contre 6e1a31b est séparé et marqué REFERENCE_ONLY. Ne pas appliquer ces deux diffs ensemble.

Fichiers de production partagés : SNDINFO, TEXTURES.weapons, MODELDEF, zscript/rf/weapons.zs et zscript/rf/enemies.zs. Le patch `evidence_only.patch` touche uniquement CVARINFO/dev.zs pour les captures Browning, recharges, culasse ouverte et stress audio ; il n'est pas requis pour jouer.

Les six modèles sont fournis comme sources/export sous `art/rf2_art_01/enemies/model_exports/`, puis installés par `python art/rf2_art_01/install_models.py` dans `src/models/rf2_art_01/`. Ce chemin dépasse la liste de préfixes de l'importeur existant ; ce pas d'installation est donc distinct et déclaré. Les OBJ ne sont pas rangés dans l'espace sprites, qui attend des images.

Timings : suites frame/durée BHPG, RFLV, ORDY, BRCD et PREG identiques à Opus 844b50f. Les collisions, vitesses, santé, consommation, cadence et dégâts ne sont pas modifiés par la passe. DamageFunction 9 est le correctif d'Opus, non un rééquilibrage artistique.

RF01.wad SHA-256 : `{q['immutable_map']['src/maps/RF01.wad']}`. Source rf01.py : `{q['immutable_map']['scripts/mapkit/rf01.py']}`.

PK3 de revue SHA-256 : `{q['pk3_sha256']}`. {q['pk3_assets_verified']} ressources vérifiées octet pour octet dans l'archive réellement chargée, noms ZIP sans doublon. Contrôle de compilation UZDoom et check_runtime : PASS.

## Preuves

UZDoom 5.0.1, Freedoom 0.13.0, Vulkan, lightmode 8 de RF01, lumières dynamiques du projet, FOV 90. La configuration complète est jointe (`evidence/review_config.ini`). Aucun gamma ni éclairage global modifié. Captures armes en 1920×1080 et 2560×1440 (HUD 1), 1920×1200 (HUD 1.25). Avant/après 1080p : même position, même orientation et mêmes demandes de capture du pilote ; le rafraîchissement après une capture PNG peut décaler la pose affichée d'un tic ou plus pendant la recharge. Les corps sont comparés en 1280×720 aux mêmes douze placements et points de vue.

Le diagnostic d'acteur confirme 12/12 poses finales avec z−floorz = 0, vitesse nulle et état terminal permanent. Le modèle supprime le redressement du billboard sous la caméra. Les captures comprennent sol plat, mur, seuil et escalier, quatre côtés et plongée.

| Film | Images | Crête du mix | Échantillons écrêtés |
|---|---:|---:|---:|
{rows}

Audio capturé directement par OpenAL Soft (float), master de revue 0.5, SFX 1, musique 1 et mix SNDINFO Opus ; export PCM16 et vidéo AAC **sans modification de gain**. Synchronisation sur bip au tic 1, exclu de l'extrait. `combat_final` est un stress contrôlé : deux vagues de cinq acteurs des trois familles, dans la cour existante, joueur invulnérable. Il ne prétend pas reproduire l'équilibrage d'une rencontre normale. `rf01_final` est un extrait du parcours autonome ordinaire. Les résultats ne constituent pas une audition humaine.

Les timings de performance avant/après sont dans `evidence/performance.json`, sur les quatre mêmes points de vue, sans rendu de sprites en arrière-plan. Ce sont les mesures du callback RenderOverlay sur bureau invisible : elles servent de comparaison locale, pas de garantie de FPS affichés sur un écran ni de budget matériel universel.

Une dernière révision de dynamique concerne exactement sept WAV de tirs, sans hausse de leur plafond de crête. Les films armes/combat/parcours ont été recapturés après cette révision. `evidence/audio_revision.json` établit que toutes les autres entrées du PK3 sont identiques octet pour octet à la version des captures visuelles, du tour des corps et de la mesure de performance conservés.

## Limites pour la revue du propriétaire

- Les corps sont rigides : ils peuvent pénétrer une marche ou un mur selon leur emprise. Le test escalier le montre, il n'est pas masqué. Aucune physique ragdoll ou adaptation au relief n'a été ajoutée.
- Les poses restent peu nombreuses (budgets existants conservés) ; les changements d'angle conservent le langage visuel de sprites à huit directions.
- Le Browning est un master généré, pas une reconstruction CAO certifiée. Le détail du chien et de la prise demande un regard artistique du propriétaire. Le FAL garde les limites d'articulation de ses calques historiques.
- Aucune audition humaine n'a été effectuée par l'agent. La matière des tirs et le confort des voix doivent être jugés à l'écoute, malgré l'absence d'écrêtage mesuré.
- L'extrait RF01 perd une capture PNG (441 images sur 442 demandes) ; sa synchronisation locale est donc approximative après cette perte, indiquée dans film.json. Les trois autres films ont leurs comptes complets et une synchronisation sur bip. Les mesures de crête portent sur le WAV moteur, pas sur un montage normalisé.
- L'approbation artistique, les sauvegardes de la branche active et les régressions finales après fusion restent à Opus/propriétaire. Aucun statut d'approbation n'est inventé.

## Commandes de vérification

Depuis la copie isolée, `RF_DEV_HIDDEN=1` et une seule instance moteur. Le stage de build doit rester sous `C:\\PROJECTS\\RF2_UZDOOM_ART\\build`.

```powershell
pwsh -NoProfile -File scripts/build.ps1
python scripts/hidden_norun.py
python scripts/check_runtime.py
python art/rf2_art_01/review/verify.py
python scripts/devrun.py --name after_weapons_1080 --map RF01 --width 1920 --height 1080 +rf_dev_weapons 1 +screenshot_quiet 1 +rf_hud_scale 1 +r_drawplayersprites 1 +screenblocks 10
python scripts/devrun.py --name after_corpses --map RF01 --width 1280 --height 720 --speed 2 --marker RF_DEV_CORPSE_DONE +rf_dev_corpse 1 +r_drawplayersprites 0 +screenblocks 12 +screenshot_quiet 1
python scripts/film.py --name weapons_final --start 10 --end 430 --every 2 +rf_dev_autopilot 0 +rf_dev_weapons 1 +screenshot_quiet 1 +r_drawplayersprites 1 +screenblocks 10 +rf_hud_scale 1
python scripts/film.py --name combat_final --end 900 --every 3 +rf_dev_autopilot 0 +rf_dev_art_combat 1 +screenshot_quiet 1 +r_drawplayersprites 1 +screenblocks 10 +rf_hud_scale 1
python scripts/film.py --name corpses_final --start 70 --end 1261 --every 3 +rf_dev_autopilot 0 +rf_dev_corpse 1 +screenshot_quiet 1 +r_drawplayersprites 0 +screenblocks 12
python scripts/film.py --name rf01_final --end 1800 --every 4 +screenshot_quiet 1 +r_drawplayersprites 1 +screenblocks 10
```

Crédits et licences : `files/art/rf2_art_01/CREDITS.md`. Prompts exacts et mode de génération intégré : `files/art/rf2_art_01/IMAGEGEN_PROMPTS.md`.
'''
    (ROOT/'art_pass/RAPPORT.md').write_text(text,encoding='utf8')
    note='''# Pour Opus — RF2-ART-01

Candidate disponible, OWNER_REVIEW_REQUIRED. Ouvrir d'abord `evidence/index.html` et `RAPPORT.md` ; `JOUER_CANDIDATE.cmd` utilise uniquement le build de revue figé.

1. Utiliser ton importeur en dry-run sur ce dossier, puis importer les fichiers autorisés. Le manifeste ne contient ni map ni source de map. Examiner tout conflit déclaré par rapport à 6e1a31b.
2. Fusionner `patch/production.patch` (base 844b50f) dans tes cinq fichiers partagés. Les versions de base et le résultat de revue sont inclus. Ne pas appliquer le diff historique REFERENCE_ONLY en plus.
3. Après import, exécuter `python art/rf2_art_01/install_models.py`. Il copie exactement les six exports listés dans `model_install` sous src/models/rf2_art_01. Ces ressources sont nécessaires aux bindings MODELDEF et ne passent pas par les préfixes de l'importeur existant.
4. Le patch `evidence_only.patch` est facultatif et réservé aux outils de revue ; ne pas activer rf_dev_art_combat dans une session joueur.
5. Rebuild, compilation, check_runtime, puis tes régressions de parcours/sauvegardes. Vérifier notamment sélection/rangement, recharges FAL, Browning vide, nouveau BloodType, sons de chute, modèles terminaux et performance après accumulation de corps.

Le redressement des corps face à la caméra est corrigé par les modèles terminaux, sans toucher aux collisions. Limite déclarée : corps rigides pouvant traverser une marche ou un mur. Les clips et captures correspondants sont conservés.

Le son a des sources enregistrées, 66 exports et masters, des variantes et une mesure du mix dense sans gain ajouté. Aucune audition humaine n'est revendiquée. Vérifier le confort réel d'écoute et la hiérarchie au casque/enceintes.

Les messages HUD consomment ton correctif Opus ; aucune refonte du portrait. Les écritures se limitent à la copie artistique et à ce dossier de livraison. Aucun fichier de l'arbre actif n'a été modifié par Codex.
'''
    (ROOT/'art_pass/POUR_OPUS.md').write_text(note,encoding='utf8')
    print('Report gates passed; RAPPORT.md and POUR_OPUS.md written')
if __name__=='__main__':main()
