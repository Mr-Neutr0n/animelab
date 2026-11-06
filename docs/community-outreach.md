# Diffusion et accueil des contributeurs

Ce document fournit des messages FR/EN à adapter, ainsi qu’un parcours de suivi.
Les [trois premières contributions](first-contribution.md) et le
[suivi #12](https://github.com/loeuf237/animelab/issues/12) sont les références.
Les textes ci-dessous sont des brouillons, pas des preuves de publication.

## Canaux et règles vérifiées le 6 novembre 2026

| Canal | Format et prochaine action |
| --- | --- |
| GitHub Discussions | Annonce bilingue avec les trois tâches, puis questions publiques dans le fil. |
| r/SideProject | Présentation personnelle et demande précise de retour ; vérifier flair, règles visibles et doublons avant envoi. |
| r/coolgithubprojects | Lien direct du dépôt avec un titre descriptif ; vérifier le formulaire et les règles au moment de publier. |
| r/selfhosted | Commentaire dans le **New Project Megathread actuel** pour un projet de moins de trois mois. Présenter Docker/serveur, et conserver la mention bêta. |
| r/homelab | Retour technique lié à un laboratoire réel ; flair **Project: Software**, déclaration d’usage de l’IA dans le texte et le flair, questions obligatoires du formulaire et karma requis. Ne pas présenter une installation NAS non testée comme validée. |
| Hacker News | Le mainteneur écrit et publie lui-même : les règles excluent texte généré et publication automatisée. Montrer un logiciel essayable avec **Show HN**, sans demande de votes. |
| LinuxFr.org | Journal technique original, ou dépêche étoffée soumise à modération ; préciser licence, fonctionnement, installation et limites plutôt qu’un simple message publicitaire. |
| Discord / forums NAS et Home-Cinema / groupes Telegram | Identifier le groupe exact et son espace projets autorisé ; adapter le message et éviter les envois répétés. |
| Canal Telegram AnimeLab | Canal [@animelabchannel](https://t.me/animelabchannel) identifié ; publier l’accueil puis l’épingler après connexion avec un compte administrateur. |

Sources : [r/selfhosted](https://www.reddit.com/r/selfhosted/about/rules.json),
[r/homelab](https://www.reddit.com/r/homelab/about/rules.json),
[r/SideProject](https://www.reddit.com/r/SideProject/about/rules.json),
[r/coolgithubprojects](https://www.reddit.com/r/coolgithubprojects/about/rules.json),
[Show HN](https://news.ycombinator.com/showhn.html),
[règles HN](https://news.ycombinator.com/newsguidelines.html),
[modération LinuxFr](https://linuxfr.org/regles_de_moderation).
Les réponses JSON vides de certains subreddits ne garantissent pas l’absence de
contraintes supplémentaires dans le formulaire. Relire les règles avant chaque envoi.

L’historique Git commence le 12 septembre 2026 ; à cette date le projet relève
par prudence du fil nouveaux projets de r/selfhosted. Cette date Git ne prouve
pas à elle seule la date de première publication publique. Ne pas qualifier la
bêta de production-ready pour contourner les règles ; demander aux modérateurs
si son admissibilité dans le fil reste incertaine.

## r/SideProject — EN

**Title:** AnimeLab: an open-source anime library app — looking for Android testers and design/docs contributors

I maintain AnimeLab, a GPL-3.0-only project for discovering, playing, downloading
and organizing anime episodes from supported sources. It has a Python/FastAPI
engine, a Vue 3/TypeScript interface, desktop packages, an Android app and a Docker
server mode.

I have added a visual walkthrough and narrowed the contribution entry points to
three tasks: one Android airplane-mode playback report, a short illustrated Linux
setup guide, and a theme palette with three previews. Reports and design work are
welcome alongside code, in English or French.

This is beta software. Android extension compatibility varies; a resolved stream
does not yet prove a complete verified download. I would like feedback on whether
the first-contribution steps are clear and what blocks a new tester or contributor.
AI assistance is used in development and in preparing this announcement.

Repository and demo: https://github.com/loeuf237/animelab
First tasks: https://github.com/loeuf237/animelab/issues/12

## r/coolgithubprojects — EN

**Title:** AnimeLab — GPL anime library, playback and download app with FastAPI, Vue, Android and Docker

**Link:** https://github.com/loeuf237/animelab

**Optional explanatory comment:** I maintain this beta project. The README includes
screenshots and a walkthrough. Contributions are welcome for Android offline
playback testing, an illustrated Linux guide and theme design. English/French
reports and small PRs are welcome. The Android APK extension runtime is
experimental; compatibility and completed-download validation remain limited.
AI assistance is used in development and in preparing this post.
Task tracker: https://github.com/loeuf237/animelab/issues/12

## r/selfhosted — EN, current new-project thread only

**AnimeLab — self-hosted anime library and download interface (beta, GPL-3.0-only)**

I maintain AnimeLab, with a Python/FastAPI backend and Vue/TypeScript web interface.
The repository includes Docker Compose setup, persistent library/settings/download
storage and shared-server documentation. Desktop and Android packages are also
available; Android's original APK extension runtime is a separate experimental
path from desktop/server source recipes.

I am looking for feedback on the Docker setup and documentation, plus contributors
for a Linux walkthrough and theme palettes. Android testers can also help with a
separate offline-playback report. This remains beta software, with source-dependent
failures and incomplete end-to-end Android download validation.
AI assistance is used in development and in preparing this comment.

Code/demo: https://github.com/loeuf237/animelab
Docker guide: https://github.com/loeuf237/animelab/blob/main/docs/docker.md
Tasks: https://github.com/loeuf237/animelab/issues/12

## r/homelab — preparation, not an unqualified advertisement

Use the self-hosted description above only after adding a real deployment report:
host architecture, OS/container runtime, storage mounts, observed resource usage,
backup/restart result and the specific lesson or question for the homelab community.
Fill the software-project prompt in the actual submission form. Select its required
AI disclosure flair and include: **AI assistance is used in development and in
preparing this post.** Do not invent percentages of AI-written code, deployment
measurements, community karma or NAS validation. A generic cross-post is not the
deliverable here. No homelab deployment is certified by this communication update.

## LinuxFr.org — proposition de journal

**Titre :** AnimeLab, une application libre de bibliothèque vidéo : architecture et premières contributions

Je développe AnimeLab, un logiciel sous licence GPL version 3 uniquement, pour
découvrir, lire, télécharger et organiser des épisodes d’anime depuis les sources
prises en charge. Le moteur Python/FastAPI et l’interface Vue/TypeScript sont
utilisables sur ordinateur et via un serveur Docker ; Android embarque également
un moteur local.

Un point technique est la distinction entre les recettes de sources sur
ordinateur/serveur et les véritables extensions APK exécutées sur Android. Les
deux parcours demandent des validations différentes. Les corrections récentes
portent notamment sur la conservation des sessions navigateur, les lecteurs
alternatifs et le passage du résolveur natif dans la file de téléchargement.

Le projet reste en bêta : toutes les extensions ne sont pas validées, les essais
Android de téléchargement complet restent limités et les paquets macOS ne sont
pas testés sur matériel réel. Les notes de version précisent ces limites.
L’utilisation des sources dépend de leur disponibilité et des contenus auxquels
chaque utilisateur a accès.

Pour accueillir des contributions délimitées, je propose trois points de départ :
un rapport de lecture Android en mode avion, un guide Linux illustré FR/EN et une
palette liée aux variables de style existantes. Une contribution peut être un
rapport, une maquette ou une correction documentaire. L’assistance IA est utilisée
dans le développement et la préparation de ce texte.

Le dépôt contient une démonstration et les instructions d’installation :
https://github.com/loeuf237/animelab
Les premières tâches et leurs livrables sont regroupés ici :
https://github.com/loeuf237/animelab/issues/12

Je recherche particulièrement les difficultés rencontrées lors d’une première
installation Linux et les observations permettant de reproduire un problème,
avec version, plateforme et étapes précises.

## Discord, forums Home-Cinema / NAS et groupes Telegram — FR

Bonjour, je maintiens AnimeLab, une application libre (GPLv3 uniquement) de
bibliothèque, lecture et téléchargement d’épisodes, avec interface web et mode
serveur Docker. Je cherche des retours ciblés sur la documentation Linux et la
persistance des données, ainsi que des contributions de design. Des tests Android
hors ligne sont aussi proposés séparément.

Le projet est en bêta ; je ne revendique pas de compatibilité Synology/Unraid
validée sans essai réel. Code, démonstration et limites :
https://github.com/loeuf237/animelab
Tâches délimitées, en français ou anglais :
https://github.com/loeuf237/animelab/issues/12
Un rapport reproductible ou une relecture du guide est déjà utile.
L’assistance IA intervient dans le développement et la préparation de ce message.

## Canal Telegram @animelabchannel — message d’accueil à épingler

Bienvenue dans le canal AnimeLab !

AnimeLab est une application libre pour découvrir, lire, télécharger et organiser
des épisodes sur ordinateur, Android et via une interface web/serveur Docker.
Le projet est en bêta ; le dépôt indique les limites des sources et plateformes.

🎬 Code, captures et démonstration : https://github.com/loeuf237/animelab
📦 Versions et notes : https://github.com/loeuf237/animelab/releases
🤝 Pour contribuer : test Android hors ligne, guide Linux ou palette de thème.
Choisissez une tâche ici : https://github.com/loeuf237/animelab/issues/12
💬 Questions et idées : https://github.com/loeuf237/animelab/discussions

Les contributions FR/EN sont bienvenues, même sans code. Précisez votre version,
votre plateforme et l’aide souhaitée dans l’issue concernée. Le mainteneur vise
un premier retour sous deux jours ouvrés selon disponibilité. Gardons les
résultats techniques dans GitHub pour que chacun puisse les retrouver.

## Hacker News — dossier factuel pour rédaction humaine

Ne pas copier un texte généré dans HN ni automatiser sa publication. Le mainteneur
rédige lui-même son titre, son récit personnel et ses réponses, conformément aux
[règles](https://news.ycombinator.com/newsguidelines.html).

Faits vérifiables à disposition : GPL-3.0-only ; Python/FastAPI + Vue/TypeScript ;
packages desktop et Android ; mode Docker ; captures et démonstration dans le
README ; bêta.5 ; moteur APK Android expérimental ; limites de téléchargement et
macOS dans les notes de version. Liens : dépôt et release ci-dessus.

Pour Show HN, donner un chemin permettant d’essayer le logiciel et expliquer avec
ses propres mots le problème résolu, les choix techniques, son rôle personnel et
les limites. Rester disponible pour les questions. Ne solliciter ni votes ni
commentaires coordonnés. Il ne s’agit pas d’une annonce de recrutement seule.

## Accueil et revue — routine du mainteneur

1. Accuser réception des nouvelles propositions sous deux jours ouvrés lorsque
   disponible ; annoncer une indisponibilité plutôt que promettre un délai ferme.
2. Confirmer le plus petit livrable, proposer un fichier utile et un contrôle ciblé.
   Inviter une PR en brouillon si la personne est bloquée.
3. Relire le résultat, expliquer les changements demandés et garder une distinction
   entre tests simulés, essai réel, design et fonction effectivement livrée.
4. Après intégration, remercier et créditer l’auteur dans les notes de version,
   cocher le suivi #12 et retirer les tâches terminées des appels mis en avant.
5. Chaque semaine, vérifier les trois points d’entrée et consigner les liens de
   publications, propositions reçues, premières PR et blocages. La mesure utile
   est une contribution accompagnée jusqu’au bout, puis un éventuel retour.

**Premier retour FR :** Merci pour ta proposition. Peux-tu préciser ta plateforme
et le résultat que tu souhaites livrer ? Commençons par le périmètre de l’issue ;
je peux aider à repérer les fichiers ou choisir une vérification. Un brouillon
ou un rapport limité est bienvenu.

**First reply EN:** Thanks for the proposal. Please state your platform and the
result you would like to deliver. Let's start with the issue's limited scope;
I can help locate the relevant files or select a check. A draft or focused report
is welcome.

**Revue FR :** Le résultat couvre les points suivants : [à préciser]. Il reste
[un point concret] à vérifier sur [plateforme/scénario]. Peux-tu joindre le
résultat observé ? Nous pourrons ensuite intégrer et créditer ta contribution.

**Review EN:** The result covers [specific criteria]. The remaining check is
[one concrete scenario/platform]. Please attach the observed result so we can
complete review and credit the contribution.
