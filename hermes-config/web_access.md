---
title: Web Access
description: Copy Paste Web Access Instructions
published: true
date: 2026-07-14T15:59:59.497Z
tags: hermes, private
editor: markdown
dateCreated: 2026-07-14T14:09:52.130Z
---


```
Configure the complete Hermes Agent web stack as a subscription-free, privacy-conscious setup.

The desired behavior is:

1. Use SearXNG for web search.
2. Use a local Hermes web-extraction plugin for static/public HTML pages.
3. Use the configured CDP browser as a fallback for JavaScript-rendered pages and screenshots.
4. Disable unused, subscription-based, or incorrectly configured web providers.
5. Test every layer and report only verified results.
6. Do not claim that a component works unless it was actually exercised.

Target SearXNG instance:

https://search.pub.bitbull.ch

CDP configuration:

Use the existing BROWSER_CDP_URL environment variable.

Never print, log, expose, or include the value of BROWSER_CDP_URL in output.

The authoritative Hermes documentation for this task is:

https://hermes-agent.nousresearch.com/docs/user-guide/features/web-search

======================================================================
PHASE 1 — INSPECT THE INSTALLATION
======================================================================

Before making changes, inspect the active Hermes installation.

Determine:

- HERMES_HOME
- Hermes config path
- Hermes environment file path
- Hermes source/plugin path
- active Hermes profile
- available web providers
- available browser providers
- whether BROWSER_CDP_URL is set
- whether SEARXNG_URL is already configured
- whether paid web-provider credentials are configured

Use the actual Hermes installation paths. Do not assume that $HOME/.hermes is correct if HERMES_HOME is set.

Typical paths are:

- $HERMES_HOME/config.yaml
- $HERMES_HOME/.env
- $HERMES_HOME/plugins/
- bundled Hermes plugins under the Hermes installation source tree

Before changing anything, create timestamped backups:

- $HERMES_HOME/config.yaml.bak-webstack-<UTC_TIMESTAMP>
- $HERMES_HOME/.env.bak-webstack-<UTC_TIMESTAMP>

Do not print secret values. It is acceptable to report only whether a variable is set or unset.

======================================================================
PHASE 2 — CONFIGURE SEARXNG SEARCH
======================================================================

Ensure this environment variable exists in:

$HERMES_HOME/.env

Required value:

SEARXNG_URL=https://search.pub.bitbull.ch

Do not put this URL into a subscription/API-key field.

Ensure the environment file has restrictive permissions:

chmod 600 "$HERMES_HOME/.env"

Configure the Hermes web search backend in:

$HERMES_HOME/config.yaml

Required configuration:

web:
  search_backend: searxng

Do not configure SearXNG as an extraction backend.

SearXNG is search-only in Hermes:

- supports web_search: yes
- supports web_extract: no

Test the SearXNG endpoint directly:

curl --fail --silent --show-error \
  --get 'https://search.pub.bitbull.ch/search' \
  --data-urlencode 'q=Hermes Agent' \
  --data-urlencode 'format=json'

Verify that:

- HTTP succeeds
- the response is JSON
- the response contains a results array
- at least one result is returned

Then test the actual Hermes SearXNG provider, not only curl.

Use a real search query, for example:

site:bitbull.ch bitbull

Verify:

- provider is available
- provider reports success=true
- results are normalized to Hermes format
- every result has title, url, description, and position

======================================================================
PHASE 3 — INSTALL A LOCAL EXTRACTOR PLUGIN
======================================================================

Install a user plugin under:

$HERMES_HOME/plugins/web/local_extractor/

The plugin must contain:

- plugin.yaml
- __init__.py
- provider.py

Use the Hermes WebSearchProvider interface:

from agent.web_search_provider import WebSearchProvider

The provider must have:

name:
  local-extractor

display_name:
  Local HTML Extractor

is_available():
  return True

supports_search():
  return False

supports_extract():
  return True

The plugin must register itself through the plugin context:

def register(ctx):
    ctx.register_web_search_provider(LocalExtractorProvider())

The plugin manifest must identify it as a backend and provide the provider name:

name: web-local-extractor
version: 1.0.0
description: "Local subscription-free HTML extractor using Python standard library only."
author: local-operator
kind: backend
provides_web_providers:
  - local-extractor

The local extractor must not require:

- a paid subscription
- an API key
- Firecrawl
- Tavily
- Exa
- Parallel
- Brave Search
- an external extraction service
- a third-party cloud endpoint

Prefer the Python standard library only, including:

- urllib.request
- html.parser.HTMLParser
- html
- re
- socket
- ipaddress
- urllib.parse

The extractor should:

1. Accept one or more public HTTP(S) URLs.
2. Fetch pages locally.
3. Use a clear User-Agent such as:
   Hermes-Agent-local-extractor/1.0
4. Use a finite request timeout, preferably 20 seconds.
5. Limit the response body to approximately 2 MB.
6. Decode UTF-8 safely with replacement for invalid bytes.
7. Extract the document title.
8. Extract readable text from:
   - headings
   - paragraphs
   - list items
   - blockquotes
   - preformatted text
   - normal article/body text
9. Remove or ignore:
   - script
   - style
   - noscript
   - template
   - svg
   - canvas
   - nav
   - footer
   - form
10. Normalize excessive whitespace.
11. Return Hermes-compatible result objects:

{
  "url": "...",
  "title": "...",
  "content": "...",
  "raw_content": "...",
  "metadata": {
    "extractor": "web-local-extractor",
    "content_type": "...",
    "bytes_read": 123
  }
}

12. Return a per-URL error instead of failing the entire batch when one URL fails.
13. Limit the returned content to a safe maximum, for example 500,000 characters.
14. Reject invalid URLs.
15. Accept only http and https URLs.
16. Reject localhost and localhost.localdomain.
17. Resolve the hostname before connecting.
18. Reject destinations that resolve to non-global/private/loopback/link-local/reserved IP addresses.
19. Do not follow a redirect to a private or internal destination without re-checking it.
20. Never include credentials or sensitive query parameters in extracted URLs.

This is a simple static HTML extractor. It does not execute JavaScript.

======================================================================
PHASE 4 — ENABLE THE SEARXNG SEARCH PLUGIN AND LOCAL EXTRACTOR
======================================================================

Configure the routing backends:

web:
  search_backend: searxng
  extract_backend: local-extractor

Enable both provider plugins using the exact path-derived plugin keys:

plugins:
  enabled:
    - web/searxng
    - web/local_extractor

Important identifier distinction:

- `web/searxng` is the bundled plugin key and must be present in `plugins.enabled`.
- `searxng` is the provider name used by `web.search_backend`.
- `web/local_extractor` is the user plugin key.
- `local-extractor` is the provider name used by `web.extract_backend`.

Do not assume that configuring `web.search_backend: searxng` enables the plugin. Verify that the plugin itself is enabled and loaded.

Do not edit Hermes core files unless there is no supported plugin mechanism and the operator explicitly authorizes a core change.

After changing the configuration, run Hermes plugin discovery in a fresh process.

Verify both plugins:

- plugin is discovered
- source and kind are correct
- plugin is enabled
- plugin has no load error
- SearXNG provider name is `searxng`
- SearXNG provider is available
- SearXNG supports_search() is true
- SearXNG supports_extract() is false
- local provider name is `local-extractor`
- local provider is available
- local provider supports_extract() is true
- local provider supports_search() is false

======================================================================
PHASE 5 — DISABLE UNUSED WEB PROVIDERS
======================================================================

Disable web providers that require paid subscriptions, API keys, or are not configured.

Use the exact plugin keys reported by Hermes plugin discovery.

For the standard bundled Hermes providers, the intended disabled list is:

plugins:
  disabled:
    - web-tavily
    - web-exa
    - web-parallel
    - web-firecrawl
    - web-brave-free
    - web-xai
    - web-ddgs
    - browser-browserbase
    - browser-firecrawl
    - browser-browser-use

Important:

- The correct Brave plugin key is web-brave-free.
- Do not use web-brave_free.
- Do not disable web-searxng.
- Enable the bundled SearXNG plugin with the exact key `web/searxng`.
- Do not disable the local extractor plugin.
- Do not disable the browser provider required for the existing CDP fallback unless Hermes specifically reports that the provider is unused and the local CDP path remains available.
- If the installed Hermes version uses different plugin identifiers, inspect plugin.yaml and use the identifiers from the running installation.
- Do not disable unrelated messaging, model, memory, or platform plugins merely because they are not web providers.

Do not configure a fake extraction backend just to make the configuration appear complete.

======================================================================
PHASE 6 — CDP FALLBACK
======================================================================

Use BROWSER_CDP_URL for browser access.

CDP must be used when:

- a page is JavaScript-rendered
- static HTML contains little or no useful content
- the page requires interaction
- a screenshot is requested
- visual rendering must be verified
- the static extractor returns an empty or obviously incomplete result
- the target site refuses non-browser HTTP access

Never expose the CDP URL value.

Test CDP with a public page such as:

https://example.com

Verify:

- a page target is available
- navigation succeeds
- the accessibility snapshot contains visible page text
- the page title or heading is visible
- browser console output contains no unexpected JavaScript errors
- screenshots render actual visible content rather than a blank page, loading placeholder, or error page

For screenshots, use browser/CDP rendering. Do not use curl or raw HTML as a substitute for visual verification.

======================================================================
PHASE 7 — FULL TEST MATRIX
======================================================================

Run all of the following tests.

TEST A — Hermes configuration

Load the configuration through Hermes itself.

Verify:

- YAML/config parsing succeeds
- web.search_backend == "searxng"
- web.extract_backend == "local-extractor"
- SEARXNG_URL is set
- the local plugin is enabled
- disabled provider identifiers are present

TEST B — SearXNG search

Run the actual Hermes SearXNG provider.

Query:

site:bitbull.ch bitbull

Verify:

- success=true
- result count is greater than zero
- normalized result objects contain:
  - title
  - url
  - description
  - position

TEST C — Direct local extraction

Extract:

https://example.com

Verify:

- no error
- title is "Example Domain"
- content contains "Example Domain"
- metadata identifies web-local-extractor

TEST D — Hermes web_extract dispatch

Call the real Hermes web_extract tool, not only the provider class.

Extract:

https://example.com

Verify:

- the selected backend is local-extractor
- the result contains a successful result
- no SearXNG search-only error is returned
- title and readable content are present

If the tool still selects SearXNG after the local plugin is configured, stop and diagnose plugin discovery/backend resolution. Do not report success.

TEST E — Multiple URLs

Extract both:

https://example.com
https://wiki.bitbull.ch/

Verify:

- results are returned per URL
- one failed URL does not discard other results
- content is present where static HTML is sufficient
- incomplete JavaScript pages are identified as incomplete rather than silently reported as complete

TEST F — SSRF and input validation

Test:

http://127.0.0.1:1
http://localhost/
not-a-url
file:///etc/passwd

Verify that all are rejected before network access.

TEST G — SearXNG and local extractor together

Verify the final routing:

web_search:
  -> SearXNG

web_extract for public static HTML:
  -> local-extractor

web_extract for JavaScript-rendered/interactive pages:
  -> CDP fallback

screenshots:
  -> CDP

TEST H — CDP visual verification

Navigate to:

https://example.com

Verify visually:

- "Example Domain" heading is visible
- paragraph text is visible
- "Learn more" link is visible
- no loading or error placeholder is visible
- the page is not blank
- browser console has no unexpected errors

======================================================================
PHASE 8 — RESTART/RELOAD
======================================================================

Configuration and plugin changes require a new Hermes process or session.

For an interactive Hermes session:

/reset

For a gateway installation:

hermes gateway restart

If the CLI is unavailable globally, use the actual Hermes launcher or service/container restart mechanism discovered during inspection.

Do not claim that the running old session uses the new plugin until a new process/session has loaded it.

======================================================================
PHASE 9 — OPERATIONAL SAFETY
======================================================================

Keep secret redaction enabled.

Do not print:

- API keys
- OAuth tokens
- auth.json contents
- .env values except sanitized variable names and set/unset status
- BROWSER_CDP_URL
- private infrastructure credentials

Preserve unrelated configuration.

Do not overwrite existing user configuration blindly.

Create a backup before editing.

Keep the local plugin under the active HERMES_HOME so it follows the active profile and survives normal Hermes restarts.

Remove generated __pycache__ directories or other temporary artifacts if they are not needed.

Do not add generated files to the project repository unless explicitly requested.

======================================================================
ACCEPTANCE CRITERIA
======================================================================

The task is complete only if all applicable criteria are verified:

1. SearXNG is configured at:
   https://search.pub.bitbull.ch

2. The bundled SearXNG plugin is enabled with:
   web/searxng

3. Hermes search uses:
   web.search_backend: searxng

4. A local extractor plugin exists at:
   $HERMES_HOME/plugins/web/local_extractor/

5. Hermes discovers and enables:
   web/local_extractor

6. Hermes extraction uses:
   web.extract_backend: local-extractor

7. Static HTML extraction succeeds without a subscription or API key.

8. SearXNG search succeeds through the real Hermes provider.

9. The real Hermes web_extract dispatch succeeds through local-extractor.

10. Invalid/private/internal URLs are rejected.

11. CDP is available through BROWSER_CDP_URL.

12. CDP navigation succeeds on a public test page.

13. CDP screenshot/visual verification succeeds when requested.

14. Unused paid/unconfigured web providers are disabled using exact plugin identifiers.

15. No API key or subscription is required for SearXNG, local extraction, or CDP.

16. Any limitation involving JavaScript-heavy pages is explicitly reported.

======================================================================
FINAL REPORT FORMAT
======================================================================

At the end, report:

- changed files
- backup files
- final web configuration, excluding secrets
- enabled/disabled web plugins
- SearXNG test result
- local extractor test result
- full web_extract dispatch result
- SSRF/input-validation result
- CDP navigation result
- CDP screenshot/visual result
- whether a restart/new session is required
- known limitations, especially JavaScript-rendered pages

Separate verified facts from assumptions.

Never report a test as passed unless real tool output confirms it.
```