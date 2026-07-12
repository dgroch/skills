# Persistent Medianet browser session

Use this when Medianet authentication must survive separate browser tasks or agent restarts.

## Preferred pattern: Browserbase Context

A normal Browserbase/Firecrawl task is ephemeral. For durable authentication, create a dedicated Browserbase **Context**, then attach every Medianet session to that same Context with persistence enabled.

1. Confirm the active Hermes profile has Browserbase credentials configured. Never print their values.
2. Create one Context via `POST https://api.browserbase.com/v1/contexts` or the Browserbase SDK.
3. Store only the non-secret Context ID in a profile-scoped state file such as `browser_auth/medianet-browserbase.json`, mode `0600`.
4. Create a session using the project ID and:
   - `browserSettings.context.id = <stored context id>`
   - `browserSettings.context.persist = true`
   - `keepAlive = true` while waiting for human login
5. Navigate the session to `https://www.medianet.com.au/` through Playwright/CDP.
6. Obtain `debuggerFullscreenUrl` from the session debug/live-view endpoint and give that temporary URL to Daniel.
7. Daniel enters credentials and MFA directly inside Live View. Do not type, request, log or store the password or MFA code.
8. Once Daniel confirms he is signed in, end the first session cleanly. Context changes are committed when the session closes.
9. Wait several seconds for Context synchronisation.
10. Start a completely new session with the same Context ID and visit an authenticated Medianet page.
11. Verify account-only UI is present and the public `Login` state is absent. Only then report persistence as working.

## Runtime and verification details

- If the active profile's system Python does not expose the Browserbase SDK, run the existing profile script in an isolated environment rather than installing globally: `uv run --with browserbase --with playwright python <script> ...`.
- Reuse the stored Context ID, but treat stored session IDs and Live View URLs as temporary and potentially expired. Generate a new session/Live View whenever human login is required.
- A public Medianet page can contain generic words such as `dashboard`, `campaign`, or `media release`. Do not treat those substrings as authentication evidence. Logged-out detection should include visible `Login`/`Log in`/`Sign in`; authenticated verification should require account-only UI or an account-only URL and absence of the public login state.
- `keepAlive=true` may leave a Browserbase session running after a CDP client disconnects. After Daniel confirms login, explicitly release/end the Browserbase session and verify it is no longer `RUNNING`; persistence is committed on session closure, not merely when Playwright disconnects.
- Only after closure and a short Context-sync delay should a wholly new session be created for the proof test. Do not reuse the login session as persistence evidence.

## Operational rules

- One Context per site/login identity; do not mix Medianet with unrelated websites.
- Avoid concurrent sessions using the same Context because sites may rotate or invalidate cookies.
- Contexts can live indefinitely, but Medianet may expire or revoke its own login cookies; detect logged-out state and request a fresh human login when necessary.
- Live-view URLs and session IDs are temporary handles. The Context ID is the durable handle.
- Never report success after the initial login alone. The required proof is a second, fresh session authenticated by the persisted Context.
- Keep the Context scoped to the active Hermes profile. Do not write browser state into another profile without explicit direction.

## Backend choice

- Browserbase Contexts are suitable when a secure human-in-the-loop Live View is needed remotely.
- Camofox `browser.camofox.managed_persistence: true` is an alternative when a persistent Camofox server and a secure VNC/live-view channel already exist.
- Firecrawl session TTL alone is not durable authentication; do not use it as proof of persistence.
