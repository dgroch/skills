"""Shopify Admin API client.

Pulls the outcome truth: orders, AOV, and abandoned checkouts for a window.
Uses the GraphQL Admin API (the REST Admin API is being wound down) with a
custom-app Admin API access token.

Env:
    SHOPIFY_STORE         e.g. lechoixflowers.myshopify.com  (the *.myshopify.com handle)
    SHOPIFY_ADMIN_TOKEN   Admin API access token (shpat_...)
    SHOPIFY_API_VERSION   optional, defaults to a known-good version

The join key back to GA4: abandoned checkouts surface the *Checkout started ->
Purchase* bleed in dollar terms, which we line up against the GA4 funnel
transition of the same name (see funnel.py).
"""

import os

import requests

DEFAULT_API_VERSION = "2025-01"


class ShopifyError(RuntimeError):
    pass


class ShopifyClient:
    def __init__(self, store=None, token=None, api_version=None, timeout=30):
        self.store = (store or os.environ.get("SHOPIFY_STORE", "")).strip()
        self.token = token or os.environ.get("SHOPIFY_ADMIN_TOKEN")
        self.api_version = api_version or os.environ.get("SHOPIFY_API_VERSION", DEFAULT_API_VERSION)
        self.timeout = timeout
        if not self.store:
            raise ValueError("SHOPIFY_STORE is required (e.g. lechoixflowers.myshopify.com)")
        if not self.token:
            raise ValueError("SHOPIFY_ADMIN_TOKEN is required")
        if not self.store.endswith("myshopify.com"):
            # Accept a bare handle too.
            self.store = f"{self.store}.myshopify.com"
        self._endpoint = f"https://{self.store}/admin/api/{self.api_version}/graphql.json"

    def _graphql(self, query, variables=None):
        resp = requests.post(
            self._endpoint,
            json={"query": query, "variables": variables or {}},
            headers={
                "X-Shopify-Access-Token": self.token,
                "Content-Type": "application/json",
            },
            timeout=self.timeout,
        )
        if resp.status_code != 200:
            raise ShopifyError(f"Shopify HTTP {resp.status_code}: {resp.text[:500]}")
        payload = resp.json()
        if payload.get("errors"):
            raise ShopifyError(f"Shopify GraphQL errors: {payload['errors']}")
        return payload["data"]

    # ------------------------------------------------------------------ #
    # Orders + AOV
    # ------------------------------------------------------------------ #
    def orders_summary(self, start_date, end_date):
        """Aggregate orders for [start_date, end_date] (YYYY-MM-DD, inclusive).

        Returns {orders, gross_revenue, aov, currency}. Paginates fully.
        """
        query = """
        query Orders($q: String!, $cursor: String) {
          orders(first: 250, query: $q, after: $cursor) {
            edges {
              cursor
              node {
                currentTotalPriceSet { shopMoney { amount currencyCode } }
              }
            }
            pageInfo { hasNextPage endCursor }
          }
        }
        """
        q = f"created_at:>={start_date} created_at:<={end_date} test:false"
        count = 0
        total = 0.0
        currency = None
        cursor = None
        while True:
            data = self._graphql(query, {"q": q, "cursor": cursor})
            block = data["orders"]
            for edge in block["edges"]:
                money = edge["node"]["currentTotalPriceSet"]["shopMoney"]
                total += float(money["amount"])
                currency = currency or money["currencyCode"]
                count += 1
            if block["pageInfo"]["hasNextPage"]:
                cursor = block["pageInfo"]["endCursor"]
            else:
                break
        aov = (total / count) if count else 0.0
        return {
            "orders": count,
            "gross_revenue": round(total, 2),
            "aov": round(aov, 2),
            "currency": currency or "AUD",
        }

    # ------------------------------------------------------------------ #
    # Abandoned checkouts
    # ------------------------------------------------------------------ #
    def abandoned_checkouts(self, start_date, end_date):
        """Abandoned checkouts for the window.

        Returns {count, lost_value, currency, samples:[...]} where lost_value is
        the summed total of carts that started checkout but never converted —
        the dollar size of the Checkout-started -> Purchase bleed.
        """
        query = """
        query Abandoned($q: String!, $cursor: String) {
          abandonedCheckouts(first: 100, query: $q, after: $cursor) {
            edges {
              node {
                totalPriceSet { shopMoney { amount currencyCode } }
                createdAt
              }
            }
            pageInfo { hasNextPage endCursor }
          }
        }
        """
        q = f"created_at:>={start_date} created_at:<={end_date}"
        count = 0
        lost = 0.0
        currency = None
        cursor = None
        samples = []
        while True:
            data = self._graphql(query, {"q": q, "cursor": cursor})
            block = data["abandonedCheckouts"]
            for edge in block["edges"]:
                money = edge["node"]["totalPriceSet"]["shopMoney"]
                amount = float(money["amount"])
                lost += amount
                currency = currency or money["currencyCode"]
                count += 1
                if len(samples) < 5:
                    samples.append({"amount": amount, "createdAt": edge["node"]["createdAt"]})
            if block["pageInfo"]["hasNextPage"]:
                cursor = block["pageInfo"]["endCursor"]
            else:
                break
        return {
            "count": count,
            "lost_value": round(lost, 2),
            "currency": currency or "AUD",
            "samples": samples,
        }

    def shop_info(self):
        data = self._graphql("query { shop { name currencyCode myshopifyDomain } }")
        return data["shop"]
