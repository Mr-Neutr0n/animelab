# Sources, extensions et épisodes — validation du 4 novembre 2026

## Périmètre

L’explorateur conserve les sources intégrées, les recettes desktop et les vrais APK Android. Les captures Aniyomi servent de référence visuelle : navigation Sources / Extensions, listes par langue, sources épinglées, identité du paquet et réglages. Il ne s’agit pas de copier des fonctions non implémentées comme un mode privé par extension.

Les dépôts, importations, mises à jour, diagnostics, recompilations et éditeurs de recettes restent accessibles. Les APK conservent l’approbation explicite du signataire, la révocation, la désinstallation partagée, les interrupteurs de source, les alias et les préférences fournies par l’extension. Les paquets natifs installés ne sont pas dupliqués dans le catalogue ; leur mise à jour individuelle reste accessible.

## Défauts corrigés

- L’inférence par domaine pouvait remplacer l’APK Voiranime choisi par le fournisseur intégré du même site. Une source choisie correspondant à ce domaine est maintenant prioritaire. La résolution média ne remplace plus une source explicite par une autre extension repérée au hasard sur le même domaine.
- Le téléchargement par lot accédait à `container.recipe` pour les APK natifs, alors que cette propriété appartient aux recettes desktop. La validation des sélecteurs reste appliquée aux recettes.
- Les candidats vidéo pouvaient être fusionnés par URL, perdant une qualité native ou ses données internes. Le repli conserve les objets distincts, même avec une URL commune.
- La préférence de qualité était ignorée quand un serveur correspondait déjà. Lecture et téléchargement partagent désormais un classement stable par serveur puis qualité ; les autres candidats restent disponibles en repli.
- L’estimation de taille ne transmettait pas les en-têtes du flux natif. Elle conserve désormais le Referer et l’agent utilisateur reçus de l’extension.
- Un épisode natif VF héritait de VOSTFR par défaut. Sa version est maintenant reprise du nom, du chemin ou de la série lorsqu’ils la précisent ; sinon elle reste non précisée. Le studio/auteur et le statut natifs peuvent être présentés sans inventer « En cours ».
- Une réponse de fiche lente pouvait remplacer une série plus récente. Les réponses obsolètes sont ignorées, y compris après avoir quitté la page.
- Une vérification WebView sur une fiche ou dans le lecteur ne proposait pas de reprise de l’opération. Le même mécanisme de session que pour la recherche s’applique désormais aux fiches et à la résolution vidéo. Fermer le lecteur annule sa reprise en attente.
- « Commencer » et « épisodes suivants » suivaient l’ordre renvoyé par l’extension, souvent décroissant. Ils partent maintenant du premier épisode non vu de la version sélectionnée. Une liste vide propose une nouvelle tentative et aucun bouton de lecture inactif.

Les numéros fractionnaires natifs restent conservés dans les métadonnées ; la numérotation de la file reste entière. Cette modification ne constitue pas une migration générale de l’identité des épisodes.

## Contrôles reproductibles

```sh
.venv/bin/python scripts/check.py python
cd frontend
npm test
npm run lint
npm run build
npm run test:ui
```

Les tests Python utilisent une bibliothèque et un dossier de téléchargement temporaires. Les tests Playwright utilisent des réponses contrôlées, sans accès aux données personnelles ni aux sites de streaming. Ils ne démontrent pas à eux seuls le fonctionnement des hébergeurs réels.

Le test Android `SourceJourneyTest#installed_anime_sources_to_download` est facultatif, limité à l’application séparée `com.animan.app.a11test`, et exige `live_sources=true`. Il utilise exclusivement les APK Anime-sama et Voiranime déjà installés, les approuve dans cette installation de test, puis vérifie recherche, fiche et résolution vidéo. `download_episode=true` ajoute un seul épisode par source, avec un nom `AnimeLab validation …` ; ce téléchargement utilise le réseau et peut être volumineux. Les journaux ne contiennent ni cookies ni URL de vidéo signée. Les résultats sont enregistrés dans `source-journey.json` dans les fichiers externes de l’application de test.

## Essais réels PC

Extensions importées depuis les APK installés sur le SCV38, avec le moteur de recettes desktop :

| Extension | Recherche | Fiche | Résolution |
| --- | --- | --- | --- |
| Anime-sama 14.33 | Bleach : 12 résultats | Bleach, saison 1 : 366 épisodes | 3 lecteurs candidats, flux Vidmoly résolu |
| Voiranime | One Piece : 10 résultats | One Piece Film: Red (VF) : 1 épisode | Flux Vidmoly résolu |

Ces essais PC ont validé la résolution, pas encore le téléchargement complet ni la lecture intégrale. La version APK Android est une exécution native différente : ses résultats physiques doivent être consignés séparément ci-dessous.

## Réception Android

Première réception sur le Samsung SCV38 (Android 10, ARM64), APK isolé du commit `5ed222a641f05db1db1d40294fa90d50a2a109b5`, SHA-256 `750b80ec1920dc2af92423a43e3be2f7c53cb7a3bc484085413d316d7e63889f` :

- Anime-sama 14.33 : 14 résultats, Bleach saison 1, 366 épisodes ; résolution vidéo interrompue par une réponse HTTP 409. Aucun téléchargement complet validé à ce stade.
- Voiranime 14.3 : 10 résultats, One Piece Film: Red (VF), un épisode ; le pilote excluait à tort le numéro 0 utilisé pour ce film. Cette erreur du pilote a été corrigée et ne constitue pas un défaut de l’APK.

Le second essai (`8462667`) a chargé le film et son numéro 0, puis obtenu un HTTP 404 à la résolution ; Anime-sama a renvoyé une recherche sans résultat exploitable. L’analyse DEX ordinaire de Voiranime 14.3 montre que son résolveur attend `thisChapterSources`. Ce bloc est présent sur l’épisode de la série Sousou no Frieren 2 (VF) vérifié sur PC : 4 résultats de recherche, 10 épisodes, un lecteur Vidmoly et un flux résolu. La prochaine réception cible cette série plutôt qu’un film.

L’audit du moteur a aussi révélé qu’un `TimeoutCancellationException` était déclaré `cancelled` (409), ce qui ne prouve donc pas un blocage Cloudflare. Le budget unique de 45 s a été remplacé par des budgets bornés par opération : 90 s pour recherche/fiche, 120 s pour les listes de lecteurs/vidéos, 60 s pour la résolution finale. Le parent dispose de 15 s de marge et peut toujours arrêter un worker non coopératif ; les échéances personnalisées des tests restent prioritaires. L’API de recherche autorise 120 s et conserve désormais le code d’erreur natif. Une expiration devient `extension_runtime_timeout` (504), distincte de l’annulation volontaire et d’une vérification de site. Un test coroutine réel vérifie cette distinction, et 45 régressions Python ciblées passent.

Le premier essai a révélé l’absence de vérification/reprise dans le lecteur. Le correctif et le pilote ajusté font l’objet d’une nouvelle réception, suivie dans la [PR nº 40](https://github.com/loeuf237/animelab/pull/40). Les résultats de cette première réception ne prouvent pas le téléchargement complet.

Validation locale du moteur : 1 127 tests réussis, 5 ignorés. Interface : 110 scénarios couverts, dont un relancé après un dépassement de délai en exécution parallèle ; puis 40 tests unitaires et 6 tests navigateur ciblés réussis après l’ajout de la reprise du lecteur et la compaction des sources. La CI Android 29/30/35 du commit `5ed222a` est réussie.

Aucune rotation de proxy ni publication de release n’est nécessaire à ces vérifications.


## File de téléchargement native : défaut reproduit puis corrigé

La réception physique du commit `171c476` a trouvé 14 résultats et 366 épisodes Anime-sama, puis résolu le flux. La tâche a ensuite échoué à 0 octet : la file utilisait encore `resolve_imported_video_stream` au lieu de `AndroidAPKSource.resolve_candidate`. Le registre supprimait aussi le fragment de l’URL d’épisode avant le rappel de l’extension, ce qui pouvait perdre son identité ou sa référence interne.

Le chemin effectif de transfert conserve désormais l’URL complète, les candidats natifs et leurs données internes, et appelle le résolveur de l’APK. Il transmet les en-têtes et pistes au moteur de transfert. Les recettes desktop conservent elles aussi leur fragment d’épisode. Une source APK indisponible ne se replie pas sur un extracteur générique.

La régression exécute la vraie file, le téléchargement HTTP via un transport contrôlé et la vérification FFprobe d’un MP4 synthétique. Elle couvre les numéros 0 et 7, deux vidéos partageant la même URL opaque mais des données internes différentes, les en-têtes nécessaires et l’absence de copie finale en double. Elle n’est pas une preuve de téléchargement d’un épisode réel : cette réception doit être ajoutée dans la PR après essai du nouvel APK.

## Réception du 5 novembre

L’APK de test du commit `1d9dadb4770e4e8a5ae6827f88a02fb5704188da` (SHA-256 `d712bf3b1a8a21e358f9f1e2e735184791fd8ab767811b41bbb2c3894949d3d0`) a été reconstruit à partir de l’artefact CI, puis vérifié avant installation. La CI générale (7 jobs) et Android (5 jobs) de ce commit est réussie. Seuls l’application de validation séparée et son pilote ont été remplacés.

- Anime-sama 14.33 : après une première tentative interrompue par `network_timeout`, la reprise trouve 14 résultats, Bleach saison 1 et ses 366 épisodes, résout l’épisode 1 VOSTFR puis transfère **17 916 023 octets**. La limite de 480 s du téléchargement est atteinte avec l’état `DOWNLOADING`, `UNVERIFIED`, export en attente. Le défaut de résolution à 0 octet est corrigé ; le téléchargement complet et son intégrité ne sont pas validés. L’instrumentation est terminée et son processus n’est plus actif.
- Voiranime 14.3 : 4 résultats pour Frieren, fiche Sousou no Frieren 2 (VF), 10 épisodes ; la résolution de l’épisode 1 renvoie 404 sans flux exploitable. Ce résultat ne démontre ni une incompatibilité générale de l’APK ni un blocage Cloudflare.
- Sur PC, une tentative complète Voiranime atteint le téléchargement HLS, puis dépasse la limite d’essai de 600 s avec des expirations réseau de segments. Aucun fichier complet n’est validé.

L’essai de la vraie file sur PC a également révélé un cas distinct : une référence d’épisode peut être un lien de lecteur connu accompagné du fragment `players`, qui conserve les lecteurs alternatifs. Le chemin rapide sautait alors la recette et perdait ces alternatives. La recette sélectionnée développe maintenant toute référence avec fragment avant le choix d’un extracteur ; une régression couvre explicitement un lien Sibnet avec `players`. Les 16 tests ciblés de file native, parcours d’épisode et flux importés passent après cette correction.

Les reçus physiques et ces limites restent distincts des tests synthétiques. Aucun changement de proxy ni nouvelle release n’a été effectué.
