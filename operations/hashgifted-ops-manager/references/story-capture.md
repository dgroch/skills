# Story Capture Boundary

Instagram story capture is the riskiest part of the Hashgifted lifecycle. Keep it separate from the main Hashgifted browser operator.

## Rule

Do not have the Hashgifted operator repair Instagram auth, solve 2FA, bypass checkpoints, or keep poking a decaying session. It should flag the problem clearly:

```text
IG story capture session expired; manual re-auth required.
```

## Preferred Service

Use a separate story-capture service with a persistent Instagram session.

Expected endpoint:

- `POST /download-story`
- Header: `Authorization: Bearer <ENDPOINT_API_KEY>`
- Body: `{ "url": "https://www.instagram.com/stories/...", "dest_filename": "2026-05-10-1430_handle_story_01.mp4" }`

Expected success:

```json
{
  "status": "ok",
  "file_path": "/var/lib/story-capture/downloads/file.mp4",
  "file_size": 1234567,
  "duration_seconds": 4.2
}
```

Expected auth failure:

```json
{
  "error": "ig_session_expired"
}
```

## Handling

- Story URL invalid, expired, or 404: flag immediately and do not silently skip.
- Endpoint returns 401: stop and request manual re-auth.
- Endpoint returns 5xx: retry once, then flag.
- Endpoint timeout over 60 seconds: flag; story may already be too late.
- Multiple stories from the same creator: capture all and sequence filenames.
- Highlight URL: capture as `highlight` rather than `story`.

## Downstream Flow

After download, use the same downstream flow as content capture:

1. Store in Drive under the campaign and creator folder.
2. Sync to brand CDN if Notion embed requires a stable public URL.
3. Embed or log in the creator's Notion page.
4. Append capture timestamp in AEST.

Filename pattern:

```text
{YYYY-MM-DD-HHMM}_{creator-handle}_story_{seq}.mp4
```
