---
name: best-practices
description: Apply modern web development best practices for security, compatibility, and code quality. Use when asked to "apply best practices", "security audit", "modernize code", "code quality review", or "check for vulnerabilities".
license: MIT
metadata:
  author: web-quality-skills
  version: "1.0"
---

# Best practices

Modern web development standards based on Lighthouse best practices audits. Covers security, browser compatibility, and code quality patterns.

## Security

### HTTPS everywhere

**Enforce HTTPS:**
```html
<!-- ❌ Mixed content -->
<img src="http://example.com/image.jpg">
<script src="http://cdn.example.com/script.js"></script>

<!-- ✅ HTTPS only -->
<img src="https://example.com/image.jpg">
<script src="https://cdn.example.com/script.js"></script>
```

Avoid protocol-relative URLs (`//example.com/...`) — they're an HTTP-era pattern with no benefit on HTTPS-only sites and hide the actual scheme from reviewers.

**HSTS Header:**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

### Content Security Policy (CSP)

```html
<!-- Basic CSP via meta tag -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' https://trusted-cdn.com; 
               style-src 'self' 'unsafe-inline';
               img-src 'self' data: https:;
               connect-src 'self' https://api.example.com;">

<!-- Better: HTTP header -->
```

**CSP Header (recommended):**
```
Content-Security-Policy: 
  default-src 'self';
  script-src 'self' 'nonce-abc123' https://trusted.com;
  style-src 'self' 'nonce-abc123';
  img-src 'self' data: https:;
  connect-src 'self' https://api.example.com;
  frame-ancestors 'self';
  base-uri 'self';
  form-action 'self';
```

**Using nonces for inline scripts:**
```html
<script nonce="abc123">
  // This inline script is allowed
</script>
```

### Trusted Types (modern DOM-XSS defense)

A strict CSP blocks loading untrusted *script files*, but it doesn't stop a string from reaching `innerHTML`, `eval`, or other DOM-XSS sinks. Trusted Types — Baseline across all major browsers since early 2026 — closes that hole by making sinks reject raw strings and accept only typed objects produced by a named policy.

```
Content-Security-Policy: require-trusted-types-for 'script'; trusted-types default;
```

```javascript
// One central policy that does the sanitization
const escape = trustedTypes.createPolicy('default', {
  createHTML: (s) => DOMPurify.sanitize(s, { RETURN_TRUSTED_TYPE: true })
});

// ❌ This now throws TypeError under enforcement
element.innerHTML = userInput;

// ✅ Goes through the policy
element.innerHTML = escape.createHTML(userInput);
```

Roll out with `Content-Security-Policy-Report-Only` first to find every sink usage in your app, then flip to enforcement. Angular has built-in Trusted Types support; React 19+ produces TrustedHTML when Trusted Types are enforced; for everything else, [DOMPurify](https://github.com/cure53/DOMPurify) is the de-facto sanitizer.

### Subresource Integrity (SRI) for third-party scripts

Pin every `<script>` and `<link rel="stylesheet">` you load from a CDN you don't control. If the CDN is compromised — as happened to polyfill.io in 2024 — the browser refuses to execute a file whose hash doesn't match.

```html
<script src="https://cdn.example.com/lib@1.2.3/dist/lib.js"
        integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
        crossorigin="anonymous"></script>
```

`integrity` accepts space-separated hashes; include the next version's hash before rotating to avoid downtime. Generate with `openssl dgst -sha384 -binary file.js | openssl base64 -A`. SRI requires `crossorigin` and an `Access-Control-Allow-Origin` response header from the CDN.

### Security headers

```
# Prevent clickjacking — prefer CSP `frame-ancestors` (above); X-Frame-Options
# is the legacy fallback for older browsers.
X-Frame-Options: DENY

# Prevent MIME type sniffing
X-Content-Type-Options: nosniff

# Do NOT send X-XSS-Protection. The legacy browser XSS auditor was deprecated
# and removed (Chrome 78, Edge 17), and in some cases it introduced its own
# vulnerabilities. Use a strict CSP + Trusted Types (below) instead.

# Control referrer information
Referrer-Policy: strict-origin-when-cross-origin

# Permissions policy (formerly Feature-Policy)
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### No vulnerable libraries

```bash
# Check for vulnerabilities
npm audit
yarn audit

# Auto-fix when possible
npm audit fix

# Check specific package
npm ls lodash
```

**Keep dependencies updated:**
```json
// package.json
{
  "scripts": {
    "audit": "npm audit --audit-level=moderate",
    "update": "npm update && npm audit fix"
  }
}
```

**Known vulnerable patterns to avoid:**
```javascript
// ❌ Recursive merges of untrusted input can pollute Object.prototype
//    via __proto__, constructor, or prototype keys.
_.merge(target, userInput);          // lodash <4.17.20
$.extend(true, {}, target, userInput); // jQuery deep extend
Object.assign(target, ...userInputs); // safe by itself (shallow), but unsafe
                                      // when target IS Object.prototype-derived
                                      // and userInput contains __proto__

// ✅ For untrusted bags, use a null-prototype object so __proto__ is just a key
const safe = Object.create(null);
Object.assign(safe, userInput); // shallow, no recursion → safe by construction

// ✅ For deep copies, structuredClone drops __proto__ and functions
const deepSafe = structuredClone(userInput);

// ✅ For deep merges, use a library that explicitly blocks dangerous keys
//    (e.g. lodash ≥4.17.21 _.mergeWith with a customizer, or deepmerge-ts).
```

### Input sanitization

```javascript
// ❌ XSS vulnerable
element.innerHTML = userInput;
document.write(userInput);

// ✅ Safe text content
element.textContent = userInput;

// ✅ If HTML needed, sanitize
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);
```

### Secure cookies

```javascript
// ❌ Insecure cookie
document.cookie = "session=abc123";

// ✅ Secure cookie (server-side)
Set-Cookie: session=abc123; Secure; HttpOnly; SameSite=Strict; Path=/
```

---

## Browser compatibility

### Doctype declaration

```html
<!-- ❌ Missing or invalid doctype -->
<HTML>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">

<!-- ✅ HTML5 doctype -->
<!DOCTYPE html>
<html lang="en">
```

### Character encoding

```html
<!-- ❌ Missing or late charset -->
<html>
<head>
  <title>Page</title>
  <meta charset="UTF-8">
</head>

<!-- ✅ Charset as first element in head -->
<html>
<head>
  <meta charset="UTF-8">
  <title>Page</title>
</head>
```

### Viewport meta tag

```html
<!-- ❌ Missing viewport -->
<head>
  <title>Page</title>
</head>

<!-- ✅ Responsive viewport -->
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Page</title>
</head>
```

### Feature detection

```javascript
// ❌ Browser detection (brittle)
if (navigator.userAgent.includes('Chrome')) {
  // Chrome-specific code
}

// ✅ Feature detection
if ('IntersectionObserver' in window) {
  // Use IntersectionObserver
} else {
  // Fallback
}

// ✅ Using @supports in CSS
@supports (display: grid) {
  .container {
    display: grid;
  }
}

@supports not (display: grid) {
  .container {
    display: flex;
  }
}
```

### Polyfills (when needed)

Prefer **bundling polyfills at build time** (Babel/SWC + `core-js`, or `@vitejs/plugin-legacy`) targeted by your supported-browsers list. This eliminates the runtime check entirely and avoids shipping polyfill bytes to modern browsers.

If you must load a polyfill at runtime, append a script element — never use `document.write` (it blocks the parser and is broken in async/deferred contexts):

```html
<script>
  if (!('fetch' in window)) {
    const s = document.createElement('script');
    s.src = '/polyfills/fetch.js';
    s.defer = true;
    document.head.appendChild(s);
  }
</script>
```

**Never load polyfills from a third-party CDN you don't control.** The `polyfill.io` service was [compromised in mid-2024](https://sansec.io/research/polyfill-supply-chain-attack) in a supply-chain attack and used to serve malware to ~100k sites. Self-host, or use a vetted mirror (e.g. [Cloudflare's `cdnjs` polyfill build](https://blog.cloudflare.com/polyfill-io-now-available-on-cdnjs-reduce-your-supply-chain-risk/)) — and pin the version with [Subresource Integrity](#subresource-integrity-sri-for-third-party-scripts).

---

## Deprecated APIs

### Avoid these

```javascript
// ❌ document.write (blocks parsing)
document.write('<script src="..."></script>');

// ✅ Dynamic script loading
const script = document.createElement('script');
script.src = '...';
document.head.appendChild(script);

// ❌ Synchronous XHR (blocks main thread)
const xhr = new XMLHttpRequest();
xhr.open('GET', url, false); // false = synchronous

// ✅ Async fetch
const response = await fetch(url);

// ❌ Application Cache (deprecated)
<html manifest="cache.manifest">

// ✅ Service Workers
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
```

### Event listener passive

```javascript
// ❌ Non-passive touch/wheel (may block scrolling)
element.addEventListener('touchstart', handler);
element.addEventListener('wheel', handler);

// ✅ Passive listeners (allows smooth scrolling)
element.addEventListener('touchstart', handler, { passive: true });
element.addEventListener('wheel', handler, { passive: true });

// ✅ If you need preventDefault, be explicit
element.addEventListener('touchstart', handler, { passive: false });
```

---


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [Console & errors](references/extended-guidance.md#console-errors)
- [Source maps](references/extended-guidance.md#source-maps)
- [Performance best practices](references/extended-guidance.md#performance-best-practices)
- [Code quality](references/extended-guidance.md#code-quality)
- [Permissions & privacy](references/extended-guidance.md#permissions-privacy)
- [Audit checklist](references/extended-guidance.md#audit-checklist)
- [Tools](references/extended-guidance.md#tools)
- [References](references/extended-guidance.md#references)

