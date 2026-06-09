"""CRO playbook — the tacit knowledge that turns a funnel drop-off into a
testable hypothesis.

Each funnel transition maps to one or more candidate hypotheses tuned for a
flowers/gifting store (Fig & Bloom). The loop picks the most relevant candidate
for the worst-bleeding transitions, scores it (ICE), and writes it to the
Hypotheses ledger. These are starting points, not gospel — the loop refreshes
evidence each run and an operator can promote/kill them in Notion.

ICE defaults here are the *confidence* and *ease* priors for each play; the
*impact* score is supplied by the loop from revenue-at-risk ranking so that the
backlog is ordered by lost dollars, not gut feel.
"""

# transition key -> list of candidate plays
PLAYS = {
    ("home_collection", "product"): [
        {
            "slug": "collection-merchandising",
            "hypothesis": "Visitors land on Home/Collection but don't reach a product. "
                          "Surfacing best-seller bouquets above the fold with clear price + "
                          "next-day delivery badges will lift collection→product CTR.",
            "friction_signal": "High exits on Home/Collection before any view_item.",
            "expected_metric": "Collection→Product rate (view_item / view_item_list)",
            "confidence": 3, "ease": 4,
        },
    ],
    ("product", "add_to_cart"): [
        {
            "slug": "pdp-delivery-clarity",
            "hypothesis": "On the product page, delivery date/cutoff and total price aren't "
                          "obvious before the CTA. Adding a delivery-date selector and an "
                          "all-in price near Add to cart will lift PDP→cart.",
            "friction_signal": "High view_item with low add_to_cart; gifting buyers need delivery certainty.",
            "expected_metric": "PDP→Cart rate (add_to_cart / view_item)",
            "confidence": 4, "ease": 3,
        },
    ],
    ("add_to_cart", "checkout_started"): [
        {
            "slug": "cart-shipping-surprise",
            "hypothesis": "Shoppers add to cart but stall before checkout, likely from a "
                          "shipping-cost or delivery-window surprise in the cart. Showing "
                          "shipping/delivery up front in the cart drawer will lift cart→checkout.",
            "friction_signal": "Add-to-cart far exceeds begin_checkout for the window.",
            "expected_metric": "Cart→Checkout rate (begin_checkout / add_to_cart)",
            "confidence": 3, "ease": 3,
        },
    ],
    ("checkout_started", "purchase"): [
        {
            "slug": "checkout-trust-payments",
            "hypothesis": "Checkout is started but not completed (confirmed by abandoned-checkout "
                          "value). Adding express wallets (Apple/Google Pay, Shop Pay), a clear "
                          "delivery-date confirmation, and trust signals will lift checkout→purchase.",
            "friction_signal": "Large begin_checkout→purchase bleed and high abandoned-checkout dollar value.",
            "expected_metric": "Checkout→Purchase rate; abandoned-checkout recovered $",
            "confidence": 4, "ease": 3,
        },
    ],
}


def play_for(transition_key):
    """Return the top candidate play for a (from,to) transition, or None."""
    plays = PLAYS.get(transition_key)
    return plays[0] if plays else None
