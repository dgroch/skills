# Medianet draft builder and verification

Use this workflow to create a Medianet press-release draft without distributing it.

## Safety boundary

- Draft creation, image upload and audience assignment are allowed when requested.
- Never click `Submit press release` without explicit approval after final review.
- Preserve placeholders and draft quotes exactly when the user asks for review rather than inventing names, dates, phone numbers or quote approval.
- End on `Save and close`, then verify under `My Press Releases > Drafts`.

## Draft creation sequence

1. Start a fresh Browserbase session attached to the persistent Medianet Context.
2. Navigate to `https://platform.medianet.com.au/press-release` and wait for the Blazor app to render `Set up press release`.
3. Open the Press Release Builder.
4. Map the supplied release into Medianet fields:
   - Headline
   - Company/organisation
   - Email introduction
   - Body content
   - Key facts
   - Media contact information
   - About us
5. Fill headline/company with normal user-input events.
6. For TinyMCE fields, synthetic `setContent()` alone may render visually without updating Medianet's Blazor model. Trigger a genuine iframe-body edit first, restore formatted HTML, then fire TinyMCE `input`, `change`, `blur` and `save()` events. Confirm Save no longer reports mandatory fields missing.
7. Save the content builder and verify the main page preview contains the expected headline, body and source URL.

## Images

- Use images from the live Fig & Bloom article or approved brand assets; do not substitute generic floral photography.
- Header and footer slots specify a maximum width of 600 px. Resize derivatives while retaining the published original as the source.
- Typical mapping:
  - header: contextual/lifestyle image at 600 px width;
  - main: strongest editorial hero image;
  - footer: supporting lifestyle image at 600 px width.
- Medianet uses a shared media dialog for all three slots. Select the intended slot first, upload, add a clear Fig & Bloom caption, then choose `Save media`.
- A Cloudinary preview in the current session proves upload only, not persistence.
- Save using the exact Press Release Builder drawer's own Save handler. Medianet can keep multiple overlapping drawers mounted with `sidebar--open`; do not select a global `Save` button.
- Release the session and verify all images from a wholly fresh session. Required proof:
  - `Attachments (N)` has the expected count;
  - each expected Medianet Cloudinary URL is present in the builder;
  - header/main/footer slots no longer show empty upload states.

## Saved audience assignment

1. Open `Set audiences`.
2. Switch from `MEDIANET LISTS` to `MY LISTS`.
3. Find the exact saved list name.
4. Select the `Add list` button belonging to that list's own row; avoid positional/global Add buttons.
5. Verify the right-hand `Target audience` panel contains the exact list and shows `Added` on its source row.
6. Save the audience drawer.
7. Verify the exact list name on the main draft page and again in a fresh session.

## Medianet UI quirks

- Desktop/mobile controls are often duplicated. Scope actions to visible controls or the intended drawer.
- Drawers can overlap while both carry `sidebar--open`; use stable IDs such as `#select-audience-sidebar` or locate the drawer owning the semantic section.
- Menu items may have zero-size rectangles despite an open opacity-based menu. Invoke the matched row's own handler rather than a global text match.
- The app may expose empty editor controls before Blazor hydration finishes. Wait for the saved headline/body before reading or editing.
- `70% complete` can be valid for a review draft when schedule/category details remain unset. Do not fill distribution details merely to raise completion.

## Final verification contract

From a new Browserbase session using the same persistent Context, verify:

- stable draft URL and draft ID;
- exact headline;
- source article URL in body HTML;
- exact saved audience name;
- expected image/attachment count and media URLs;
- appearance under `My Press Releases > Drafts`;
- no evidence that Submit was clicked or distribution occurred.

Report unresolved editorial placeholders separately so the reviewer sees what still requires approval.
