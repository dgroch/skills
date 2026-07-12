/**
 * v5-engine: klaviyo.js
 *
 * Klaviyo API integration for uploading composed emails as campaign drafts.
 * Uses Klaviyo API v2024-10-15.
 */

const https = require('https');

const KLAVIYO_BASE = 'a.klaviyo.com';
const KLAVIYO_REVISION = '2024-10-15';

/**
 * Make an authenticated Klaviyo API request
 */
function klaviyoRequest(method, path, body = null) {
  return new Promise((resolve, reject) => {
    const apiKey = process.env.KLAVIYO_API_KEY;
    if (!apiKey) {
      reject(new Error('KLAVIYO_API_KEY not set in environment'));
      return;
    }

    const postData = body ? JSON.stringify(body) : null;

    const options = {
      hostname: KLAVIYO_BASE,
      path: `/api${path}`,
      method,
      headers: {
        'Authorization': `Klaviyo-API-Key ${apiKey}`,
        'revision': KLAVIYO_REVISION,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };

    if (postData) {
      options.headers['Content-Length'] = Buffer.byteLength(postData);
    }

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (res.statusCode >= 400) {
            const errMsg = parsed.errors?.map(e => `${e.detail} (${e.code})`).join('; ') || `HTTP ${res.statusCode}`;
            reject(new Error(errMsg));
          } else {
            resolve({ status: res.statusCode, data: parsed });
          }
        } catch (e) {
          reject(new Error(`Failed to parse response: ${data.substring(0, 200)}`));
        }
      });
    });

    req.on('error', reject);
    if (postData) req.write(postData);
    req.end();
  });
}

/**
 * Create a template with HTML content
 */
async function createTemplate(name, html) {
  const result = await klaviyoRequest('POST', '/templates/', {
    data: {
      type: 'template',
      attributes: {
        name: `v5-engine: ${name}`,
        html,
        editor_type: 'CODE'
      }
    }
  });

  return result.data?.data?.id;
}

/**
 * Create a campaign with an email message (no content yet)
 */
async function createCampaign(name, audienceId, messageAttrs) {
  const result = await klaviyoRequest('POST', '/campaigns/', {
    data: {
      type: 'campaign',
      attributes: {
        name,
        audiences: {
          included: [audienceId],
          excluded: []
        },
        'campaign-messages': {
          data: [{
            type: 'campaign-message',
            attributes: messageAttrs
          }]
        }
      }
    }
  });

  const campaign = result.data?.data;
  const messageId = campaign?.relationships?.['campaign-messages']?.data?.[0]?.id;

  return {
    campaignId: campaign?.id,
    messageId
  };
}

/**
 * Assign a template to a campaign message
 */
async function assignTemplate(messageId, templateId) {
  const result = await klaviyoRequest('POST', '/campaign-message-assign-template', {
    data: {
      type: 'campaign-message',
      id: messageId,
      relationships: {
        template: {
          data: {
            type: 'template',
            id: templateId
          }
        }
      }
    }
  });

  return result.data?.data?.relationships?.template?.data?.id;
}

/**
 * Delete a template (cleanup after Klaviyo clones it)
 */
async function deleteTemplate(templateId) {
  await klaviyoRequest('DELETE', `/templates/${templateId}/`);
}

/**
 * Create a campaign draft in Klaviyo
 *
 * Flow:
 * 1. Create template with HTML content
 * 2. Create campaign with email message attributes
 * 3. Assign template to message (Klaviyo clones it)
 * 4. Delete original template (cleanup)
 *
 * @param {object} opts
 * @param {string} opts.name - Campaign name
 * @param {string} opts.subject - Email subject line
 * @param {string} opts.previewText - Preview text
 * @param {string} opts.fromEmail - Sender email
 * @param {string} opts.fromName - Sender name
 * @param {string} opts.html - Full HTML content
 * @param {string} opts.audienceId - Klaviyo list/segment ID
 * @returns {Promise<{ campaignId: string, messageId: string, name: string, url: string }>}
 */
async function createCampaignDraft(opts) {
  const {
    name,
    subject,
    previewText = '',
    fromEmail = 'hello@figandbloom.com.au',
    fromName = 'Fig & Bloom',
    html,
    audienceId
  } = opts;

  if (!name) throw new Error('Campaign name is required');
  if (!subject) throw new Error('Subject line is required');
  if (!html) throw new Error('HTML content is required');
  if (!audienceId) throw new Error('Audience ID is required');

  console.log('  Creating template with HTML...');
  const templateId = await createTemplate(name, html);

  console.log('  Creating campaign with message...');
  const { campaignId, messageId } = await createCampaign(
    name,
    audienceId,
    {
      channel: 'email',
      content: {
        subject,
        preview_text: previewText,
        from_email: fromEmail,
        from_label: fromName
      }
    }
  );

  console.log('  Assigning template to message...');
  await assignTemplate(messageId, templateId);

  console.log('  Cleaning up original template...');
  await deleteTemplate(templateId);

  return {
    campaignId,
    messageId,
    name,
    status: 'draft',
    url: `https://www.klaviyo.com/campaigns/${campaignId}`
  };
}

/**
 * Verify a campaign exists and get its status
 */
async function verifyCampaign(campaignId) {
  const result = await klaviyoRequest('GET', `/campaigns/${campaignId}/`);
  const campaign = result.data?.data;

  return {
    id: campaign?.id,
    name: campaign?.attributes?.name,
    status: campaign?.attributes?.status,
    archived: campaign?.attributes?.archived || false
  };
}

/**
 * List recent email campaigns
 */
async function listCampaigns(limit = 5) {
  const encodedFilter = encodeURIComponent("equals(messages.channel,'email')");
  const result = await klaviyoRequest('GET', `/campaigns/?filter=${encodedFilter}&sort=-updated_at`);
  const campaigns = result.data?.data || [];

  return campaigns.slice(0, limit).map(c => ({
    id: c.id,
    name: c.attributes?.name,
    status: c.attributes?.status,
    updated: c.attributes?.['updated-at']
  }));
}

module.exports = { createCampaignDraft, verifyCampaign, listCampaigns, klaviyoRequest };
