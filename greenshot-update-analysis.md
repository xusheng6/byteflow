# Greenshot Update Mechanism Analysis

## Overview

Greenshot **does** have an automated update checker, but it is a **notification-only** mechanism — it does **not** automatically download or install updates. It simply checks for new versions and notifies the user, who must then manually download the update from the website.

## How It Works

### Update Check Flow

1. **Startup**: `MainForm.cs:457` creates an `UpdateService` instance and calls `Startup()`, which registers a background periodic task.

2. **Background Polling**: The `UpdateService` (`src/Greenshot/Helpers/UpdateService.cs`) runs a background loop that:
   - Waits 20 seconds after app startup before the first check (to avoid slowing down launch).
   - Fetches a JSON feed from `https://getgreenshot.org/update-feed.json` using `Dapplo.HttpExtensions`.
   - Re-checks periodically based on the `UpdateCheckInterval` configuration (default: every **14 days**; configurable in settings from 0–365 days; 0 disables checks).

3. **Feed Format**: The JSON feed (`UpdateFeed` entity in `src/Greenshot/Helpers/Entities/UpdateFeed.cs`) contains just two fields:
   ```json
   {
     "release": "1.3.x",
     "beta": "2.0.x"
   }
   ```

4. **Version Comparison**: `ProcessFeed()` strips non-numeric characters from the version strings and parses them as `System.Version` objects. It compares the feed versions against the running application's `FileVersionInfo`.

5. **User Notification**: If a newer version is found (and >24 hours since the last notification), it shows a toast/tray notification via `INotificationService`. Clicking the notification opens `https://getgreenshot.org/downloads` in the default browser using `Process.Start()`.

### Configuration (`CoreConfiguration.cs`)

| Setting | Default | Description |
|---|---|---|
| `UpdateCheckInterval` | 14 (days) | How often to check; 0 = disabled |
| `CheckForUnstable` | false | Also check for beta versions |
| `LastUpdateCheck` | — | Timestamp of the last check |

## Signature / Integrity Verification

**Greenshot does NOT verify the signature or integrity of any downloaded file in its update mechanism**, because it does not download any files at all. The entire update flow is:

1. Fetch a small JSON feed over HTTPS.
2. Compare version numbers.
3. Show a notification.
4. Open the browser to the downloads page.

There is:
- **No automatic download** of installers or binaries.
- **No signature verification** (Authenticode, GPG, checksums, etc.) anywhere in the update code.
- **No hash/checksum validation** of the JSON feed itself (it relies solely on HTTPS transport security).
- **No code-signing certificate pinning** or public key verification.

The only security provided is **HTTPS** for the feed URL (`https://getgreenshot.org/update-feed.json`), which protects against passive eavesdropping and basic MITM attacks but does not provide application-level integrity verification.

## Security Implications

Since Greenshot only notifies the user and directs them to the website, the attack surface of the update mechanism itself is limited to:

1. **Feed manipulation**: If an attacker compromises the web server or performs a MITM attack (e.g., via a compromised CA), they could serve a fake version number to suppress update notifications (downgrade notification attack) or potentially craft a malicious feed. However, the feed is only parsed for version strings — there are no download URLs or executable paths in the feed data.

2. **Notification URL**: The download URL (`https://getgreenshot.org/downloads`) is hardcoded in the source code, not taken from the feed. This means an attacker cannot redirect users to a malicious download via feed manipulation alone.

## Key Source Files

- `src/Greenshot/Helpers/UpdateService.cs` — Main update check logic
- `src/Greenshot/Helpers/Entities/UpdateFeed.cs` — JSON feed entity model
- `src/Greenshot/Forms/MainForm.cs:457` — Where the update service is started
- `src/Greenshot.Base/Core/CoreConfiguration.cs:204-208` — Update-related config properties
- `src/Greenshot/Forms/SettingsForm.cs:532` — UI for configuring the check interval
