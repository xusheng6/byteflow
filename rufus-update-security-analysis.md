# Rufus Update Mechanism & Signature Verification Analysis

## Does Rufus have an automated update mechanism?

**Yes.** Rufus has a fully automated update check and download system implemented primarily in `src/net.c` and `src/stdlg.c`.

### How the update check works (`CheckForUpdatesThread` in `src/net.c`)

1. **Periodic check**: By default, Rufus checks for updates every 24 hours (`DEFAULT_UPDATE_INTERVAL = 24*3600`). Users can disable this or force a manual check.
2. **Version file retrieval**: Rufus queries its server (`RUFUS_URL`) for a `.ver` version file matching the OS architecture and version (e.g., `rufus_win_x64_6.2.ver`), falling back to less-specific names.
3. **Version comparison**: The downloaded version file is parsed to extract the new version number, minimum platform requirements, and a download URL. If the server version is newer, the user is prompted to download it.

### How the update binary is downloaded

The actual update binary is downloaded via `DownloadSignedFile()` (`src/net.c:345-407`), called through `DownloadSignedFileThreaded()` from the update dialog in `src/stdlg.c:1871`.

---

## Does Rufus verify signatures on downloaded binaries?

**Yes, extensively.** Rufus implements **multiple layers** of signature verification:

### Layer 1: OpenSSL RSA Signature on Download (`DownloadSignedFile`)

**File**: `src/net.c:344-407`

When downloading the update binary:
1. The binary is downloaded to a memory buffer (not written to disk yet).
2. A corresponding `.sig` file is downloaded from the same URL + `.sig` suffix.
3. `ValidateOpensslSignature()` is called to verify the binary against the `.sig` file using a **hardcoded RSA-2048 public key** embedded in `src/pki.c:111-156`.
4. The verification uses SHA-256 hashing via `CryptHashData` + `CryptVerifySignature` (Windows CryptoAPI).
5. **If verification fails**: the download is rejected with `"FATAL: Download signature is invalid"`, the status is set to 403 (Forbidden), and the binary is never written to disk.
6. **Only if verification succeeds** is the binary written to the output file.

### Layer 2: Authenticode Signature Validation (`ValidateSignature`)

**File**: `src/pki.c:728-821`

Before launching the downloaded update binary (`src/stdlg.c:1839`):
1. **Certificate name check**: `GetSignatureName()` extracts the signer's Common Name and country code, validating against a hardcoded allowlist:
   - Accepted names: `"Akeo Consulting"`, `"Akeo Systems"`, `"Pete Batard"` (defined in `src/pki.c:46`)
   - Expected country: `"IE"` (Ireland) (defined in `src/pki.c:48`)
2. **WinVerifyTrust (Authenticode)**: Calls `WinVerifyTrustEx()` with `WTD_REVOKE_WHOLECHAIN` to perform full Windows Authenticode validation including certificate chain and revocation checking.
3. **If the signature name doesn't match**: the user is warned and the update is rejected (unless they explicitly override).
4. **If Authenticode fails**: the downloaded file is unconditionally deleted.

### Layer 3: Timestamp Anti-Rollback Protection

**File**: `src/pki.c:792-805`

After Authenticode validation succeeds:
1. The **RFC 3161 timestamp** of the currently-running Rufus binary is retrieved.
2. The **RFC 3161 timestamp** of the downloaded update is retrieved.
3. If the update's timestamp is **older** than the current binary's timestamp, the update is rejected: `"Update timestamp is younger than ours - Aborting update"`.
4. This prevents **downgrade attacks** where an attacker could serve a legitimately-signed but older (potentially vulnerable) version of Rufus.

### Layer 4: Nested Timestamp Cross-Validation

**File**: `src/pki.c:700-714`

When dual-signing (SHA-1 + SHA-256) was used:
1. Both the primary and nested signature timestamps are extracted.
2. If they differ by more than 60 seconds, the timestamps are rejected as potentially tampered.
3. This prevents an attacker from altering the more vulnerable signature's timestamp to bypass chronology checks.

### Layer 5: Version File Signature Verification

**File**: `src/net.c:700-706`

Even the `.ver` version file itself (which tells Rufus about available updates) is signature-verified:
1. A corresponding `.sig` file is downloaded for the version file.
2. `ValidateOpensslSignature()` validates it against the same hardcoded RSA-2048 key.
3. If invalid: `"FATAL: Version signature is invalid"` — the update process aborts entirely.

This prevents an attacker from injecting a fake version file to redirect users to a malicious download URL.

---

## Summary

| Security Layer | What it Protects | Mechanism |
|---|---|---|
| Version file RSA signature | Update metadata integrity | Hardcoded RSA-2048 pubkey + SHA-256 |
| Download RSA signature (.sig) | Binary integrity before write | Hardcoded RSA-2048 pubkey + SHA-256 |
| Authenticode (WinVerifyTrust) | Binary authenticity + chain of trust | Windows PKI with revocation checking |
| Certificate name/country check | Signer identity verification | Allowlist: "Akeo Consulting" / "Akeo Systems" / "Pete Batard" (IE) |
| Timestamp anti-rollback | Downgrade attack prevention | RFC 3161 timestamp comparison |
| Nested timestamp validation | Dual-sign tampering prevention | Cross-validation within 60-second tolerance |

**Conclusion**: Rufus has a robust, defense-in-depth approach to update security. It verifies signatures at multiple stages — the version metadata, the downloaded binary (before writing to disk), and the binary again (via Authenticode before execution). It also includes anti-rollback protections to prevent downgrade attacks using legitimately-signed older versions.
