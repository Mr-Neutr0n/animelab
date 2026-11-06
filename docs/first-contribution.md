# Votre première contribution à AnimeLab

[Français](first-contribution.md) | [English](first-contribution.en.md)

Choisissez une seule tâche ci-dessous et commentez son issue avec votre idée,
votre plateforme et l’aide souhaitée. Consultez les commentaires récents avant
de commencer pour éviter un travail en double. Les trois issues sont les points
d’entrée mis en avant ; le [suivi #12](https://github.com/loeuf237/animelab/issues/12)
présente aussi les autres tâches.

Le mainteneur peut aider à définir le périmètre, repérer les fichiers et choisir
les vérifications. Un rapport ou une maquette suffit pour commencer. Objectif de
premier retour : deux jours ouvrés, selon disponibilité. Voir le
[guide de contribution](../CONTRIBUTING.md).

État de référence au **6 novembre 2026** : release **v0.1.6-beta.5** pour les tests
installés ; branche `main` pour documentation et design. Notez toujours le tag ou
le résultat de `git rev-parse HEAD` réellement utilisé. Les essais sur un appareil
ne certifient pas tous les appareils ou toutes les sources.

## Android

**Mission :** documenter un démarrage et une lecture en mode avion sur un téléphone,
dans [#32](https://github.com/loeuf237/animelab/issues/32). Aucun changement Kotlin
ni compilation Android n’est demandé.

**Préparation :** appareil Android 10+ ARM64, [APK bêta.5](https://github.com/loeuf237/animelab/releases/tag/v0.1.6-beta.5)
et petite vidéo que vous pouvez utiliser. Préparez un téléchargement terminé dans
AnimeLab avec des données de test ; ne touchez pas à une bibliothèque personnelle
pour la nettoyer. Si la préparation échoue, décrivez ce blocage sans affirmer que
la lecture hors ligne échoue. Le moteur d’extensions APK reste expérimental.

1. Notez version, modèle, version Android, format vidéo et emplacement privé/exporté.
2. Fermez complètement AnimeLab, activez le mode avion puis rouvrez l’application.
3. Ouvrez les médias disponibles, lancez la vidéo et déplacez la position de lecture.
4. Fermez et rouvrez ; vérifiez la reprise de position. Testez les sous-titres ou
   pistes audio seulement s’ils sont présents localement.
5. Rétablissez la connexion et consignez au plus trois blocages reproductibles.

**Livrable :** un commentaire dans #32 ou une petite PR documentaire avec cette
matrice remplie, des étapes numérotées et des captures utiles :

| Étape | Réussi / échoué / bloqué / non testé | Observation et preuve |
| --- | --- | --- |
| Démarrage en mode avion | À renseigner | |
| Accès aux médias locaux | À renseigner | |
| Lecture et déplacement temporel | À renseigner | |
| Fermeture et reprise de position | À renseigner | |

**Validation :** décrire le résultat observé, y compris un succès ou un blocage,
sans partager cookies, URL signées ou base personnelle. Points d’entrée :
[stockage Android](android-distribution.md), [lecteur](../frontend/src/stores/player.ts)
et [bibliothèque](../frontend/src/views/LibraryView.vue).

## Linux

**Mission :** suivre les instructions existantes puis proposer un court guide
illustré FR/EN dans [#21](https://github.com/loeuf237/animelab/issues/21).

**Préparation :** Linux, Git, Python 3.12/3.13, uv 0.13.1, Node.js 22.13+ dans la
branche 22.x et FFmpeg/ffprobe. Utilisez un compte/profil de test sans bibliothèque
AnimeLab personnelle. L’installation télécharge des dépendances ; une relecture
ou une correction FR/EN peut être proposée sans installer la chaîne complète.

1. Notez distribution, architecture et commit du checkout.
2. Suivez [CONTRIBUTING](../CONTRIBUTING.md#préparer-lenvironnement) et le
   [guide de développement](development.md) pour installer les dépendances et
   compiler l’interface, puis ouvrir le launcher avec
   `uv run --locked --group desktop python desktop.py`.
3. Montrez comment distinguer ce checkout d’une archive de release contenant
   l’exécutable `AnimeLab`. N’inventez pas un exécutable dans le dossier source.
4. Capturez le launcher et l’interface réellement obtenus, les erreurs éventuelles
   et le recours au navigateur si la WebView native manque.
5. Arrêtez le serveur lancé pour l’essai avec le bouton **Stop** du launcher.

**Livrable :** une PR limitée au guide et à ses liens dans les README FR/EN,
avec deux ou trois captures, commandes suivies et prérequis manquants identifiés.
Une difficulté d’installation documentée est aussi un retour utile dans l’issue.

**Validation :** relire les liens, faire correspondre les légendes FR/EN et
indiquer exactement la plateforme essayée. La vérification de Markdown ne prouve
pas un démarrage réel. Réutilisez [desktop.py](../desktop.py) et le
[guide desktop](desktop-distribution.md) ; aucun changement du launcher n’est requis.

## Design

**Mission :** proposer une palette supplémentaire dans
[#28](https://github.com/loeuf237/animelab/issues/28), avec trois aperçus. Aucun
backend, build Android ou nouveau sélecteur de thèmes n’est demandé.

**Préparation :** les quatre palettes et les modes clair/sombre existent déjà.
Lisez [themes.css](../frontend/src/themes.css),
[ThemePicker.vue](../frontend/src/components/ThemePicker.vue),
[appearance.ts](../frontend/src/stores/appearance.ts) et l’[identité visuelle](branding/README.md).
Vous pouvez produire des maquettes statiques sans installer l’application.

1. Nommez la palette et associez chaque couleur à une variable existante,
   notamment `--bg`, `--panel`, `--text`, `--muted`, `--accent` et `--line`.
2. Montrez bibliothèque, extensions et lecteur, avec au moins un aperçu étroit.
3. Présentez texte, focus, sélection et erreur avec des repères autres que la couleur.
4. Relevez les contrastes texte/fond et documentez les limites des variantes
   clair/sombre ; une mesure ou une capture vaut mieux qu’une promesse générale.

**Livrable :** palette documentée et trois images annotées dans #28 ou une PR.
Précisez l’origine/licence des éléments réutilisés. L’intégration au sélecteur
reste une étape séparée, discutée dans #23.

**Validation :** couleurs liées aux vrais tokens, libellés lisibles, état de focus
visible et aperçu mobile. Une maquette n’est pas une preuve de thème intégré.

## Proposer et recevoir une revue

Dans votre commentaire ou PR, indiquez : tâche choisie, résultat proposé,
version/plateforme, vérifications effectuées et aide attendue. Une PR en brouillon
peut être relue tôt. Gardez les changements limités au livrable convenu.

Pour les questions ouvertes, utilisez les
[Discussions](https://github.com/loeuf237/animelab/discussions). Les décisions
techniques restent dans l’issue ou la PR. Les contributions acceptées sont
créditées dans les notes de version, y compris design, tests et documentation.
