# DevSecOps Debugging Log

## Pipeline Run #1 — Container Scan Failure (CVE in base image)

**Date:** 2026-05-17  
**Pipeline run:** #1  
**Status:** Failed — Container Security Scan  

**What happened:**  
First pipeline run. SAST and SCA passed. Trivy scanned the Docker image and found Critical CVEs in the python:3.11-slim base image Debian packages. Pipeline blocked as designed — the security gate worked correctly.

**Root cause:**  
python:3.11-slim is built on Debian 13.4 which contains OS packages with unfixed CVEs. These are not fixable because Debian has not patched them yet.

**Fix applied:**  
Added --ignore-unfixed flag to Trivy command. This tells Trivy to only fail the build on CVEs where a patched version exists. Unfixed CVEs are still reported in the JSON artifact but do not block deployment.

---

## Pipeline Run #2 and #3 — langchain version does not exist

**Date:** 2026-05-17  
**Pipeline runs:** #2, #3  
**Status:** Failed — Docker build error inside Container Security Scan  

**What happened:**  
Attempted to fix CVE-2025-68664 in langchain-core by upgrading langchain to version 0.3.81. Docker build failed inside the pipeline with pip error: no matching distribution found.

**Root cause:**  
CVE-2025-68664 affects langchain-core, not the langchain package itself. These are two separate packages with different version numbering. langchain 0.3.81 does not exist — the langchain package only goes up to 0.3.30 in the 0.3.x series. The fix needed to target langchain-core directly.

**Secondary root cause:**  
langchain 0.3.30 requires langchain-core>=0.3.85 as a dependency. Pinning langchain-core==0.3.81 caused a dependency conflict because 0.3.81 is lower than the minimum required 0.3.85. Since 0.3.85 is higher than 0.3.81 it also contains the CVE fix.

**Fix applied:**  
Pinned langchain-core==0.3.85 which satisfies both the langchain 0.3.30 dependency requirement and patches CVE-2025-68664. Verified locally with docker build before pushing.

**Lesson learned:**  
Always verify package versions exist using pip index versions <package> before pinning. Always test docker build locally before pushing to avoid burning pipeline minutes on build errors.

---

## Pipeline Run #4 — Trivy image reference parsing failure

**Date:** 2026-05-17  
**Pipeline run:** #4  
**Status:** Failed — Container Security Scan  

**What happened:**  
Docker build succeeded. Trivy installed successfully. Trivy crashed with FATAL error before scanning could complete. No trivy-report.json was produced.

**Error message:**

FATAL Fatal error run error: image scan error: unable to initialize
artifact: failed to parse the image name: could not parse reference

**Root cause:**  
The Trivy command used YAML multiline syntax with backslash continuation and inconsistent indentation inside a block scalar. The GitHub Actions expression ${{ github.sha }} at the end of the multiline command was not being evaluated and passed correctly to the shell, resulting in an empty image reference being passed to Trivy.

**Fix applied:**  
Assigned the image name to a shell variable first, then passed the variable to Trivy:

```bash
IMAGE="eu-ai-governance:${{ github.sha }}"
trivy image --exit-code 1 --severity CRITICAL --ignore-unfixed --format json --output trivy-report.json "$IMAGE"
```

This ensures the GitHub Actions expression is evaluated before the trivy command runs, with no backslash continuation ambiguity.

**Lesson learned:**  
When using GitHub Actions expressions inside multiline shell commands, assign them to variables first. Backslash continuation in YAML block scalars can behave unexpectedly depending on indentation and shell environment.

---

## Pipeline Run #5 — All jobs passed

**Date:** 2026-05-17  
**Pipeline run:** #5  
**Status:** Success  

**Results:**  
- SAST (Bandit + Semgrep): ✅ 20s  
- SCA (pip-audit + Syft + Grype): ✅ 53s  
- Container Security Scan (Trivy): ✅ 37s  
- Push Image to ACR: ✅ 51s  

**CVE-2025-68664 status:** Patched via langchain-core==0.3.85  
**Image pushed to:** euaigovernanceacr.azurecr.io/eu-ai-governance:555a8fb...  
**Security gate:** Working correctly — blocks on fixable Critical CVEs, reports unfixable CVEs in artifact