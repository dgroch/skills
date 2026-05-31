#!/usr/bin/env python3
"""
put_upload.py — push rendered tiles to Shopify's staged GCS targets.

This is the ONLY unauthenticated step in the upload flow: the signed PUT URL
already carries its credentials in the query string, so plain curl works and
there is nothing to copy by hand except the URL itself.

Flow (the other steps run through your Shopify Admin GraphQL access):
  1. stagedUploadsCreate(httpMethod: PUT)  → gives {url, resourceUrl} per file
  2. THIS SCRIPT: PUT each local PNG to its url
  3. fileCreate(originalSource: resourceUrl, contentType: IMAGE, alt: ...)
  4. poll the MediaImage nodes until fileStatus == READY → grab image.url

Input JSON = array of: { "local": "out/out_card-champagne.png",
                         "url": "<signed PUT url>",
                         "resourceUrl": "<resourceUrl>" }

Usage:  python3 put_upload.py put_targets.json
Prints OK/FAIL per file and echoes the resourceUrls (feed them to fileCreate).

ALWAYS use httpMethod: PUT for staging, not POST. POST returns ~9 long signed
form fields (policy + signature) you'd have to transcribe by hand; a single
corrupted base64 char => silent 400. PUT puts the signature in the URL, so the
only thing you copy is one string and curl does the rest.
"""
import json, subprocess, sys

if len(sys.argv) < 2:
    print("usage: python3 put_upload.py put_targets.json"); sys.exit(1)

targets = json.load(open(sys.argv[1]))
ok_urls = []
for t in targets:
    code = subprocess.run(
        ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-X', 'PUT',
         '-H', 'Content-Type: image/png', '--data-binary', '@' + t['local'], t['url']],
        capture_output=True, text=True).stdout.strip()
    ok = code in ('200', '201', '204')
    print(('OK  ' if ok else 'FAIL'), code, t['local'])
    if ok:
        ok_urls.append(t['resourceUrl'])

print('\nresourceUrls (pass to fileCreate):')
for u in ok_urls:
    print(u)
