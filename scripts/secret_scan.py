#!/usr/bin/env python3
"""
secret_scan.py - Secret detection for skills library

Scans for common secret patterns that would trigger GitHub Push Protection.
"""

import re
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "skills"

# Patterns that would trigger secret scanners
# These are regex patterns for REAL secret formats (not placeholders)
# NOTE: Avoid overly broad patterns like generic base64 that match URLs
# NOTE: Patterns should match HARDCODED secrets, not env var references
PATTERNS = [
    # GitHub tokens (specific prefixes)
    (r'ghp_[A-Za-z0-9]{36,}', 'GitHub Personal Access Token'),
    (r'gho_[A-Za-z0-9]{36,}', 'GitHub OAuth Token'),
    (r'ghu_[A-Za-z0-9]{36,}', 'GitHub User Token'),
    (r'ghs_[A-Za-z0-9]{36,}', 'GitHub Server Token'),
    (r'ghr_[A-Za-z0-9]{36,}', 'GitHub Refresh Token'),
    
    # AWS (specific formats)
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID'),
    # AWS Secret: 40 chars, specific charset - more restrictive
    (r'(?i)aws[_-]?secret[_-]?access[_-]?key["\s:=]+[A-Za-z0-9/+=]{40}', 'AWS Secret Access Key'),
    
    # Google / Firebase
    (r'AIza[A-Za-z0-9_-]{35}', 'Google API Key'),
    
    # Stripe (specific prefixes)
    (r'sk_live_[A-Za-z0-9]{24,}', 'Stripe Live Secret Key'),
    (r'sk_test_[A-Za-z0-9]{24,}', 'Stripe Test Secret Key'),
    (r'pk_live_[A-Za-z0-9]{24,}', 'Stripe Live Publishable Key'),
    (r'pk_test_[A-Za-z0-9]{24,}', 'Stripe Test Publishable Key'),
    
    # Slack (specific prefixes)
    (r'xoxb-[0-9]{11,}-[0-9]{11,}-[A-Za-z0-9]{24}', 'Slack Bot Token'),
    (r'xoxp-[0-9]{11,}-[0-9]{11,}-[0-9]{11,}-[A-Za-z0-9]{24}', 'Slack User Token'),
    (r'xoxa-[0-9]{11,}-[0-9]{11,}-[0-9]{11,}-[A-Za-z0-9]{24}', 'Slack App Token'),
    
    # Generic patterns
    (r'Bearer [A-Za-z0-9._-]{20,}', 'Bearer Token'),
    (r'eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}', 'JWT Token'),
    (r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----', 'Private Key'),
    (r'-----BEGIN (PGP )?PRIVATE KEY BLOCK-----', 'PGP Private Key'),
    
    # Sentry (sntrys_ prefix)
    (r'sntrys_[A-Za-z0-9]{32,}', 'Sentry Auth Token'),
    
    # Generic API key patterns - match HARDCODED values (not process.env, os.environ, etc.)
    # Look for actual secret values assigned directly, not via env var
    (r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)["\s:=]+(?![a-zA-Z_$][a-zA-Z0-9_$]*\(?\s*(?:process\.env|os\.environ|Environment\.GetEnvironmentVariable|getenv|config\.requireSecret|builder\.AddParameter|vault|secret[_-]?manager))[A-Za-z0-9._-]{20,}', 'Hardcoded API Key/Secret'),
]

# Placeholders that are OK (should NOT trigger)
ALLOWED_PLACEHOLDERS = [
    '<YOUR_',
    '<AWS_',
    '<GOOGLE_',
    '<STRIPE_',
    '<GITHUB_',
    '<SLACK_',
    '<SENTRY_',
    '<API_KEY>',
    '<SECRET>',
    '<TOKEN>',
    '<PRIVATE_KEY>',
    'YOUR_',
    'REDACTED',
    'EXAMPLE',
    'PLACEHOLDER',
    'xxxxxxxx',
    'AKIAIOSFODNN7EXAMPLE',
    'wJalrXUtnFEMI/K7MDENG',
    'sk_test_20cbqx6v2hpftsbq203r36yqccazez',  # Known fake Stripe test key
    'AKIAxxxxxxxxxxxxxxxx',  # Masked AWS key
]


def is_allowed(match_text: str) -> bool:
    """Check if a match is an allowed placeholder."""
    for placeholder in ALLOWED_PLACEHOLDERS:
        if placeholder in match_text:
            return True
    return False


# Broad patterns to find potential secrets
BROAD_PATTERNS = [
    # GitHub tokens
    (r'ghp_[A-Za-z0-9]{36,}', 'GitHub Personal Access Token'),
    (r'gho_[A-Za-z0-9]{36,}', 'GitHub OAuth Token'),
    (r'ghu_[A-Za-z0-9]{36,}', 'GitHub User Token'),
    (r'ghs_[A-Za-z0-9]{36,}', 'GitHub Server Token'),
    (r'ghr_[A-Za-z0-9]{36,}', 'GitHub Refresh Token'),
    
    # AWS
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID'),
    (r'(?i)aws[_-]?secret[_-]?access[_-]?key["\s:=]+[A-Za-z0-9/+=]{40}', 'AWS Secret Access Key'),
    
    # Google / Firebase
    (r'AIza[A-Za-z0-9_-]{35}', 'Google API Key'),
    
    # Stripe
    (r'sk_live_[A-Za-z0-9]{24,}', 'Stripe Live Secret Key'),
    (r'sk_test_[A-Za-z0-9]{24,}', 'Stripe Test Secret Key'),
    (r'pk_live_[A-Za-z0-9]{24,}', 'Stripe Live Publishable Key'),
    (r'pk_test_[A-Za-z0-9]{24,}', 'Stripe Test Publishable Key'),
    
    # Slack
    (r'xoxb-[0-9]{11,}-[0-9]{11,}-[A-Za-z0-9]{24}', 'Slack Bot Token'),
    (r'xoxp-[0-9]{11,}-[0-9]{11,}-[0-9]{11,}-[A-Za-z0-9]{24}', 'Slack User Token'),
    (r'xoxa-[0-9]{11,}-[0-9]{11,}-[0-9]{11,}-[A-Za-z0-9]{24}', 'Slack App Token'),
    
    # Generic
    (r'Bearer [A-Za-z0-9._-]{20,}', 'Bearer Token'),
    (r'eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}', 'JWT Token'),
    (r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----', 'Private Key'),
    (r'-----BEGIN (PGP )?PRIVATE KEY BLOCK-----', 'PGP Private Key'),
    
    # Sentry
    (r'sntrys_[A-Za-z0-9]{32,}', 'Sentry Auth Token'),
    
    # Generic API keys - broad match, filtered later
    (r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)["\s:=]+[A-Za-z0-9._-]{20,}', 'Potential Hardcoded Secret'),
]

# Safe patterns that indicate proper secret handling (env vars, vaults, etc.)
# If a match contains any of these, it's likely NOT a hardcoded secret
SAFE_INDICATORS = [
    'process.env',
    'os.environ',
    'os.getenv',
    'Environment.GetEnvironmentVariable',
    'getenv(',
    'config.requireSecret',
    'builder.AddParameter',
    'vault',
    'secret_manager',
    'keyvault',
    'secretsmanager',
    'parameterstore',
    'dotenv',
    'rails.application.credentials',
    'credential.',
    '${',
    'env.',
    'environ[',
    # Token generation / response handling (not hardcoded secrets)
    'jwtservice.generate',
    'jwtservice.sign',
    'generateToken',
    'signToken',
    'createToken',
    'response.access_token',
    'response.token',
    'access_token:',
    'token:',
    # Placeholder patterns
    'your-secret',
    'your-key',
    'your-token',
    'your-api',
    'example',
    'placeholder',
    'xxxxxxxx',
    'AKIAIOSFODNN7EXAMPLE',
    'sk_test_20cbqx6v2hpftsbq203r36yqccazez',
    'AKIAxxxxxxxxxxxxxxxx',
    'AIzaXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    'AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q',
    # Encrypted / base64 examples
    'encrypted...base64',
    '...encrypted...',
    # Private key templates (in examples)
    '-----BEGIN PRIVATE KEY-----',
    '-----BEGIN OPENSSH PRIVATE KEY-----',
    '-----BEGIN RSA PRIVATE KEY-----',
]


def is_likely_safe(match_text: str, context_line: str) -> bool:
    """Check if a match is likely a safe pattern (env var, vault, etc.)."""
    combined = (match_text + ' ' + context_line).lower()
    for indicator in SAFE_INDICATORS:
        if indicator.lower() in combined:
            return True
    # Also check for placeholder patterns
    if any(ph in match_text for ph in ['<YOUR_', '<AWS_', '<GOOGLE_', '<STRIPE_', '<GITHUB_', 
                                        '<SLACK_', '<SENTRY_', '<API_KEY>', '<SECRET>', 
                                        '<TOKEN>', '<PRIVATE_KEY>', 'YOUR_', 'REDACTED', 
                                        'EXAMPLE', 'PLACEHOLDER', 'xxxxxxxx', 
                                        'AKIAIOSFODNN7EXAMPLE', 'sk_test_20cbqx6v2hpftsbq203r36yqccazez',
                                        'AKIAxxxxxxxxxxxxxxxx', 'AIzaXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
                                        'AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q',
                                        'encrypted...base64', '...encrypted...',
                                        '-----BEGIN PRIVATE KEY-----',
                                        '-----BEGIN OPENSSH PRIVATE KEY-----',
                                        '-----BEGIN RSA PRIVATE KEY-----']):
        return True
    return False


def scan_file(file_path: Path) -> list:
    """Scan a single file for secrets. Returns list of (pattern_name, match, line_num)."""
    findings = []
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return findings  # Skip binary files
    except Exception:
        return findings
    
    lines = content.split('\n')
    
    for pattern_regex, pattern_name in BROAD_PATTERNS:
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(pattern_regex, line)
            for match in matches:
                match_text = match.group(0)
                if not is_allowed(match_text) and not is_likely_safe(match_text, line):
                    findings.append((pattern_name, match_text, line_num, line.strip()[:100]))
    
    return findings


def safe_print(text: str):
    """Print text safely, replacing non-encodable characters."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))


def main():
    all_findings = []
    files_scanned = 0
    
    for file_path in SKILLS_DIR.rglob("*"):
        if file_path.is_file() and not file_path.name.endswith('.tm7'):
            # Skip very large files
            if file_path.stat().st_size > 500_000:
                continue
            
            findings = scan_file(file_path)
            if findings:
                rel_path = file_path.relative_to(SKILLS_DIR.parent)
                for pattern_name, match_text, line_num, line_content in findings:
                    all_findings.append({
                        'file': str(rel_path),
                        'pattern': pattern_name,
                        'match': match_text[:50] + ('...' if len(match_text) > 50 else ''),
                        'line': line_num,
                        'context': line_content
                    })
            files_scanned += 1
    
    safe_print(f"Scanned {files_scanned} files")
    
    if all_findings:
        safe_print(f"\n[WARNING] FOUND {len(all_findings)} POTENTIAL SECRETS:")
        for f in all_findings:
            safe_print(f"  {f['file']}:{f['line']} - {f['pattern']}: {f['match']}")
            safe_print(f"    Context: {f['context']}")
        safe_print("\nThese would trigger GitHub Push Protection. Please sanitize.")
        sys.exit(1)
    else:
        safe_print("[OK] No secrets detected")
        sys.exit(0)


if __name__ == '__main__':
    main()