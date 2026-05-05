// brand-cdn — single Worker, multi-bucket
// Deployed at: https://brand-cdn.figandbloom.workers.dev
//
// Upload (auth):  POST   /upload/:bucket/:key+   Bearer ${UPLOAD_TOKEN}
// Read (public):  GET    /:bucket/:key+
// Health:         GET    /  or  /health
//
// To add a new brand:
//   1. Create the R2 bucket (Cloudflare → R2 → Create bucket)
//   2. Add the brand to the BUCKETS map below
//   3. Worker → Settings → Bindings → Add R2 bucket binding
//      with the variable name shown in BUCKETS
//   4. Deploy

const BUCKETS = {
  whoosh: 'WHOOSH_BUCKET',
  bower: 'BOWER_BUCKET',
  figandbloom: 'FIGANDBLOOM_BUCKET',
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/^\/+/, '');
    const segments = path.split('/').filter(Boolean);

    // Health check
    if (path === '' || path === 'health') {
      return new Response('ok\n', { status: 200 });
    }

    // Upload: POST /upload/:bucket/:key+
    if (request.method === 'POST' && segments[0] === 'upload') {
      const auth = request.headers.get('authorization') || '';
      const expected = `Bearer ${env.UPLOAD_TOKEN}`;
      if (!env.UPLOAD_TOKEN || auth !== expected) {
        return new Response('unauthorized\n', { status: 401 });
      }

      const bucketName = segments[1];
      const key = segments.slice(2).join('/');
      const bindingName = BUCKETS[bucketName];
      if (!bindingName || !key) {
        return new Response('bad request: POST /upload/:bucket/:key\n', { status: 400 });
      }
      const bucket = env[bindingName];
      if (!bucket) {
        return new Response(`bucket ${bucketName} not bound\n`, { status: 500 });
      }

      const contentType = request.headers.get('content-type') || 'application/octet-stream';
      await bucket.put(key, request.body, {
        httpMetadata: { contentType },
      });

      const publicUrl = `${url.origin}/${bucketName}/${key}`;
      return Response.json({ ok: true, url: publicUrl, bucket: bucketName, key });
    }

    // Read: GET /:bucket/:key+
    if (request.method === 'GET') {
      const bucketName = segments[0];
      const key = segments.slice(1).join('/');
      const bindingName = BUCKETS[bucketName];
      if (!bindingName || !key) {
        return new Response('not found\n', { status: 404 });
      }
      const bucket = env[bindingName];
      if (!bucket) {
        return new Response('bucket not bound\n', { status: 500 });
      }

      const obj = await bucket.get(key);
      if (!obj) {
        return new Response('not found\n', { status: 404 });
      }

      const headers = new Headers();
      obj.writeHttpMetadata(headers);
      headers.set('etag', obj.httpEtag);
      headers.set('cache-control', 'public, max-age=31536000, immutable');
      return new Response(obj.body, { headers });
    }

    return new Response('method not allowed\n', { status: 405 });
  },
};
