# Sessions Cloudflare : Aniyomi, Suwayomi et correctifs AnimeLab

Étude et diagnostic du 3 novembre 2026. Périmètre : moteur partagé Linux,
Windows et macOS, WebView Android et extensions APK utilisant sa passerelle HTTP.

## Conclusion

`curl_cffi` reproduit certaines caractéristiques HTTP/TLS d'un navigateur, mais
n'exécute pas le JavaScript d'une page et ne devient pas une WebView. Un refus
n'établit donc pas à lui seul que Cloudflare a « détecté curl ». Il faut distinguer
challenge, interdiction explicite, DNS, délai réseau et restriction géographique.

La correction conserve les requêtes ordinaires dans le moteur et utilise un vrai
navigateur pour la vérification assistée. Elle maintient une identité de session
cohérente, suspend les appels de la source pendant la vérification et reprend
l'opération réelle après fermeture. Le changement de proxy est désormais réservé
aux réponses indiquant explicitement une restriction géographique.

Cela corrige les défauts identifiés d'AnimeLab. Cela ne garantit pas qu'un site
acceptera toujours une application tierce ou qu'un jeton obtenu par navigateur
sera accepté par un autre transport.

## 1. Aniyomi : WebView et client HTTP partagent la session

Révision étudiée : `97414446b8a95994c72dd33c41c971a89d4d25b8`.

Le [CloudflareInterceptor](https://github.com/aniyomiorg/aniyomi/blob/97414446b8a95994c72dd33c41c971a89d4d25b8/core/common/src/main/java/eu/kanade/tachiyomi/network/interceptor/CloudflareInterceptor.kt)
reconnaît certains refus, ferme la réponse et supprime l'ancien `cf_clearance`.
Il exécute ensuite une vraie WebView, attend le chargement ou un renouvellement
du cookie, détruit cette WebView et rejoue la requête initiale. L'attente est bornée.
Ce n'est pas un mécanisme de rotation d'adresses IP.

[AndroidCookieJar](https://github.com/aniyomiorg/aniyomi/blob/97414446b8a95994c72dd33c41c971a89d4d25b8/core/common/src/main/java/eu/kanade/tachiyomi/network/AndroidCookieJar.kt)
utilise Android CookieManager pour les lectures et écritures du client HTTP.
Le [WebViewInterceptor](https://github.com/aniyomiorg/aniyomi/blob/97414446b8a95994c72dd33c41c971a89d4d25b8/core/common/src/main/java/eu/kanade/tachiyomi/network/interceptor/WebViewInterceptor.kt)
active JavaScript et le stockage DOM et utilise l'agent utilisateur de la
requête ou son fournisseur par défaut.
Le [UserAgentInterceptor](https://github.com/aniyomiorg/aniyomi/blob/97414446b8a95994c72dd33c41c971a89d4d25b8/core/common/src/main/java/eu/kanade/tachiyomi/network/interceptor/UserAgentInterceptor.kt)
respecte un agent utilisateur explicitement fourni par l'extension.

Conséquence pour AnimeLab : partager les cookies pertinents et conserver
l'identité utilisée pour la vérification, au lieu de fabriquer une nouvelle
identité à chaque appel. La politique AnimeLab force l'identité apprise pour
le domaine vérifié afin de préserver cette session ; avant vérification, un
agent utilisateur explicitement fourni par une extension reste respecté.

## 2. Suwayomi : session du navigateur et réponse de secours optionnelle

Révision étudiée : `7b061be09c9b62a89a63addd11ac91c40fc2510f`.

Le [CloudflareInterceptor de Suwayomi](https://github.com/Suwayomi/Suwayomi-Server/blob/7b061be09c9b62a89a63addd11ac91c40fc2510f/server/src/main/kotlin/eu/kanade/tachiyomi/network/interceptor/CloudflareInterceptor.kt)
coordonne les résolutions simultanées par hôte. Avec FlareSolverr configuré,
il réutilise les cookies et **l'agent utilisateur retourné par le navigateur**,
puis réessaie la requête. La session du service a une durée de vie et des délais
bornés. La configuration peut transmettre un proxy au navigateur ; cela n'impose
pas de rotation pour chaque challenge.

Une option `flareSolverrAsResponseFallback` permet, si la reprise HTTP échoue,
de retourner la réponse réussie du navigateur pour les cas pris en charge.
Elle montre une limite importante : importer un cookie ne prouve pas que la
requête suivante, envoyée avec un autre transport, sera acceptée.

[KcefWebView](https://github.com/Suwayomi/Suwayomi-Server/blob/7b061be09c9b62a89a63addd11ac91c40fc2510f/server/src/main/kotlin/suwayomi/tachidesk/global/impl/KcefWebView.kt)
est un véritable moteur Chromium/CEF, avec échange des cookies persistants du
serveur. Il ne s'agit pas de modifier seulement des en-têtes curl.

AnimeLab ne déploie pas FlareSolverr et ne transforme pas du DOM capturé en
réponse HTTP supposée équivalente. Le transfert des réponses complètes est une
fonctionnalité distincte, non implémentée dans ce correctif. Une extraction
incorrecte perdrait notamment statuts, en-têtes, redirections ou données POST.

## 3. Défauts identifiés et changements

| Défaut | Correction |
| --- | --- |
| Agent Windows/Chrome imposé à Chromium, à la WebView et aux requêtes | Chromium fournit son UA via CDP ; Android fournit celui du WebView installé ; la WebView desktop conserve celui de son moteur. |
| En-têtes de navigateur ajoutés implicitement par curl | Désactivation des en-têtes automatiques ; suppression des client hints `sec-ch-ua*` incompatibles lorsque l'identité du domaine a été apprise. |
| Ancienne option « Random (Rotator) » changeant l'UA des appels natifs | Cette préférence historique utilise désormais le fournisseur stable par défaut. |
| UA du navigateur perdu au redémarrage | Persistance par domaine avec les cookies, liée à la même route ; suppression lors d'un changement de route. |
| Cookies de clearance associés à l'ancienne identité | Suppression de `cf_clearance` et `__cf_bm` lors d'un changement d'UA appris, y compris les sessions historiques sans UA connu ; conservation des autres cookies de connexion. |
| Appels HTTP concurrents pendant la vérification Chromium | Même verrou de session que pour WebView : drain des connexions existantes, refus des nouvelles requêtes et flux. |
| Sonde HTTP exécutée alors que Chromium est ouvert | Suppression de la sonde ; import, fermeture, libération de la source, puis reprise de l'opération. |
| Reprise déclenchée au simple changement d'un cookie | Synchronisation seule pendant l'ouverture ; reprise à la confirmation ou à la fermeture observée. |
| Rotation sur CAPTCHA, 403, 451 ou coupure réseau | Rotation uniquement après indice géographique explicite ; un 403/451 seul ne suffit pas. |
| Rotation après réception partielle d'une vidéo | Suppression ; reprise Range/HLS sur la même route en conservant les données reçues. |
| Proposition « changer de proxy » sur un challenge | Retirée du panneau de vérification ; autres boutons conditionnés au diagnostic géographique du serveur. |
| Actualisation du pool public avant contrôle de la cause | Refus côté API avant toute actualisation si aucun blocage géographique n'est identifié. |
| Refus WAF d'un fichier optionnel mettant toute la source en attente | Portée limitée à l'URL refusée ; les vrais interstitiels conservent la suspension du domaine. L'ouverture de la WebView suspend toujours tous ses appels. |

Les refus HTML Cloudflare 403/503 personnalisés ouvrent aussi la vérification
assistée, même sans les marqueurs habituels. Un refus ordinaire sans ces indices
reste distinct d'un challenge. Les flux remontent désormais les catégories DNS,
TLS et timeout aussi précisément que les requêtes synchrones.

Un challenge explicite `cf-mitigated: challenge` garde priorité sur un texte
mentionnant un pays. Les restrictions géographiques reconnues comprennent des
messages explicites de pays/région et l'erreur Cloudflare 1009. Les mécanismes de
limitation existants continuent de respecter les attentes et ne provoquent pas
une rotation d'IP. Les transferts actifs interdisent toujours la rotation.

## 4. Diagnostic des sources signalées

Les adresses ci-dessous proviennent des extensions présentes dans la base locale,
consultée en lecture seule. Les essais n'ont modifié ni cette base ni les cookies
personnels. Ils ont utilisé une session isolée, sans proxy, sans lecture vidéo,
avec au plus 64 Kio de corps inspecté dans le diagnostic final.

| Source / adresse configurée | Résultat depuis cette connexion le 3 novembre | Interprétation |
| --- | --- | --- |
| Anime-Sama, `https://anime-sama.to/` | HTTP 200, serveur Cloudflare, échantillon de 65 536 octets | Cloudflare n'interdit pas systématiquement ce transport sur la page d'accueil. Recherche, lecteur et hébergeur restent des étapes différentes. |
| OtakuFR, `https://otakufr.cc/` | Erreur de transport à l'ouverture, sans réponse HTTP exploitable | Aucun challenge ni blocage géographique démontré. Ne pas changer de proxy automatiquement. |
| AniSama, `https://v1.animesz.xyz/` | Échec de résolution DNS locale (`getaddrinfo`) | Pas de réponse Cloudflare à diagnostiquer ; vérifier l'adresse actuelle de l'extension. |

`https://www.otakufr.org/` répondait aussi en HTTP 200 lors d'un premier contrôle,
mais ce n'est **pas l'adresse configurée dans l'extension installée**. Ce résultat
ne valide donc pas OtakuFR dans AnimeLab et ne justifie pas de changer son domaine
sans vérifier la compatibilité de l'extension.

Ces premières mesures portent sur cette machine et ce moment. Elles ne constituent
pas une validation complète des trois extensions. Les essais complémentaires sur
le téléphone sont décrits ci-dessous.

## 5. Validation et limites

Les régressions couvrent la persistance et la portée de l'UA, les cookies de
connexion conservés, les redirections, les flux, l'absence de rotation sur
challenge/refus ordinaire, les restrictions géographiques, et les reprises exactes
Range/HLS après interruption. Des tests avec le **Chrome réellement installé**
exercent les échanges CDP et imposent la fermeture avant reprise ; un serveur
local exige à la fois le cookie reçu et le véritable UA du navigateur.

Résultats locaux : **plus de 1 000 tests Python réussis, 5 ignorés**, contrôles Ruff et
Mypy réussis, **37 tests frontend réussis**, compilation Vue réussie et **5 essais
Playwright ciblés réussis** dans le Chrome installé (mobile/desktop, français et
anglais, reprise et politique des proxys).

### Complément : recherche et plantage sur le téléphone reconnecté

La recherche réelle `Bleach`, avec la recette Anime-sama installée sur le PC,
appelle `/catalogue/?s=Bleach` et renvoie **12 résultats en 6,1 secondes**. La
réponse de la page d'accueil seule n'aurait pas suffi à le vérifier. Cet essai
ne valide pas encore le transport de l'APK sur le téléphone.

Le SCV38 reconnecté expose plusieurs crashs de `com.animan.app` les 2 et 3 novembre :
`java.io.IOException: write failed: EPIPE (Broken pipe)` dans l'exécuteur du
pont HTTP. Le lecteur du processus d'extensions peut disparaître avant la fin de
la réponse (annulation, dépassement de délai ou arrêt du worker). L'écriture
non protégée faisait alors tomber le processus principal. Le pont ferme désormais
son descripteur et traite cette rupture comme l'échec d'une seule requête ; il
ferme aussi les deux descripteurs si la file du réseau refuse la tâche.

Une régression Android ferme volontairement le lecteur avant une grosse réponse,
puis exige qu'une requête suivante réussisse sans exception échappée de
l'exécuteur. L'instrumentation des APK optimisés inclut cette régression.
Les routes catalogue/filtres conservent également les catégories réseau détaillées
au lieu de toutes les masquer sous « La source est momentanément inaccessible ».

Un candidat optimisé signé, construit depuis `9677824`, a été installé par mise à
jour sur le **Samsung SCV38, Android 10**, en conservant les données. Son certificat
correspond à celui de l'application installée. Les **deux tests du pont** passent
sur ce téléphone : lecteur fermé et exécuteur refusant une tâche. Le processus
principal est ensuite resté ouvert plus de vingt minutes sans nouvelle exception
`EPIPE`. L'exécution complète du candidat `c080a1e` passe aussi sur les émulateurs
Android 11 et 15 : démarrage du moteur et deux régressions du pont. Android 10 x86
valide les sondes natives, sans prétendre exécuter le moteur ARM64 complet.

Le téléphone utilise **l'APK Anime-sama 14.33**, distinct de la recette PC 14.31.
L'ouverture de l'accueil provoque un accès optionnel à
`https://anime-sama.to/catalogue/dragon-ball-super/film/vostfr/episodes.js`.
Cette URL renvoie un **HTTP 403 Cloudflare « Sorry, you have been blocked »**,
sans challenge interactif ni indication géographique. Le même refus apparaît
dans la véritable WebView Android. L'import de session ne permet donc pas
d'affirmer que cette ressource est accessible.

Le refus de ce fichier mettait jusqu'ici **tout le domaine** en vérification.
Une recherche `Bleach` était ainsi rejetée avant même de contacter son catalogue.
Après fermeture de la WebView et libération de cette attente, la recherche réelle
de l'APK a affiché les saisons de Bleach sur le téléphone. La correction distingue
désormais ce refus limité à une URL d'un véritable interstitiel, qui reste associé
au domaine. Six régressions couvrent cette distinction pour les requêtes ordinaires,
les réponses bornées et les flux, ainsi que le maintien de la suspension complète
pendant l'ouverture du navigateur. Une septième régression conserve un challenge
de domaine lorsqu'un refus de fichier arrive ensuite sur une requête déjà en vol.
Les opérations qui reçoivent effectivement un
refus continuent de le signaler ; aucun changement de proxy n'est déclenché.

Avec le correctif `3d894e9`, un essai réel isolé sur PC a d'abord reçu ce même
refus sur `episodes.js`, puis recherché `Bleach` dans la même session, avec la
recette extraite de l'APK 14.33 : **12 résultats en 5,9 secondes**, sans ouverture
de navigateur ni rotation de proxy. Cet essai vérifie la reprise des autres URL,
pas l'accès au fichier refusé ni la lecture de toutes les vidéos.

### Premier candidat de contrôle sur le SCV38

Le candidat signé construit depuis `2322836a970bb40fda425ee93199572d94bbe371`
a ensuite été installé comme mise à jour sur le même téléphone. Son empreinte
SHA-256 est `09f4ca5bfee3e61fdb09c5e51bf6f5892d19a01172d633d4bcd6fd819cf9a526`.
Le certificat correspond à l'installation existante et les données sont conservées.

- Les **deux tests du pont HTTP passent** sur le téléphone. Des fermetures de
  lecteurs ont aussi été traitées pendant les appels réels, sans exception fatale
  ni arrêt du processus principal.
- La recherche réelle de l'APK Anime-sama renvoie **9 résultats pour Bleach en
  9,1 secondes**, visibles dans l'interface, sans ouverture de WebView ni rotation
  de proxy. L'essai PC et celui du téléphone utilisent respectivement la recette
  extraite et le véritable APK ; leurs nombres de résultats sont consignés
  séparément.
- La fiche **Bleach Saison 1** charge son titre, son image et sa description,
  mais la liste d'épisodes revient **vide**. Cet essai ne valide donc pas la
  lecture ni le téléchargement de la série. Une exception réseau avalée par
  l'extension peut masquer un refus sous une liste vide ; l'observation seule
  ne prouve pas que le site n'a aucun épisode.

La [CI générale](https://github.com/loeuf237/animelab/actions/runs/41678376485),
la [validation des extensions APK](https://github.com/loeuf237/animelab/actions/runs/41678376600)
et le [candidat Android signé](https://github.com/loeuf237/animelab/actions/runs/41678386986)
passent sur cette révision. Python 3.13 en CI rapporte **1 110 tests réussis,
8 ignorés**. L'application optimisée passe ses trois tests sur Android 11 et 15,
en complément des sondes natives Android 10. Le workflow de validation ne publie
aucune release.

### Cause supplémentaire : origine absente lors du chargement des scripts

Un essai contrôlé avec **trois sessions PC indépendantes**, même transport et
même UA, a donné sur le script VOSTFR de Bleach Saison 1 : **403 sans Referer,
200 avec `Referer: https://anime-sama.to/`, puis 403 sans Referer**. Avec cet
en-tête, les scripts VOSTFR et VF renvoient respectivement 53 866 et 52 756 octets
de JavaScript. La simple ouverture de leur URL dans une WebView ne fournit pas
ce contexte de page ; son refus ne démontre donc pas un blocage général du
navigateur ou une interdiction géographique.

L'extension amont appelle `GET(docUrl)` sans ses en-têtes de source dans
`fetchPlayers`, puis transforme les exceptions en liste vide. Le client source
AnimeLab fournit désormais une origine publique aux requêtes GET/HEAD de scripts
JavaScript de **la même origine** lorsqu'aucun Referer n'est fourni. Les en-têtes
explicites, y compris un Referer vide, sont conservés. Les autres hôtes, ports,
schémas, méthodes et médias sont exclus. Les changements de domaine de la source
sont pris en compte sans reconstruire son client ; les identifiants, le chemin,
la requête et le fragment des préférences ne sont jamais copiés dans cet en-tête.

Cette adaptation de compatibilité est propre à AnimeLab ; ce n'est pas un
comportement attribué à l'intercepteur Cloudflare d'Aniyomi. La régression Android
exerce le véritable client de source dérivé jusqu'au pont, avec un transport
contrôlé, et vérifie la portée ainsi que la conservation des en-têtes.

Complément du 4 novembre : le moteur PC, avec la recette extraite de l'APK 14.33,
renvoie **12 résultats de recherche et 366 épisodes pour Bleach Saison 1** en
11,1 secondes au total. Les tests du runtime incluant la portée du Referer passent
sur les émulateurs Android 10, 11 et 15. Les résultats complémentaires du candidat
signé avec cette correction sont consignés dans la
[validation de la PR nº 39](https://github.com/loeuf237/animelab/pull/39).

Le contrôle réel a aussi identifié un délai trop court dans la recherche globale :
les APK, identifiés par un numéro de source, étaient annulés au bout de 12 secondes
alors que leurs appels peuvent développer saisons et films. Le moteur PC disposait
déjà d'un budget plus large pour ces catalogues. Les recherches APK disposent
désormais de 60 secondes côté API, pour laisser répondre leur worker borné à
45 secondes et sa passerelle parent bornée à 55 secondes. Six régressions vérifient
qu'une expansion peut finir après l'ancien délai et qu'un appel bloqué reste annulé,
en recherche ciblée comme en recherche globale.

Les essais d'interface vérifient la reprise et l'absence de promesse « accès
vérifié ». L'instrumentation Android compare également l'UA exposé aux extensions
à celui du WebView installé. Une compilation ne remplace pas l'exécution de cette
instrumentation ni un essai des sites sur le téléphone de l'utilisateur.

Cloudflare documente des échecs liés à l'UA, aux IP différentes, aux WebView et
aux navigateurs automatisés. Si un site exige le navigateur pour chaque requête,
le partage de cookies seul peut rester insuffisant. AnimeLab conserve alors un
état de vérification explicite ; aucune boucle de rotation de proxy n'est lancée.

Références officielles :

- [Aniyomi : diagnostic](https://aniyomi.org/docs/guides/troubleshooting/diagnosis).
- [Cloudflare : échecs de résolution](https://developers.cloudflare.com/cloudflare-challenges/troubleshooting/challenge-solve-issues/).
- [Cloudflare : navigateurs pris en charge](https://developers.cloudflare.com/cloudflare-challenges/reference/supported-browsers/).
- [Cloudflare : fonctionnement des challenges](https://developers.cloudflare.com/cloudflare-challenges/concepts/how-challenges-work/).
- [Cloudflare : portée de la clearance](https://developers.cloudflare.com/cloudflare-challenges/concepts/clearance/).
