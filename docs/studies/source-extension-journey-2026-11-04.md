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
- Une vérification WebView sur une fiche ne proposait pas de reprise de l’opération. Le même mécanisme de session que pour la recherche s’applique désormais aux fiches.
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

En cours : compilation de la version isolée et test sur le Samsung SCV38 (Android 10, ARM64). Ne pas considérer cette section comme une preuve de téléchargement réussi avant ajout du résultat physique.

Aucune rotation de proxy ni publication de release n’est nécessaire à ces vérifications.
