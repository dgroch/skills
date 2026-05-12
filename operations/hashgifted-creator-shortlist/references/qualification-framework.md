# Qualification Framework

Use this for pre-communication applicant qualification. The goal is to build a strong shortlist, not to select creators.

Apply rules in order. First hard failure wins.

## Hard Gates

Recommend `decline` when the creator fails a non-negotiable campaign gate:

- Location outside the allowed region. For Fig & Bloom, allowed delivery regions are Melbourne, Sydney, and Brisbane metro areas only.
- Required platform missing.
- Follower minimum not met when the campaign has a true minimum.
- Excluded category present.

If the hard gate evidence is not reliable, use `manual_review` rather than decline. If the creator appears otherwise strong but delivery location is merely unconfirmed, mark the recommendation with warning `metro_eligibility_unconfirmed` so `hashgifted-creator-select` asks before final selection.

## Brand Safety

Recommend `decline` for clear brand-safety mismatches:

- Gambling-heavy content.
- Alcohol-heavy identity or venue content unless campaign explicitly allows it.
- Controversial politics or conspiracy content.
- Crypto or scam-adjacent promotion.
- Overtly laddish humour or content that would feel jarring next to premium floral gifting.

Gaming and streaming creators are usually weak fits for floral gifting. Use `manual_review` only if there is a strong lifestyle or gifting angle.

## Campaign Objective Fit

For `audience awareness`, prioritise:

- Audience relevance to the campaign occasion.
- Strong local or demographic alignment.
- Real engagement and comments.
- Creator trust with their audience.

For `content library`, prioritise:

- Visual quality and consistency.
- Strong reels/video ability when video deliverables are likely.
- Product, home, lifestyle, beauty, food, fashion, interiors, events, or gifting context.
- Ability to show an emotional or visual story without heavy direction.

For `both`, require at least medium strength on audience and content quality.

## Fig & Bloom Aesthetic Fit

Apply `hashgifted-ops-manager/references/brand-aesthetic-rubric.md`.

Recommend `shortlist` when the creator is a strong fit for the shared rubric and the current campaign objective.

Strong shortlist signals observed in successful Fig & Bloom bouquet runs:

- Home/interiors/styling contexts where flowers can naturally appear on a bench, table, shelf, entry, bedroom, or living space.
- Motherhood/family creators with warm home routines, young children, gifting occasions, nursery/family table scenes, or authentic domestic storytelling.
- Hosting, food, cafe, recipe, table setting, celebration, wedding/bridal, self-care, and lifestyle grids that can plausibly frame a bouquet as a gift or occasion moment.
- Soft/premium visuals: natural light, clean neutrals, gentle colour, editorial lifestyle, uncluttered compositions, or existing floral/bouquet imagery.
- Prior successful/relevant brand behaviour, especially visible Fig & Bloom, floral, gifting, hamper, home, food, beauty, or self-care sponsored content.

Weak or pass signals for bouquet shortlisting, unless another strong compensating signal is present:

- Fashion-only, bikini/glamour-only, travel-only, nightlife/event-only, performance/theatre-only, pet-only, fitness-only, text/meme-heavy, product-spam, or generic beauty/skincare grids with no plausible bouquet/home/occasion context.
- Controversial political content, inflammatory commentary, or brand-adjacent safety risk.
- Very low visible quality or chaotic UGC where flowers would feel cheap/transactional rather than premium.
- Follower count alone without visual fit; high reach is not enough if the grid cannot carry a Fig & Bloom bouquet naturally.

## Campaign Calibration

Apply the one-off campaign note after hard gates and safety:

- Mother's Day: mums, family creators, lifestyle, beauty, food, and emotionally warm content are strong signals.
- Local campaigns: location confidence matters more than follower count; for Fig & Bloom, final selection requires explicit Melbourne/Sydney/Brisbane metro confirmation in the creator thread.
- Content-library campaigns: visual quality and consistency matter more than audience size.
- Audience-awareness campaigns: audience relevance and engagement matter more than polish alone.

## Engagement Quality

Use the shared brand rubric for engagement judgement.

Use `manual_review` when:

- Follower count is strong but comments look thin or generic.
- The grid is chaotic but there are a few strong relevant posts.
- Location or audience fit is plausible but not proven.
- Social profile is private, deleted, rate-limited, or unavailable and Hashgifted signals are otherwise promising.

## Shortlist Balance

Build a sensible mix of nano, micro, and mid-tier creators. Do not fill the shortlist with one tier unless the campaign asks for it.

## Default Posture

When in doubt, use `manual_review` rather than decline. Decline is final; manual review preserves optionality without prematurely advancing the creator.

In user-approved auto-shortlist mode, `manual_review` means “leave unmutated and note if useful,” not “ask mid-run.” Complete the full queue, shortlist only confident fits, then report the remaining uncertain/pass population without taking decline actions unless explicitly authorised.
