---
name: agentme-edr-policy-027-environment-variable-configuration-files
description: Defines when to use YAML config files versus .env files for configuration, how to combine them, and how .env is loaded for spawned processes. Use when setting up project configuration for any application, CLI, or library.
apply-to: All projects that use environment variables for configuration
valid-from: 2026-06-09
---

# agentme-edr-policy-027: Environment variable configuration files

## Context and Problem Statement

Projects need a consistent way to define non-secret configuration — service URLs, feature flags, port numbers, runtime modes — that varies across environments. Ad-hoc approaches (hardcoded defaults, scattered exports, application-level dotenv loaders, and flat env-var-only configs) lead to inconsistent behavior and unclear ownership of configuration.

CLI tools additionally need to handle multi-attribute invocation configuration without forcing users to provide every value as a flag. At the same time, some of those values may be environment-specific and must not be committed to the repository.

How should projects manage environment variable configuration and CLI invocation configuration across local development, deployment stages, and Makefiles?

## Decision Outcome

**Use YAML config files for CLI invocation configuration with multiple attributes; use `.env` files to supply environment variables to spawned processes and to hold uncommitted values referenced by config files. Load `.env` exclusively at process launch time — never inside application code.**

Secrets (API keys, passwords, tokens) MUST NOT be placed in `.env` files. Those are handled by [agentme-edr-022](../principles/022-secrets-management.md).

### Details

#### 01-when-to-use-dotenv

A `.env` file MUST be used when either of the following is true:

1. **Spawned process needs env vars** — the project launches a process (a deployable service, background worker, or shell script) that reads configuration from OS environment variables such as port numbers or API endpoint URLs.
2. **Value must not be committed** — a configuration value used in a YAML config file (see rule 07) is environment-specific or sensitive enough to exclude from version control. In that case, store the value in `.env` and reference it from the YAML file using env var substitution (see rule 08).

Do not use `.env` as a general-purpose configuration store when a YAML config file is the right tool (see rule 07).

Example `.env` for a service with process-level env vars:
```
SERVER_URL=http://localhost:8080
LOG_LEVEL=debug
FEATURE_FLAG_NEW_UI=false
```

---

#### 02-dotenv-not-committed

`.env` MUST be listed in `.gitignore` and must never be committed to the repository. It is intended for local use in standalone projects and libraries that do not have a formal deployment pipeline.

---

#### 03-dotenv-example-committed

A `.env.example` file MUST be committed alongside `.env`. It contains all the same variable names with placeholder or illustrative values — no real URLs, credentials, or server names. This file documents what configuration is expected without exposing real values.

Example `.env.example`:
```
SERVER_URL=http://localhost:8080
LOG_LEVEL=debug
FEATURE_FLAG_NEW_UI=false
```

---

#### 04-stage-specific-dotenv-committed

Stage-specific overrides MUST use the naming convention `.env.[stage]` (e.g., `.env.production`, `.env.staging`, `.env.test`). These files may be committed to the repository because they carry deployment-stage configuration rather than local developer configuration. They are used during deployment pipelines where the stage is known and explicit.

The generic `.env` must still not be committed. The distinction is: `.env` is for local, ad-hoc, standalone use; `.env.[stage]` is for deployment pipelines with a defined environment identity.

---

#### 05-load-in-makefile-before-processes

When `.env` defines variables consumed by shell scripts or spawned processes, the Makefile MUST load and export them before invoking those processes. Use the following pattern at the top of the relevant Makefile or in a shared include:

```makefile
ifneq (,$(wildcard .env))
  include .env
  export
endif
```

This ensures all variables in `.env` are available as environment variables to every child process spawned by `make`. The `ifneq` guard prevents errors when `.env` does not exist (e.g., in CI or fresh checkouts).

---

#### 06-no-application-level-dotenv-loading

Applications MUST NOT load `.env` files directly inside their own code using dotenv libraries or equivalent mechanisms. Configuration must enter the process exclusively as OS-level environment variables, set before the process is launched (by the Makefile, a shell script, CI, or a container runtime).

Prohibited patterns:

```python
# Python — disallowed
from dotenv import load_dotenv
load_dotenv()
```

```typescript
// TypeScript — disallowed
import dotenv from "dotenv";
dotenv.config();
```

```go
// Go — disallowed
godotenv.Load()
```

Permitted pattern: set env vars in the Makefile (see rule 05), then launch the application normally. Inside application code, read configuration only from `os.environ`, `process.env`, or the standard OS environment API for the language.

This rule prevents two parallel loading paths — OS env and file-based env — from coexisting invisibly in the same process.

---

#### 07-cli-adapters-use-yaml-config

CLI adapters with multiple configuration attributes MUST use a YAML config file rather than env vars or flags for those attributes. This applies whenever configuration is nested, repetitive, or too verbose for flags alone.

The CLI layer is responsible for loading and parsing the YAML file and passing the resolved values to the application layer. The application layer must not read the config file directly.

Default config file discovery should follow the pattern defined in [agentme-edr-015](../application/015-cli-tool-standards.md): load `[cwd]/[tool-name].yml` by default, or an explicit path provided via `--config`.

Example `myconfig.yml`:
```yaml
openapi_endpoint: https://example.com/openapi
log_level: debug
max_retries: 3
```

---

#### 08-env-var-substitution-in-config-files

When a YAML config file contains a value that MUST NOT be committed (such as a real endpoint URL, a username, or any other environment-specific value), that value must be expressed as an environment variable reference using `${VAR_NAME}` syntax, and the actual value must be defined in `.env`.

This keeps the YAML file committable while keeping the environment-specific value out of the repository.

Example:

`.env` (not committed):
```
OPENAPI_ENDPOINT=https://real-server.example.com/openapi
```

`myconfig.yml` (committed):
```yaml
openapi_endpoint: ${OPENAPI_ENDPOINT}
log_level: debug
```

The `.env` file must be loaded in the Makefile before launching the process (see rule 05) so the variable is available when the CLI or process reads the config file.

## References

- [agentme-edr-022](../principles/022-secrets-management.md) - Secrets must use OS keychains or cloud secret managers, not `.env` files
- [agentme-edr-017](017-tool-execution-and-scripting.md) - Makefiles are the authoritative command entry point; rule 05 above integrates with that standard
- [agentme-edr-008](008-common-targets.md) - Standard Makefile target names
- [agentme-edr-015](../application/015-cli-tool-standards.md) - CLI config file discovery and CLI-to-application separation
