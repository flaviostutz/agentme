---
name: agentme-edr-policy-022-secrets-management
description: Defines how secrets (API keys, passwords, tokens, credentials, private certificates) must be stored, fetched, and provisioned. Use when implementing secret handling in any language or deployment target.
apply-to: All software projects handling secrets
valid-from: 2026-05-28
---

# agentme-edr-policy-022: Secrets management

## Context and Problem Statement

A "secret" is any sensitive information whose exposure would compromise security or access control. Examples include API keys, passwords, authentication tokens, credentials, and private certificates. Plain configuration data (feature flags, endpoint URLs, port numbers) is not a secret.

Secrets stored on disk — even in `.env` files excluded from version control — are vulnerable to accidental exposure, tooling leaks, and lateral movement after a compromise. Hardcoded or cached secrets resist rotation and create synchronization headaches across environments.

What practices should projects follow to handle secrets securely across local development and cloud deployments?

## Decision Outcome

**Use native OS keychains for local development and cloud secret managers for deployed environments, accessed through a unified connector with ordered fallback.**

All implementation practices derive from three guiding principles:

1. **Least exposure** — minimize the means, timespan, and surface of contact with the secret.
2. **Easiness in secret rotation** — design so rotating a secret requires no code change or redeployment.
3. **Support for local and cloud deployment runs** — the same application code must work transparently in both environments.

### Details

#### 01-no-secrets-on-disk

Secrets must never be stored on the disk of a developer machine or server. This includes `.env` files (even when gitignored), plaintext config files, embedded in source code, or any other file-based storage.

The only acceptable local persistence is through the operating system's native secret manager (e.g., macOS Keychain, Windows Credential Manager, Linux Secret Service).

---

#### 02-local-dev-uses-native-keychain

During local development, secrets must be stored and retrieved using the native OS secret manager. Use cross-platform libraries to keep the code OS-agnostic:

| Language | Library |
|----------|---------|
| Python | `keyring` |
| JavaScript/TypeScript | `cross-keychain` |
| Go | `go-keyring` |

The "group" (service name) defaults to the module name. The secret identifier should match the ID used in the cloud secret manager for consistency.

---

#### 03-fallback-lookup-order

Secret fetching must implement a fallback chain in the following order:

1. **Native OS keychain** — attempt to retrieve the secret using the local keychain library (used during local development).
2. **Cloud secret manager** — if not found locally, fetch from the configured cloud secret manager (AWS Secrets Manager, Azure Key Vault, etc.) (used in cloud environments).
3. **Raise an exception** — if both lookups fail, raise an exception with a clear message indicating both failed paths.

Example error message:
```
Secret 'db-password' could not be found in keychain under group 'mymodule' or in AWS Secrets Manager under secretId 'db-password'
```

---

#### 04-secret-fetching-in-connector

The secret fetching logic (including the fallback chain from rule 03) must live in a dedicated "connector" module or function. This isolates secret-access concerns from business logic and provides a single point to configure secret sources, caching policy, and error handling.

---

#### 05-setup-secrets-makefile-target

Every module that requires secrets must expose a `setup-secrets` Makefile target. This target:

- Prompts the user for each required secret value interactively.
- If the user provides an empty value, the existing secret is not updated.
- Stores the provided value in the native OS keychain.
- Uses the module name as the default group (service name).
- Uses secret identifiers that match the cloud secret manager IDs.

The desired developer flow:

```text
$ make run
Error: Secret 'api-key' could not be found in keychain under group 'mymodule'
       or in AWS Secrets Manager under secretId 'api-key'

$ make setup-secrets
Enter value for 'api-key' (leave empty to skip):
> ****
Secret 'api-key' stored in keychain under group 'mymodule'.

$ make run
# Application starts successfully
```

#### 05a-makefile-uses-security-utility

Makefile targets (e.g., `setup-secrets`) must use the macOS native `security` CLI to store and retrieve secrets from the keychain. This restricts Makefile-based secret management to macOS developer machines, which is acceptable since all contributors are expected to use macOS.

Do **not** use `keyring` or other cross-platform libraries in Makefiles — `security` is simpler to invoke from shell and requires no additional dependencies.

Storing a secret:
```makefile
security add-generic-password -a "$(USER)" -s "mymodule/api-key" -w "$(SECRET_VALUE)" -U
```

Retrieving a secret (e.g., to pass to a command):
```makefile
SECRET_VALUE := $(shell security find-generic-password -a "$(USER)" -s "mymodule/api-key" -w 2>/dev/null)
```

The `-U` flag updates the entry if it already exists. Use the format `<group>/<secret-id>` as the service name (`-s`) to mirror the module name and cloud secret manager ID convention defined in rule 02 and 05.

In library code (Python, JS/TS, Go), continue using the cross-platform libraries defined in rule 02 (`keyring`, `cross-keychain`, `go-keyring`). The `security` utility is only for Makefile scripts.

---

#### 06-never-log-or-leak-secrets

Secrets must never be logged under any circumstance or sent to any service that is not clearly the intended consumer of that secret (authentication, encryption, etc.). This applies to all log levels including debug and trace. Error messages must reference the secret name or identifier, never its value.

---

#### 07-prefer-dynamic-fetching

Wherever possible, fetch secrets dynamically from the secret manager at the time of use. Avoid storing secrets in global variables or caching them indefinitely. Dynamic fetching through a specialized service enables:

- Automatic password rotation without redeployment.
- Immediate propagation of rotated secrets.
- Reduced window of exposure if memory is compromised.

Short-lived caching (e.g., a few minutes) is acceptable when performance requires it, but must have an explicit TTL.

---

#### 08-prefer-fetching-at-point-of-use

Prefer fetching the secret inside the function that directly needs it rather than passing it through multiple layers as a function argument. This minimizes the exposure surface by reducing the number of code paths that handle the raw secret value.

Passing secrets via function arguments is acceptable when the consuming function cannot access the connector directly, but the default design should fetch at the point of use.

## References

- [agentme-edr-008](../devops/008-common-targets.md) - Common development script names (defines Makefile target conventions)
- [agentme-edr-009](009-error-handling.md) - Error handling (governs how the fallback exception should be raised)
