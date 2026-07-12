---
name: telegram-file-attachment
description: How to attach files to Telegram messages from Hermes. Use when users ask for files, documents, or exports to be sent.
tags: [telegram, file-upload, messaging]
---

# Telegram File Attachment

## How to send files to the user on Telegram

**Include `MEDIA:/absolute/path/to/file` directly in your response text.**

That's it. The gateway converts it to a native Telegram file attachment.

```
MEDIA:/tmp/report.pdf
MEDIA:/opt/data/workspace/file.md
MEDIA:/tmp/image.png
```

## Common mistakes (don't do these)

- `send_message` tool with MEDIA in the body → sends as text, not attachment
- Writing MEDIA path inside a code block → rendered as text
- Using `hermes send -f` → sends file body as message text, not as attachment
- Trying to use Telegram API directly → unnecessary, the gateway handles it

## Supported formats

Images (.png, .jpg, .webp) appear as photos. Audio (.ogg) sends as voice. Video (.mp4) plays inline. Everything else sends as a document attachment.
