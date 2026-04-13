#!/usr/bin/env python3
"""
Lightweight Deputy API client using only Python stdlib (no requests dependency).
Usage:
  python deputy_api_client.py <subdomain> <token> <endpoint> [--method METHOD] [--params JSON] [--data JSON] [--all-pages]
Example:
  python deputy_api_client.py 18b41717033219.au.deputy.com "$DEPUTY_TOKEN" resource/Employee --all-pages
"""
import sys
import json
import urllib.parse
import urllib.request
import argparse

API_BASE = 'https://{subdomain}/api'


def call_api(subdomain, token, path, method='GET', params=None, data=None):
    base = API_BASE.format(subdomain=subdomain.rstrip('/'))
    url = urllib.parse.urljoin(base + '/', path.lstrip('/'))
    if params:
        qp = urllib.parse.urlencode(params, doseq=True)
        url = url + ('&' if '?' in url else '?') + qp

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'User-Agent': 'deputy-connector/1.0'
    }

    if data is not None:
        body = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    else:
        body = None

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        charset = resp.headers.get_content_charset() or 'utf-8'
        text = resp.read().decode(charset)
        if not text:
            return None
        return json.loads(text)


def iter_all_pages(subdomain, token, path):
    # Deputy resource endpoints often return list-style JSON. If they page via 'next' links,
    # follow a Next or use offset/limit; for simplicity, if response is a list return it.
    # If response includes paging wrapper, try common fields.
    r = call_api(subdomain, token, path)
    if isinstance(r, list):
        return r
    # common wrapper patterns
    if isinstance(r, dict):
        # look for 'data' or 'Items' or similar
        for key in ('data', 'Items', 'results', 'Results'):
            if key in r and isinstance(r[key], list):
                return r[key]
    # fallback: return the raw response in a single-element list
    return [r]


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument('subdomain')
    p.add_argument('token')
    p.add_argument('endpoint')
    p.add_argument('--method', default='GET')
    p.add_argument('--params', help='JSON object of query params', default=None)
    p.add_argument('--data', help='JSON object of request body', default=None)
    p.add_argument('--all-pages', action='store_true')
    args = p.parse_args(argv)

    params = json.loads(args.params) if args.params else None
    data = json.loads(args.data) if args.data else None

    try:
        if args.all_pages:
            result = iter_all_pages(args.subdomain, args.token, args.endpoint)
        else:
            result = call_api(args.subdomain, args.token, args.endpoint, method=args.method.upper(), params=params, data=data)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')
        print(f"HTTP {e.code}: {e.reason}", file=sys.stderr)
        try:
            print(json.dumps(json.loads(body), indent=2))
        except Exception:
            print(body)
        sys.exit(1)
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main(sys.argv[1:])
