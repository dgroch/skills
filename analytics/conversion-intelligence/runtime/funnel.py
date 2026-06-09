"""Locked funnel definition for the Conversion Intelligence Programme.

This is the single source of truth for how the funnel is measured. Every GA4
read uses these steps, in this order, with these GA4 event names — so that
drop-off is comparable run over run and pre/post.

Confirmed funnel (do not change without a deliberate re-baseline):

    Collection/Home -> Product (bouquet) -> Add to cart -> Checkout started -> Purchase

Mapped to GA4 enhanced-ecommerce events. If the store does not emit one of
these events, fix the GA4 tagging rather than swapping the event here — the
whole point is a stable measurement contract.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class FunnelStep:
    key: str            # stable identifier used in code + dedup keys
    label: str          # human label, matches Notion "Funnel step" options
    ga4_event: str      # GA4 event that marks reaching this step


# Ordered, top of funnel first.
FUNNEL_STEPS = [
    FunnelStep("home_collection", "Home/Collection", "view_item_list"),
    FunnelStep("product", "Product (bouquet)", "view_item"),
    FunnelStep("add_to_cart", "Add to cart", "add_to_cart"),
    FunnelStep("checkout_started", "Checkout started", "begin_checkout"),
    FunnelStep("purchase", "Purchase", "purchase"),
]

# Transition labels match the Notion "Funnel step" select options exactly, so
# a detected drop-off maps straight onto a hypothesis record.
TRANSITION_LABELS = {
    ("home_collection", "product"): "Home/Collection → Product",
    ("product", "add_to_cart"): "Product → Add to cart",
    ("add_to_cart", "checkout_started"): "Add to cart → Checkout started",
    ("checkout_started", "purchase"): "Checkout started → Purchase",
}

GA4_EVENTS = [s.ga4_event for s in FUNNEL_STEPS]


def step_by_event(event_name):
    for s in FUNNEL_STEPS:
        if s.ga4_event == event_name:
            return s
    return None


def transition_label(from_key, to_key):
    return TRANSITION_LABELS.get((from_key, to_key), f"{from_key} → {to_key}")
