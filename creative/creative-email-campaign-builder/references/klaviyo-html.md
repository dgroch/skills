# Klaviyo HTML Conversion — Fig & Bloom

## Overview

Converting the approved design mockup (modern CSS) into Klaviyo-compatible email HTML. Email clients have limited CSS support — this reference covers the translation.

## Key Constraints

1. **Table-based layout** — use `<table>`, `<tr>`, `<td>` instead of flexbox/grid
2. **Inline styles** — all styles must be inline (no `<style>` block for layout; `<style>` in `<head>` only for web fonts and media queries)
3. **Max width 600px** — standard email width
4. **No JavaScript** — none
5. **Background images** — use VML fallback for Outlook
6. **Web fonts** — load via `<link>` in `<head>`, with robust fallback stacks

## Template Structure

```html
<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ email_subject }}</title>
  
  <!-- Web fonts (renders in Apple Mail, iOS, Android, some webmail) -->
  <!-- Lust and Cervanttis must be hosted — use Klaviyo CDN or self-host -->
  
  <style>
    /* Reset */
    body, table, td { margin:0; padding:0; }
    img { border:0; display:block; }
    
    /* Responsive */
    @media screen and (max-width: 600px) {
      .email-container { width:100% !important; }
      .stack-column { display:block !important; width:100% !important; }
      .stack-column-center { text-align:center !important; }
      .hero-text { font-size:36px !important; }
    }
  </style>
</head>
<body style="margin:0;padding:0;background-color:#D8CCBE;font-family:'NeuzeitGro','Gill Sans','Helvetica Neue',sans-serif;font-weight:300">

  <!-- Preheader (hidden) -->
  <div style="display:none;font-size:1px;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden">
    {{ preheader_text }}
  </div>

  <!-- Email wrapper -->
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#D8CCBE">
    <tr>
      <td align="center" style="padding:0">
        <table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="background-color:#FFFFFF;max-width:600px;width:100%">
          
          <!-- SECTIONS GO HERE -->
          
        </table>
      </td>
    </tr>
  </table>

</body>
</html>
```

## Section Conversion Patterns

### Full-width image
```html
<tr>
  <td style="border-top:1px solid #e8e2da">
    <img src="{IMAGE_URL}" width="600" style="width:100%;height:auto;display:block" alt="{ALT}">
  </td>
</tr>
```

### Two-column product grid
```html
<tr>
  <td style="border-top:1px solid #e8e2da">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td class="stack-column" width="50%" valign="top" style="border-right:1px solid #e8e2da">
          <img src="{IMG_1}" width="300" style="width:100%;display:block" alt="">
          <div style="padding:16px;text-align:center">
            <!-- product info -->
          </div>
        </td>
        <td class="stack-column" width="50%" valign="top">
          <img src="{IMG_2}" width="300" style="width:100%;display:block" alt="">
          <div style="padding:16px;text-align:center">
            <!-- product info -->
          </div>
        </td>
      </tr>
    </table>
  </td>
</tr>
```

### Hero with text overlay
For the hero with text overlaid on an image, use a background image on a `<td>` with VML fallback for Outlook:

```html
<tr>
  <td background="{HERO_IMAGE_URL}" bgcolor="#c8b8a4" width="600" height="450" valign="middle" style="background-image:url({HERO_IMAGE_URL});background-size:cover;background-position:center;text-align:center">
    <!--[if gte mso 9]>
    <v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false" style="width:600px;height:450px;">
    <v:fill type="tile" src="{HERO_IMAGE_URL}" />
    <v:textbox inset="0,0,0,0">
    <![endif]-->
    <div style="background:rgba(0,0,0,.30);padding:40px">
      <!-- hero text content -->
    </div>
    <!--[if gte mso 9]>
    </v:textbox></v:rect>
    <![endif]-->
  </td>
</tr>
```

## Klaviyo Template Tags

| Tag | Purpose |
|---|---|
| `{{ first_name\|default:'Moment Maker' }}` | Personalised greeting |
| `{{ email }}` | Recipient email |
| `{% unsubscribe %}` | Unsubscribe link (required) |
| `{% manage_preferences %}` | Email preferences |
| `{{ view_in_browser_url }}` | View in browser fallback |
| `{% if ... %}` / `{% endif %}` | Conditional content |

## Image Hosting

- **Product images:** Use Shopify CDN URLs directly: `figandbloom.com/cdn/shop/files/{filename}`
- **Campaign-specific images** (hero, lifestyle): Upload to Klaviyo media library or Shopify Files, use the hosted URL
- **Illustrations:** Upload to Klaviyo media library as PNGs, reference by URL
- **Logo:** Shopify CDN: `cdn.shopify.com/s/files/1/0657/8723/2489/files/F_B_Logo_Horizontal_BLK_914x200_0eb09d11-e91b-4f05-8ef4-9e54a99cb903.png?v=1776028453`

## Testing Checklist

Before deploying to Klaviyo:
- [ ] Renders in Apple Mail, Gmail (web + app), Outlook 365
- [ ] Responsive at 375px (mobile), 600px (desktop)
- [ ] All images have alt text
- [ ] All links point to correct Shopify URLs
- [ ] Klaviyo template tags render correctly in preview
- [ ] Unsubscribe link works
- [ ] Preheader text is set and hidden
- [ ] Font fallbacks display acceptably when web fonts don't load
