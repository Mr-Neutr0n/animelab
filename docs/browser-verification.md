# Browser verification and cookie sessions

AnimeLab keeps the HTTP client for normal source requests. If a site requires
browser verification, open its managed verification mode from the blocked search,
catalogue or download. A real browser executes JavaScript; the user completes any
interactive CAPTCHA. AnimeLab does not include a CAPTCHA-solving service.

## Session exchange and automatic resuming

The verification browser receives the relevant HTTP cookies **before** navigating
to the source. While verification is open, AnimeLab exchanges cookie updates in
both directions, including removals. Unrelated domains are excluded and concurrent
HTTP refreshes take precedence over stale browser copies. A proxy/session change
invalidates the exchange instead of reusing cookies on a different route.

Both managed modes suspend new HTTP requests and media streams for the source,
after draining existing connections. Cookie changes synchronize the session only;
they never trigger a parallel emulated HTTP probe. Confirm completion in AnimeLab
or close the managed window. AnimeLab imports the session, stops browser
networking, then resumes the pending operation. Its real response determines
whether access succeeds; a cookie import is not reported as verified access.
Navigation away from a search cancels that search's pending refresh.

Chromium supplies its actual user agent through CDP. Android uses the installed
WebView's default user agent, and desktop WebView keeps its native engine's user
agent. AnimeLab persists the learned user agent with each domain's cookies and
route. It removes incompatible client hints and old Cloudflare clearance when
the browser identity changes, preserving unrelated login cookies. A route change
invalidates both the learned identity and its cookies.

A CAPTCHA, ordinary HTTP 403/451, DNS error, timeout, TLS error or interrupted
transfer never triggers proxy rotation. Only an explicit country/region refusal
can allow one retry through the opted-in proxy pool, before any bytes are exposed.
The manual rotation API applies the same geographic restriction. Manual operator
proxy configuration remains available; keep the same route during verification.
See the [comparative study and source-specific diagnosis](studies/cloudflare-sessions-2026-11-03.md).

Android uses Android System WebView and CookieManager; no additional Chromium
runtime is bundled. CookieManager exposes fewer attributes than Chromium's CDP:
AnimeLab retains attributes of cookies seeded by Python and bounds the lifetime
of newly observed Android cookies to one hour. Unknown non-Cloudflare cookie
paths are restricted to the observed URL, and ambiguous duplicate names retain
their seeded scope rather than merging distinct sessions. A plain external browser tab does
not share its cookies with AnimeLab.

## Choosing an installed Chromium executable

Chrome, Chromium, Edge and Brave are detected automatically on desktop. An
explicit path replaces automatic detection. Firefox is not a CDP-compatible
substitute. Do not put command-line arguments in the executable path.

- **Desktop launcher:** Requests tab → Chromium executable → Browse. Save and
  restart an already running engine to apply the launcher preference.
- **Web interface:** Settings → Proxy & Network → Verification browser. The path
  is on the **engine machine**, not on a remote browser's device. Save outside an
  active verification. These controls are restricted to local personal use.
- **Startup:** use the options below, or the corresponding environment variables.

```bash
python run.py --chromium-path /usr/bin/chromium
./AnimeLab --chromium-path "/opt/My Browser/chrome" --launch
```

Windows example:

```powershell
.\AnimeLab.exe --chromium-path "C:\Program Files\Google\Chrome\Application\chrome.exe" --launch
```

`ANIMELAB_CHROMIUM_PATH` overrides the saved web setting. Desktop launcher values
are passed to the engine at startup; explicit desktop CLI options also update the
saved launcher values. An empty launcher path with headless mode off defers to
the web setting or automatic discovery. When startup settings control the browser, the web form
explains that they must be changed at startup and disables its Save button.
An empty web setting restores automatic discovery.

The browser uses a private profile, a loopback-only debugging endpoint and the
source session's proxy. Proxies requiring authentication are currently unsupported
by managed Chromium verification. Android WebView verification is unavailable
while a proxy is selected. No browser is downloaded automatically.

## Servers without a display or a system WebView

An operator can explicitly enable headless Chromium:

```bash
python run.py --chromium-path /usr/bin/chromium --chromium-headless
```

Equivalent environment settings:

```bash
export ANIMELAB_CHROMIUM_PATH=/usr/bin/chromium
export ANIMELAB_CHROMIUM_HEADLESS=true
```

Headless mode runs the real browser and JavaScript without a display. **It cannot
present an interactive CAPTCHA to the user.** A site may still reject it. For
interactive verification, use a visible browser on the engine machine and omit
`--chromium-headless` (or use `--no-chromium-headless`). The browser sandbox remains
enabled; root-only container setups need an appropriate non-root runtime.

For an authenticated shared server:

```bash
python -m animelab.shared serve --public-url https://anime.example.org \
  --chromium-path /usr/bin/chromium --chromium-headless
```

The operator-selected executable and headless preference are inherited by each
private account engine. A signed-in remote user may start headless verification
only for that account's known blocked source. Cookies/profiles remain in that
account's workspace. Remote users cannot choose executables, open host GUI
windows, or alter operator browser settings. A remote personal server without
account authentication retains the local-only restriction for managed browser
launching. Docker images do not install Chromium; provide it and its system
libraries yourself before setting its path.

## Verification coverage

Regression tests cover scoped cookie exchange, concurrent refreshes, deletion,
proxy changes, local/remote authorization and automatic resuming. A local HTTP
fixture is also exercised with a real installed headless Chromium; this verifies
the integration without attempting to solve a production CAPTCHA. Android Kotlin
compilation checks the bridge, while physical-device/browser-provider behavior
still requires device validation.
