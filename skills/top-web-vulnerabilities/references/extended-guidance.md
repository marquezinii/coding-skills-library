<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## Quick Reference

### Vulnerability Categories Summary

| Category | Vulnerability Numbers | Key Controls |
|----------|----------------------|--------------|
| Injection | 1-13 | Parameterized queries, input validation, output encoding |
| Authentication | 14-23, 85-86 | MFA, session management, account lockout |
| Data Exposure | 24-27 | Encryption at rest/transit, access controls, DLP |
| Misconfiguration | 28-36 | Secure defaults, hardening, patching |
| XML | 37-39, 65 | Disable external entities, limit expansion |
| Access Control | 40-44 | RBAC, least privilege, authorization checks |
| Deserialization | 45-47 | Avoid untrusted data, integrity validation |
| API Security | 48-51, 75 | OAuth, rate limiting, input validation |
| Communication | 52-55 | TLS 1.2+, certificate validation, HTTPS |
| Client-Side | 56-60 | CSP, X-Frame-Options, safe DOM |
| DoS | 61-65 | Rate limiting, DDoS protection, resource limits |
| SSRF | 66, 87-88 | URL whitelisting, egress filtering |
| Mobile/IoT | 76-84 | Encryption, authentication, secure storage |
| Business Logic | 74, 92-97 | Threat modeling, logic testing |
| Zero-Day | 98-100 | Defense in depth, threat intelligence |

### Critical Security Headers

```
Content-Security-Policy: default-src 'self'; script-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=()
```

### OWASP Top 10 Mapping

| OWASP 2021 | Related Vulnerabilities |
|------------|------------------------|
| A01: Broken Access Control | 40-44, 23, 74 |
| A02: Cryptographic Failures | 24-25, 53-55 |
| A03: Injection | 1-13, 37-39 |
| A04: Insecure Design | 74, 92-97 |
| A05: Security Misconfiguration | 26-36 |
| A06: Vulnerable Components | 34, 98-100 |
| A07: Auth Failures | 14-23, 85-86 |
| A08: Data Integrity | 45-47 |
| A09: Logging Failures | 73 |
| A10: SSRF | 66, 87-88 |

---

## Constraints and Limitations

- Vulnerability definitions represent common patterns; specific implementations vary
- Mitigations must be adapted to technology stack and architecture
- New vulnerabilities emerge continuously; reference should be updated
- Some vulnerabilities overlap across categories (e.g., IDOR appears in multiple contexts)
- Effectiveness of mitigations depends on proper implementation
- Automated scanners cannot detect all vulnerability types (especially business logic)

---

## Troubleshooting

### Common Assessment Challenges

| Challenge | Solution |
|-----------|----------|
| False positives in scanning | Manual verification, contextual analysis |
| Business logic flaws missed | Manual testing, threat modeling, abuse case analysis |
| Encrypted traffic analysis | Proxy configuration, certificate installation |
| WAF blocking tests | Rate adjustment, IP rotation, payload encoding |
| Session handling issues | Cookie management, authentication state tracking |
| API discovery | Swagger/OpenAPI enumeration, traffic analysis |

### Vulnerability Verification Techniques

| Vulnerability Type | Verification Approach |
|-------------------|----------------------|
| Injection | Payload testing with encoded variants |
| XSS | Alert boxes, cookie access, DOM inspection |
| CSRF | Cross-origin form submission testing |
| SSRF | Out-of-band DNS/HTTP callbacks |
| XXE | External entity with controlled server |
| Access Control | Horizontal/vertical privilege testing |
| Authentication | Credential rotation, session analysis |

---

## References

- OWASP Top 10 Web Application Security Risks
- CWE/SANS Top 25 Most Dangerous Software Errors
- OWASP Testing Guide
- OWASP Application Security Verification Standard (ASVS)
- NIST Cybersecurity Framework
- Source: Kumar MS - Top 100 Web Vulnerabilities

## When to Use
This skill is applicable to execute the workflow or actions described in the overview.
