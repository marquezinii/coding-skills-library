<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## Layer 2: Image Scanning

### 2.1 Trivy (Recommended — Fast, Comprehensive)

```bash
# Install
brew install trivy                              # macOS
apt install trivy                               # Debian/Ubuntu
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh \
  -o "$tmpdir/trivy-install.sh"
sed -n '1,160p' "$tmpdir/trivy-install.sh"
sh "$tmpdir/trivy-install.sh"

# Scan an image for CVEs
trivy image myapp:latest

# Fail CI on HIGH/CRITICAL severity
trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:latest

# Scan Dockerfile for misconfigurations
trivy config ./Dockerfile

# Scan entire repo (vulnerabilities + secrets + misconfigs)
trivy fs --scanners vuln,secret,misconfig .

# Generate SBOM (CycloneDX or SPDX)
trivy image --format cyclonedx --output sbom.json myapp:latest
trivy image --format spdx-json  --output sbom.spdx.json myapp:latest

# Ignore specific CVEs (add justification comments)
trivy image --ignorefile .trivyignore myapp:latest
```

**.trivyignore example:**
```
# CVE-2023-1234 — only exploitable via X feature, not used in this app
CVE-2023-1234

# CVE-2023-5678 — fix not yet available; tracked in issue #42
CVE-2023-5678
```

### 2.2 Grype (Anchore Alternative)

```bash
# Install
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh \
  -o "$tmpdir/grype-install.sh"
sed -n '1,160p' "$tmpdir/grype-install.sh"
sh "$tmpdir/grype-install.sh"

# Scan image
grype myapp:latest

# Fail on critical
grype myapp:latest --fail-on critical

# Output SARIF for GitHub Security tab
grype myapp:latest -o sarif > results.sarif

# Pair with Syft for SBOM generation
syft myapp:latest -o cyclonedx-json > sbom.json
grype sbom:sbom.json                            # Scan the SBOM directly
```

### 2.3 Hadolint — Dockerfile Linting

```bash
# Run directly
docker run --rm -i hadolint/hadolint < Dockerfile

# With config file
hadolint --config .hadolint.yaml --failure-threshold warning Dockerfile
```

**.hadolint.yaml:**
```yaml
failure-threshold: warning
ignore:
  - DL3008   # Pin versions in apt-get (allow floating for base layer)
trustedRegistries:
  - gcr.io
  - ghcr.io
  - public.ecr.aws
```

### 2.4 Secret Scanning in Images

```bash
# Trivy covers secrets too
trivy image --scanners secret myapp:latest

# Dedicated: TruffleHog
trufflehog docker --image myapp:latest

# git-secrets to prevent committing secrets
git secrets --scan
```

### 2.5 CI Integration (GitHub Actions — SHA-Pinned)

```yaml
permissions:
  contents: read
  security-events: write      # Required for uploading SARIF

jobs:
  security-scan:
    runs-on: ubuntu-24.04
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2

      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Lint Dockerfile
        uses: hadolint/hadolint-action@54c9adbab1582c2ef04b2016b760714a4bfde3cf  # v3.1.0
        with:
          dockerfile: Dockerfile
          failure-threshold: warning

      - name: Scan with Trivy
        uses: aquasecurity/trivy-action@6e7b7d1fd3e4fef0c5fa8cce1229c54b2c9bd0d8  # v0.28.0
        with:
          image-ref: myapp:${{ github.sha }}
          format: sarif
          output: trivy-results.sarif
          severity: HIGH,CRITICAL
          exit-code: '1'

      - name: Upload results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@4f3212b61783c3c68e8309a0f18a699764811cda  # v3.27.1
        if: always()          # Upload even if scan found issues
        with:
          sarif_file: trivy-results.sarif
```

---

## Layer 3: Runtime Security

### 3.1 docker run Hardening Flags

```bash
docker run \
  --read-only \                              # Read-only root filesystem
  --tmpfs /tmp:noexec,nosuid,size=100m \     # Writable tmpfs for /tmp only
  --tmpfs /var/run \                         # For PID files if needed
  --user 10001:10001 \                       # Non-root UID:GID
  --cap-drop ALL \                           # Drop ALL Linux capabilities
  --cap-add NET_BIND_SERVICE \               # Re-add only what's truly needed
  --security-opt no-new-privileges:true \    # Prevent privilege escalation via setuid
  --security-opt seccomp=seccomp.json \      # Custom seccomp profile
  --security-opt apparmor=docker-default \   # AppArmor profile
  --pids-limit 100 \                         # Prevent runaway process spawning
  --memory 512m \                            # OOM protection
  --memory-swap 512m \                       # Disable swap
  --cpus 1.0 \                               # CPU limit
  --network none \                           # No network (if not needed)
  --health-cmd "curl -f http://localhost:3000/health || exit 1" \
  --health-interval 30s \
  myapp:latest
```

### 3.2 Linux Capabilities — What to Drop and Keep

Drop ALL, then explicitly add only what your app requires:

| Capability | Purpose | Keep? |
|---|---|---|
| `NET_BIND_SERVICE` | Bind ports < 1024 | Only if binding a privileged port |
| `CHOWN` | Change file ownership | No — set ownership at build time |
| `SETUID` / `SETGID` | Switch user identity | No — drop always |
| `SYS_ADMIN` | Broad privileged operations | No — most dangerous capability |
| `NET_ADMIN` | Configure network interfaces | No (only network tools) |
| `SYS_PTRACE` | Debug/trace processes | No (only debugger containers) |
| `DAC_OVERRIDE` | Override file permissions | No — runs as correct user |
| `NET_RAW` | Raw sockets (ping) | No (blocked by default seccomp anyway) |

> **Most web apps need zero capabilities.** `--cap-drop ALL` alone is often sufficient.

### 3.3 Docker Compose Hardening

```yaml
services:
  app:
    image: myapp:latest
    read_only: true
    user: "10001:10001"
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
      - /var/run:noexec,nosuid,size=10m
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE    # Only if binding port < 1024
    security_opt:
      - no-new-privileges:true
      - seccomp:./references/seccomp-profile-template.json
    pids_limit: 100
    mem_limit: 512m
    memswap_limit: 512m
    cpus: 1.0
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    networks:
      - backend
    # Only expose externally if truly required
    # ports: ["8080:8080"]
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

networks:
  backend:
    driver: bridge
    internal: true    # No external connectivity unless needed
```

### 3.4 Seccomp Profiles

The Docker default seccomp profile blocks ~44 dangerous syscalls. For stricter control:

```bash
# Step 1: Audit syscalls your app actually makes
docker run --security-opt seccomp=unconfined \
  --name audit-run myapp:latest &

# Capture with strace
strace -c -p $(docker inspect --format '{{.State.Pid}}' audit-run)

# Or with sysdig (more container-friendly)
sysdig -p "%syscall.type" container.name=audit-run | sort -u

# Step 2: Build a custom profile from references/seccomp-profile-template.json
# Step 3: Apply it
docker run --security-opt seccomp=references/seccomp-profile-template.json myapp:latest
```

See `references/seccomp-profile-template.json` for a minimal starting allowlist for typical web servers.

### 3.5 AppArmor Profile (Linux hosts)

```bash
# Load Docker's default AppArmor profile
sudo apparmor_parser -r /etc/apparmor.d/docker-default

# Apply at runtime
docker run --security-opt apparmor=docker-default myapp:latest

# Generate a custom profile
aa-genprof myapp   # Interactive — run app under aa-complain mode first
```

---

## Layer 4: Supply Chain Security

### 4.1 Sign Images with Cosign (Sigstore — Keyless)

```bash
# Install cosign
brew install cosign    # macOS
# or: https://github.com/sigstore/cosign/releases

# Sign after push — keyless via OIDC (no long-lived keys)
cosign sign ghcr.io/org/myapp:latest

# Verify before deploy
cosign verify ghcr.io/org/myapp:latest \
  --certificate-identity-regexp="https://github.com/org/repo" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com"
```

**GitHub Actions — Sign & Verify Pipeline:**
```yaml
permissions:
  id-token: write     # Required for OIDC keyless signing
  packages: write

steps:
  - uses: sigstore/cosign-installer@dc72c7d5c4d10cd6bcb8cf6e3fd625a9e5e537da  # v3.7.0

  - name: Sign image (keyless via OIDC)
    run: |
      cosign sign --yes \
        ghcr.io/${{ github.repository }}:${{ github.sha }}
    env:
      COSIGN_EXPERIMENTAL: "true"

  - name: Attach SBOM attestation
    run: |
      cosign attest --yes \
        --predicate sbom.json \
        --type cyclonedx \
        ghcr.io/${{ github.repository }}:${{ github.sha }}
```

### 4.2 SBOM Generation & Attestation

```bash
# Generate SBOM with Syft
syft myapp:latest -o cyclonedx-json > sbom.json
syft myapp:latest -o spdx-json > sbom.spdx.json

# Attach to image as attestation
cosign attest --predicate sbom.json --type cyclonedx ghcr.io/org/myapp:latest

# Verify SBOM attestation before deployment
cosign verify-attestation \
  --type cyclonedx \
  --certificate-identity-regexp="https://github.com/org/repo" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  ghcr.io/org/myapp:latest
```

### 4.3 Use Trusted Registries & Enable Registry Scanning

| Registry | Built-in Scanning | Notes |
|---|---|---|
| GHCR (GitHub Container Registry) | No (use Trivy in CI) | Best for OSS, OIDC auth |
| AWS ECR | Yes (enhanced scanning via Inspector) | Enable per-repo |
| GCP Artifact Registry | Yes (Container Analysis) | Enabled by default |
| Azure ACR | Yes (Defender for Containers) | Premium tier |
| Docker Hub | Yes (limited on free tier) | Avoid for private images |

```bash
# Enable ECR enhanced scanning
aws ecr put-registry-scanning-configuration \
  --scan-type ENHANCED \
  --rules '[{"repositoryFilters":[{"filter":"*","filterType":"WILDCARD"}],"scanFrequency":"CONTINUOUS_SCAN"}]'
```

### 4.4 Admission Control — Block Unsigned/Unscanned Images

```yaml
# Kyverno policy — require signed images before admission
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-signed-images
spec:
  validationFailureAction: Enforce
  rules:
    - name: verify-image-signature
      match:
        resources:
          kinds: [Pod]
      verifyImages:
        - imageReferences:
            - "ghcr.io/org/*"
          attestors:
            - entries:
                - keyless:
                    subject: "https://github.com/org/repo/.github/workflows/*"
                    issuer: "https://token.actions.githubusercontent.com"
```

---

## Layer 5: Kubernetes Pod Security

> Full reference: `references/kubernetes-pod-security.md`

### 5.1 Pod Security Context

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: production
spec:
  replicas: 3
  template:
    spec:
      # ── Pod-level security context ─────────────────────
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        runAsGroup: 10001
        fsGroup: 10001
        fsGroupChangePolicy: OnRootMismatch
        seccompProfile:
          type: RuntimeDefault    # Use containerd/runc default seccomp
        supplementalGroups: []

      automountServiceAccountToken: false   # Disable unless needed

      # ── Container-level security context ──────────────
      containers:
        - name: app
          image: ghcr.io/org/myapp@sha256:<digest>   # Always use digest
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
              add: []              # Add nothing unless absolutely required
            runAsNonRoot: true
            runAsUser: 10001
            seccompProfile:
              type: RuntimeDefault

          # ── Resource limits (required for restricted PSA) ──
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"

          # ── Writable tmpfs mounts ──────────────────────
          volumeMounts:
            - name: tmp
              mountPath: /tmp
            - name: varrun
              mountPath: /var/run

      volumes:
        - name: tmp
          emptyDir:
            medium: Memory
            sizeLimit: 100Mi
        - name: varrun
          emptyDir:
            medium: Memory
            sizeLimit: 10Mi
```

### 5.2 Pod Security Admission (K8s 1.25+)

```bash
# Audit existing workloads before enforcing
kubectl label namespace production \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/audit-version=latest

# Warn in staging, enforce in production
kubectl label namespace staging \
  pod-security.kubernetes.io/warn=restricted

kubectl label namespace production \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/enforce-version=latest
```

| PSA Level | What It Blocks |
|---|---|
| `privileged` | No restrictions |
| `baseline` | Blocks hostNetwork, hostPID, privileged containers, hostPath |
| `restricted` | Also requires non-root, read-only FS, drops capabilities, seccomp |

### 5.3 NetworkPolicy — Zero-Trust Networking

```yaml
# Step 1: Deny all ingress and egress by default in the namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]

---
# Step 2: Selectively allow only required traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-app
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: ingress-nginx
          podSelector:
            matchLabels:
              app.kubernetes.io/name: ingress-nginx
      ports:
        - port: 3000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - port: 5432
    - to:                 # Allow only cluster DNS
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - port: 53
          protocol: UDP
        - port: 53
          protocol: TCP
```

### 5.4 RBAC — Least Privilege

```yaml
# Create minimal role — never use wildcards
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-reader
  namespace: production
rules:
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    resourceNames: ["myapp-config"]    # Lock to specific resource names
    verbs: ["get"]                     # Never ["*"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-reader-binding
  namespace: production
subjects:
  - kind: ServiceAccount
    name: myapp-sa
    namespace: production
roleRef:
  kind: Role
  name: app-reader
  apiGroup: rbac.authorization.k8s.io
```

```bash
# Audit what permissions a service account has
kubectl auth can-i --list --as=system:serviceaccount:production:myapp-sa

# Find overly-permissive cluster roles
kubectl get clusterrolebindings -o json | \
  jq '.items[] | select(.roleRef.name == "cluster-admin") | .subjects'
```

### 5.5 Kyverno Policy Examples

```yaml
# Require non-root containers
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-non-root
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-run-as-non-root
      match:
        resources:
          kinds: [Pod]
      validate:
        message: "Containers must not run as root (runAsNonRoot: true required)"
        pattern:
          spec:
            containers:
              - securityContext:
                  runAsNonRoot: true

---
# Require image digest pinning
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-image-digest
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-digest
      match:
        resources:
          kinds: [Pod]
      validate:
        message: "Images must be pinned to a SHA256 digest, not just a tag"
        pattern:
          spec:
            containers:
              - image: "*@sha256:*"

---
# Block privileged containers
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-privileged
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-privileged
      match:
        resources:
          kinds: [Pod]
      validate:
        message: "Privileged containers are not allowed"
        pattern:
          spec:
            containers:
              - =(securityContext):
                  =(privileged): "false"
```

---

## Common Pitfalls & Fixes

| Problem | Root Cause | Fix |
|---|---|---|
| Image runs as root | No `USER` directive | Add `RUN useradd ...` and `USER appuser` |
| Secret in `docker history` | `ENV` or `RUN curl -H "Bearer $TOKEN"` | Use `RUN --mount=type=secret` |
| Large image with many CVEs | Full base image (`node:20`, `ubuntu`) | Switch to `node:20-slim` or `distroless` |
| App crashes with `--read-only` | Writes to `/tmp` or app directory | Add `--tmpfs /tmp` for writable temp space |
| Trivy scan blocks CI on unfixable CVEs | No ignore file | Add `.trivyignore` with justified entries |
| Container needs `SYS_ADMIN` | Missing `--cap-drop` context | Investigate why — almost always avoidable |
| Tag-based images drift over time | Mutable tags | Pin to `@sha256:` digest; use Renovate to update |
| K8s pod rejected by PSA | Missing security context fields | Add `runAsNonRoot`, `readOnlyRootFilesystem`, `allowPrivilegeEscalation: false` |
| App can't write to filesystem | `readOnlyRootFilesystem: true` | Mount `emptyDir` volumes for writable paths |

---

## Security Checklist

### Dockerfile
- [ ] Minimal base image (distroless, slim, or alpine — not full debian/ubuntu)
- [ ] Multi-stage build — no build tools, devDependencies, or compilers in runtime image
- [ ] Non-root `USER` declared before `CMD`/`ENTRYPOINT`
- [ ] Base image pinned to `@sha256:...` digest (not just tag)
- [ ] No secrets in `ENV`, `ARG`, or `RUN` commands
- [ ] `HEALTHCHECK` defined
- [ ] OCI labels present (`org.opencontainers.image.*`)
- [ ] `.dockerignore` excludes `.git`, `.env`, secrets, tests
- [ ] `ENTRYPOINT` uses exec form, not shell form

### Image Scanning
- [ ] Trivy or Grype scan in CI (fails on HIGH/CRITICAL)
- [ ] Hadolint passes with no warnings
- [ ] Secret scan run on image (`trivy --scanners secret`)
- [ ] SBOM generated and stored
- [ ] `.trivyignore` has justified entries for accepted CVEs

### Runtime
- [ ] `--read-only` filesystem
- [ ] `--cap-drop ALL` (add back only what's documented as required)
- [ ] `--security-opt no-new-privileges:true`
- [ ] `--security-opt seccomp=<profile>` applied
- [ ] Resource limits set (`--memory`, `--cpus`, `--pids-limit`)
- [ ] Image signed with Cosign; verified before deploy

### Kubernetes
- [ ] `readOnlyRootFilesystem: true`
- [ ] `allowPrivilegeEscalation: false`
- [ ] `runAsNonRoot: true` with explicit UID
- [ ] `capabilities.drop: ["ALL"]`
- [ ] Resource `requests` and `limits` defined
- [ ] `automountServiceAccountToken: false`
- [ ] Namespace PSA enforced at `restricted` level
- [ ] `NetworkPolicy` default-deny applied
- [ ] RBAC uses specific resource names and minimal verbs

---

## Reference Files

- `references/base-image-comparison.md` — Size, CVE count, shell/pkg-manager trade-offs: distroless vs alpine vs slim vs scratch
- `references/seccomp-profile-template.json` — Minimal syscall allowlist for typical web servers; start here and extend
- `references/kubernetes-pod-security.md` — NetworkPolicy, RBAC, OPA/Kyverno policies, service account hardening, PSA

## Related Skills

- `docker-expert` — General Docker usage, Compose orchestration, image optimization
- `gha-security-review` — Security audit of GitHub Actions workflows
- `github-actions-advanced` — CI pipeline patterns including scanner integration
- `kubernetes-architect` — Full Kubernetes architecture, not just security
- `api-security-best-practices` — Application-level security (injection, auth, OWASP)
- `k8s-security-policies` — Extended Kubernetes security policies

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific penetration testing or a formal security audit.
- Seccomp profiles and AppArmor are Linux-only; macOS/Windows Docker Desktop uses different mechanisms.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
