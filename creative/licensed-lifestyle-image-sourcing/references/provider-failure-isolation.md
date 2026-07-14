# Provider failure isolation for licensed lifestyle image sourcing

## Why this exists

Licensed stock providers are fallback sources after the owned Fig & Bloom asset library. They should improve the run, not make it brittle. During a blog refresh, the Pexels official API key was present but Pexels returned `403` with provider body `error code: 1010` from the runtime environment. Unsplash was still reachable and returned valid candidates.

The durable lesson is not "Pexels is broken". It is: **provider failures must be isolated** so one provider cannot abort the whole image-sourcing waterfall.

## Required behaviour

When querying `providers=pexels,unsplash`:

1. Query owned asset library first as usual.
2. Query each licensed provider independently.
3. If a provider fails:
   - capture `{provider, error, status/body excerpt}` in `providers[]`;
   - return no candidates for that provider;
   - continue with the remaining providers.
4. If at least one provider returns usable candidates, proceed.
5. If no licensed candidates are usable, fall through to generated brand photography or escalate with the exact missing/error state.
6. Do not silently hotlink arbitrary web images to compensate.

## Selection and tracking

- Unsplash selections must trigger the selected image's `download_tracking_url` and record the HTTP result.
- Pexels selections should record photographer/source/licence metadata from the API response.
- Keep provider and photographer metadata in the blog run report or manifest sidecar.

## Blog refresh pattern

For Fig & Bloom blog posts, the best outcome often combines:

- owned Fig & Bloom product/context image; plus
- licensed lifestyle context image, e.g. bedside table, card-writing desk, wrapped present, candle/table scene.

Use licensed imagery only for lifestyle/context, never as a fake Fig & Bloom floral product.
