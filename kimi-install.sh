#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-https://cdn.kimi.com/kimi-claw}"
TGZ_URL="${TGZ_URL:-$BASE_URL/kimi-claw-latest.tgz}"
SEARCH_TGZ_URL="${SEARCH_TGZ_URL:-$BASE_URL/openclaw-kimi-search-0.1.2.tgz}"

OPENCLAW_BIN="${OPENCLAW_BIN:-openclaw}"
NPM_BIN="${NPM_BIN:-npm}"
TARGET_DIR="${TARGET_DIR:-$HOME/.openclaw/extensions/kimi-claw}"
SEARCH_TARGET_DIR="${SEARCH_TARGET_DIR:-$HOME/.openclaw/extensions/kimi-search}"
OPENCLAW_CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-$HOME/.openclaw/openclaw.json}"
PROMPT_TIMEOUT_MS="${PROMPT_TIMEOUT_MS:-1800000}"
LOCAL_SYNC_CONFIG_PATH="${LOCAL_SYNC_CONFIG_PATH:-$HOME/.kimi/kimi-claw/kimi-claw-config.json}"
INSTALL_FAIL_LOG_DIR="${INSTALL_FAIL_LOG_DIR:-$HOME/.kimi/kimi-claw/log}"
INSTALL_RUN_LOG_PATH=""

WS_URL="${WS_URL:-}"
BOT_TOKEN="${BOT_TOKEN:-}"
KIMIAPI_HOST="${KIMIAPI_HOST:-${OPENCLAW_KIMIAPI_HOST:-}}"
GATEWAY_URL="${GATEWAY_URL:-}"
GATEWAY_TOKEN="${GATEWAY_TOKEN:-}"
GATEWAY_AGENT_ID="${GATEWAY_AGENT_ID:-}"

SEARCH_PLUGIN_ENABLED="${SEARCH_PLUGIN_ENABLED:-0}"
LOG_ENABLED_FLAG="0"
SHELL_ENABLED_FLAG="0"

usage() {
  cat <<'USAGE'
Usage:
  curl -fsSL https://cdn.kimi.com/kimi-claw/install.sh | bash -s -- [options]

Core options:
  --ws-url <ws_url>              Bridge WebSocket URL (optional)
  --bot-token <token>            Bridge token (optional)
  --kimiapi-host <url>           Kimi API host (optional)
  --gateway-url <ws_url>         Gateway URL (optional)
  --gateway-token <token>        Gateway token (optional)
  --agent-id <id>                Gateway agent id (optional)
  --tgz-url <url|s3://...>       Plugin package URL
  --target-dir <path>            Plugin install dir
  --with-search-plugin           Install kimi-search plugin together
  --skip-search-plugin           Do not install kimi-search plugin
  --search-tgz-url <url|s3://...> Search plugin package URL
  --search-target-dir <path>     Search plugin install dir
  --log-enabled                  Persist log.enabled=true into plugin config
  --shell-enabled                Persist bridge.shell.enabled=true into plugin config
  -h, --help

Notes:
  - Install and upgrade are unified: this script always performs a replace install.
  - Existing plugin config is kept by default.
  - If --ws-url is passed without --bot-token, bridge.token is written as empty string.
  - Optional config flags accept empty values; install still proceeds.
  - If no config options are passed, plugin runtime config is not modified.
USAGE
}

log() {
  printf "[install-oss] %s\n" "$*"
}

log_warn() {
  printf "[install-oss] WARN: %s\n" "$*"
}

log_error() {
  printf "[install-oss] ERROR: %s\n" "$*" >&2
}

expand_user_path() {
  local value="$1"
  if [ "$value" = "~" ]; then
    printf "%s" "$HOME"
    return
  fi
  case "$value" in
    "~/"*)
      printf "%s/%s" "$HOME" "${value#\~/}"
      ;;
    *)
      printf "%s" "$value"
      ;;
  esac
}

require_cmd() {
  local cmd="$1"
  local hint="$2"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    log_error "missing command: $cmd"
    log_error "$hint"
    exit 1
  fi
}

need_value() {
  local opt="$1"
  local val="${2:-}"
  if [ -z "$val" ]; then
    log_error "missing value for $opt"
    exit 1
  fi
}

need_next_arg() {
  local opt="$1"
  local argc="$2"
  if [ "$argc" -lt 2 ]; then
    log_error "missing value for $opt"
    exit 1
  fi
}

download_to_file() {
  local src="$1"
  local dst="$2"

  if [[ "$src" == s3://* ]]; then
    require_cmd aws "install aws cli then retry"
    aws s3 cp "$src" "$dst"
  else
    require_cmd curl "install curl then retry"
    curl -fsSL "$src" -o "$dst"
  fi
}

cleanup_legacy_plugin_config() {
  local config_path="$1"
  if [ ! -f "$config_path" ]; then
    return
  fi

  OPENCLAW_CONFIG_PATH="$config_path" node - <<'NODE'
const fs = require("fs");
const path = require("path");

const configPath = process.env.OPENCLAW_CONFIG_PATH || "";
if (!configPath) process.exit(0);

let payload;
try {
  payload = JSON.parse(fs.readFileSync(configPath, "utf8"));
} catch {
  process.exit(0);
}
if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
  process.exit(0);
}

let changed = false;
const plugins = payload.plugins && typeof payload.plugins === "object" && !Array.isArray(payload.plugins)
  ? payload.plugins
  : {};
if (payload.plugins !== plugins) {
  payload.plugins = plugins;
  changed = true;
}

const entries = plugins.entries && typeof plugins.entries === "object" && !Array.isArray(plugins.entries)
  ? plugins.entries
  : {};
if (plugins.entries !== entries) {
  plugins.entries = entries;
  changed = true;
}
if (Object.prototype.hasOwnProperty.call(entries, "openclaw-kimi-bridge-connector")) {
  delete entries["openclaw-kimi-bridge-connector"];
  changed = true;
}

const installs = plugins.installs && typeof plugins.installs === "object" && !Array.isArray(plugins.installs)
  ? plugins.installs
  : {};
if (plugins.installs !== installs) {
  plugins.installs = installs;
  changed = true;
}
if (Object.prototype.hasOwnProperty.call(installs, "openclaw-kimi-bridge-connector")) {
  delete installs["openclaw-kimi-bridge-connector"];
  changed = true;
}

const load = plugins.load && typeof plugins.load === "object" && !Array.isArray(plugins.load)
  ? plugins.load
  : {};
if (plugins.load !== load) {
  plugins.load = load;
  changed = true;
}
const rawPaths = Array.isArray(load.paths) ? load.paths : [];
if (!Array.isArray(load.paths)) {
  changed = true;
}
const nextPaths = [];
const seen = new Set();
for (const item of rawPaths) {
  if (typeof item !== "string") {
    changed = true;
    continue;
  }
  const resolved = path.resolve(item.startsWith("~/") ? path.join(process.env.HOME || "", item.slice(2)) : item);
  if (path.basename(resolved) === "openclaw-kimi-bridge-connector") {
    changed = true;
    continue;
  }
  if (seen.has(resolved)) {
    changed = true;
    continue;
  }
  seen.add(resolved);
  nextPaths.push(resolved);
}
if (
  !Array.isArray(load.paths) ||
  load.paths.length !== nextPaths.length ||
  load.paths.some((value, index) => value !== nextPaths[index])
) {
  load.paths = nextPaths;
  changed = true;
}

if (changed) {
  fs.writeFileSync(configPath, `${JSON.stringify(payload, null, 2)}\n`);
}
NODE
}

read_plugin_id_from_path() {
  local dir="$1"
  node - "$dir/openclaw.plugin.json" <<'NODE'
const fs = require("fs");
const filePath = process.argv[2];
if (!filePath) {
  process.stdout.write("kimi-claw");
  process.exit(0);
}
try {
  const payload = JSON.parse(fs.readFileSync(filePath, "utf8"));
  if (payload && typeof payload.id === "string" && payload.id.trim()) {
    process.stdout.write(payload.id.trim());
    process.exit(0);
  }
} catch {
  // ignore
}
process.stdout.write("kimi-claw");
NODE
}

build_config_patch_json() {
  WS_URL="$WS_URL" \
  BOT_TOKEN="$BOT_TOKEN" \
  KIMIAPI_HOST="$KIMIAPI_HOST" \
  GATEWAY_URL="$GATEWAY_URL" \
  GATEWAY_TOKEN="$GATEWAY_TOKEN" \
  GATEWAY_AGENT_ID="$GATEWAY_AGENT_ID" \
  LOG_ENABLED_FLAG="$LOG_ENABLED_FLAG" \
  SHELL_ENABLED_FLAG="$SHELL_ENABLED_FLAG" \
  node - <<'NODE'
const patch = {};

const setBridge = () => {
  if (!patch.bridge) patch.bridge = {};
  return patch.bridge;
};
const setGateway = () => {
  if (!patch.gateway) patch.gateway = {};
  return patch.gateway;
};

const wsUrl = String(process.env.WS_URL || "").trim();
const botToken = String(process.env.BOT_TOKEN || "").trim();
const kimiapiHost = String(process.env.KIMIAPI_HOST || "").trim();
const gatewayUrl = String(process.env.GATEWAY_URL || "").trim();
const gatewayToken = String(process.env.GATEWAY_TOKEN || "").trim();
const gatewayAgentId = String(process.env.GATEWAY_AGENT_ID || "").trim();

if (wsUrl) {
  const bridge = setBridge();
  bridge.url = wsUrl;
  bridge.token = botToken;
} else if (botToken) {
  const bridge = setBridge();
  bridge.token = botToken;
}

if (kimiapiHost) {
  const bridge = setBridge();
  bridge.kimiapiHost = kimiapiHost;
}

if (gatewayUrl) {
  const gateway = setGateway();
  gateway.url = gatewayUrl;
}
if (gatewayToken) {
  const gateway = setGateway();
  gateway.token = gatewayToken;
}
if (gatewayAgentId) {
  const gateway = setGateway();
  gateway.agentId = gatewayAgentId;
}

if (String(process.env.LOG_ENABLED_FLAG || "") === "1") {
  patch.log = { enabled: true };
}

if (String(process.env.SHELL_ENABLED_FLAG || "") === "1") {
  const bridge = setBridge();
  bridge.shell = { enabled: true };
}

process.stdout.write(JSON.stringify(patch));
NODE
}

merge_plugin_config() {
  local config_path="$1"
  local plugin_name="$2"
  local patch_json="$3"

  OPENCLAW_CONFIG_PATH="$config_path" PLUGIN_NAME="$plugin_name" PATCH_JSON="$patch_json" node - <<'NODE'
const fs = require("fs");

const configPath = process.env.OPENCLAW_CONFIG_PATH || "";
const pluginName = process.env.PLUGIN_NAME || "kimi-claw";
let patch;
try {
  patch = JSON.parse(process.env.PATCH_JSON || "{}");
} catch {
  patch = {};
}

const isRecord = (value) => value && typeof value === "object" && !Array.isArray(value);
const deepMerge = (base, incoming) => {
  const out = { ...base };
  for (const [key, value] of Object.entries(incoming)) {
    if (isRecord(out[key]) && isRecord(value)) {
      out[key] = deepMerge(out[key], value);
    } else {
      out[key] = value;
    }
  }
  return out;
};

let payload = {};
try {
  if (fs.existsSync(configPath)) {
    const parsed = JSON.parse(fs.readFileSync(configPath, "utf8"));
    if (isRecord(parsed)) {
      payload = parsed;
    }
  }
} catch {
  // ignore malformed file and fallback to empty object
}

const plugins = isRecord(payload.plugins) ? payload.plugins : {};
payload.plugins = plugins;
const entries = isRecord(plugins.entries) ? plugins.entries : {};
plugins.entries = entries;
const entry = isRecord(entries[pluginName]) ? entries[pluginName] : {};
entries[pluginName] = entry;
const existingConfig = isRecord(entry.config) ? entry.config : {};

const merged = deepMerge(existingConfig, patch);
process.stdout.write(JSON.stringify(merged));
NODE
}

patch_local_sync_config_if_exists() {
  local target_path="$LOCAL_SYNC_CONFIG_PATH"
  if [ ! -f "$target_path" ]; then
    log "local sync config not found; skip: $target_path"
    return 0
  fi

  if LOCAL_SYNC_CONFIG_PATH="$target_path" PROMPT_TIMEOUT_MS="$PROMPT_TIMEOUT_MS" node - <<'NODE'
const fs = require("fs");

const targetPath = process.env.LOCAL_SYNC_CONFIG_PATH || "";
const timeout = Number.parseInt(String(process.env.PROMPT_TIMEOUT_MS || ""), 10);

if (!targetPath) {
  process.exit(0);
}
if (!Number.isFinite(timeout)) {
  throw new Error("PROMPT_TIMEOUT_MS is invalid");
}

const raw = fs.readFileSync(targetPath, "utf8");
const payload = JSON.parse(raw);
if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
  throw new Error("local sync config must be a JSON object");
}

const bridge =
  payload.bridge && typeof payload.bridge === "object" && !Array.isArray(payload.bridge)
    ? payload.bridge
    : {};
payload.bridge = bridge;
bridge.promptTimeoutMs = timeout;

fs.writeFileSync(targetPath, `${JSON.stringify(payload, null, 2)}\n`);
NODE
  then
    log "patched local sync config: $target_path (bridge.promptTimeoutMs=$PROMPT_TIMEOUT_MS)"
  else
    log_warn "failed to patch local sync config: $target_path"
  fi
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --ws-url|--bridge-url)
      need_next_arg "$1" "$#"
      WS_URL="$2"
      shift 2
      ;;
    --bot-token)
      need_next_arg "$1" "$#"
      BOT_TOKEN="$2"
      shift 2
      ;;
    --kimiapi-host)
      need_next_arg "$1" "$#"
      KIMIAPI_HOST="$2"
      shift 2
      ;;
    --gateway-url)
      need_next_arg "$1" "$#"
      GATEWAY_URL="$2"
      shift 2
      ;;
    --gateway-token)
      need_next_arg "$1" "$#"
      GATEWAY_TOKEN="$2"
      shift 2
      ;;
    --agent-id)
      need_next_arg "$1" "$#"
      GATEWAY_AGENT_ID="$2"
      shift 2
      ;;
    --tgz-url)
      need_next_arg "$1" "$#"
      TGZ_URL="$2"
      need_value "$1" "$TGZ_URL"
      shift 2
      ;;
    --target-dir)
      need_next_arg "$1" "$#"
      TARGET_DIR="$2"
      need_value "$1" "$TARGET_DIR"
      shift 2
      ;;
    --with-search-plugin)
      SEARCH_PLUGIN_ENABLED="1"
      shift
      ;;
    --skip-search-plugin)
      SEARCH_PLUGIN_ENABLED="0"
      shift
      ;;
    --search-tgz-url)
      need_next_arg "$1" "$#"
      SEARCH_TGZ_URL="$2"
      need_value "$1" "$SEARCH_TGZ_URL"
      shift 2
      ;;
    --search-target-dir)
      need_next_arg "$1" "$#"
      SEARCH_TARGET_DIR="$2"
      need_value "$1" "$SEARCH_TARGET_DIR"
      shift 2
      ;;
    --log-enabled)
      LOG_ENABLED_FLAG="1"
      shift
      ;;
    --shell-enabled)
      SHELL_ENABLED_FLAG="1"
      shift
      ;;
    # compatibility flags (ignored)
    --bridge-mode|--bridge-user-id|--retry-base-ms|--retry-max-ms|--retry-max-attempts|--bridge-check-timeout-ms|--bridge-check-settle-ms|--gateway-check-timeout-ms|--gateway-check-settle-ms|--gateway-check-retries|--gateway-check-interval-ms|--gateway-check-initial-delay-ms|--model-id)
      need_next_arg "$1" "$#"
      shift 2
      ;;
    --skip-bridge-check|--skip-gateway-check|--skip-connectivity-checks|--allow-missing-bridge-config|--setup-default-model)
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      log_error "unknown argument: $1"
      usage
      exit 1
      ;;
  esac
done

TARGET_DIR="$(expand_user_path "$TARGET_DIR")"
SEARCH_TARGET_DIR="$(expand_user_path "$SEARCH_TARGET_DIR")"
OPENCLAW_CONFIG_PATH="$(expand_user_path "$OPENCLAW_CONFIG_PATH")"
INSTALL_FAIL_LOG_DIR="$(expand_user_path "$INSTALL_FAIL_LOG_DIR")"

require_cmd "$OPENCLAW_BIN" "install OpenClaw CLI then retry"
require_cmd "$NPM_BIN" "install Node.js + npm then retry"
require_cmd node "install Node.js then retry"
require_cmd tar "install tar then retry"

TMP_DIR="$(mktemp -d)"
INSTALL_TS="$(date +%s)"
INSTALL_RUN_LOG_PATH="$TMP_DIR/install_run.log"
if command -v tee >/dev/null 2>&1; then
  exec > >(tee -a "$INSTALL_RUN_LOG_PATH") 2>&1
else
  exec >>"$INSTALL_RUN_LOG_PATH" 2>&1
fi

# -- rollback state --
MAIN_BACKUP_DIR=""
MAIN_ROLLBACK_NEEDED="0"
MAIN_PLUGIN_NAME=""
SEARCH_BACKUP_DIR=""
SEARCH_ROLLBACK_NEEDED="0"
SEARCH_PLUGIN_NAME_SAVED=""

on_exit() {
  local exit_code=$?

  # rollback main plugin if needed
  if [ "$MAIN_ROLLBACK_NEEDED" = "1" ] && [ -n "$MAIN_BACKUP_DIR" ] && [ -d "$MAIN_BACKUP_DIR" ]; then
    log_warn "main plugin install failed (exit=$exit_code), rolling back to previous version"
    rm -rf "$TARGET_DIR"
    mv "$MAIN_BACKUP_DIR" "$TARGET_DIR"
    "$OPENCLAW_BIN" plugins install -l "$TARGET_DIR" >/dev/null 2>&1 || true
    if [ -n "$MAIN_PLUGIN_NAME" ]; then
      "$OPENCLAW_BIN" plugins enable "$MAIN_PLUGIN_NAME" >/dev/null 2>&1 || true
    fi
    "$OPENCLAW_BIN" gateway restart >/dev/null 2>&1 || true
    log_warn "main plugin rollback completed"
  fi

  # rollback search plugin if needed
  if [ "$SEARCH_ROLLBACK_NEEDED" = "1" ] && [ -n "$SEARCH_BACKUP_DIR" ] && [ -d "$SEARCH_BACKUP_DIR" ]; then
    log_warn "search plugin install failed, rolling back to previous version"
    rm -rf "$SEARCH_TARGET_DIR"
    mv "$SEARCH_BACKUP_DIR" "$SEARCH_TARGET_DIR"
    "$OPENCLAW_BIN" plugins install -l "$SEARCH_TARGET_DIR" >/dev/null 2>&1 || true
    if [ -n "$SEARCH_PLUGIN_NAME_SAVED" ]; then
      "$OPENCLAW_BIN" plugins enable "$SEARCH_PLUGIN_NAME_SAVED" >/dev/null 2>&1 || true
    fi
    log_warn "search plugin rollback completed"
  fi

  if [ "$exit_code" -ne 0 ] && [ -n "$INSTALL_RUN_LOG_PATH" ] && [ -f "$INSTALL_RUN_LOG_PATH" ]; then
    local fail_log_file=""
    local fail_ts=""
    fail_ts="$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$INSTALL_FAIL_LOG_DIR" >/dev/null 2>&1 || true
    fail_log_file="$INSTALL_FAIL_LOG_DIR/install_fail_${fail_ts}_$$.log"
    if {
      printf "time=%s\n" "$(date '+%Y-%m-%d %H:%M:%S %z')"
      printf "exit_code=%s\n" "$exit_code"
      printf "target_dir=%s\n" "$TARGET_DIR"
      printf "search_target_dir=%s\n" "$SEARCH_TARGET_DIR"
      printf "tgz_url=%s\n" "$TGZ_URL"
      printf "search_tgz_url=%s\n\n" "$SEARCH_TGZ_URL"
      cat "$INSTALL_RUN_LOG_PATH"
    } >"$fail_log_file" 2>/dev/null; then
      log_warn "install failure log saved to: $fail_log_file"
    else
      log_warn "install failed and could not write failure log to: $INSTALL_FAIL_LOG_DIR"
    fi
  fi

  rm -rf "$TMP_DIR"
}
trap on_exit EXIT

# -- stage & verify helper --
# Usage: stage_plugin <tgz_path> <staging_dir>
# Extracts tgz, runs npm install, and verifies the result in a staging directory.
# The caller can then atomically swap the staging dir into the final target.
stage_plugin() {
  local tgz_path="$1"
  local staging_dir="$2"

  mkdir -p "$staging_dir"
  tar -xzf "$tgz_path" -C "$staging_dir" --strip-components=1

  if [ ! -f "$staging_dir/package.json" ]; then
    log_error "invalid tgz content (missing package.json)"
    return 1
  fi

  log "installing dependencies in staging dir"
  (
    cd "$staging_dir"
    "$NPM_BIN" install --omit=dev
  )

  # sanity check: verify the plugin entry point can be loaded
  if [ -f "$staging_dir/openclaw.plugin.json" ]; then
    local main_file
    main_file="$(node -e "
      const p = require('$staging_dir/openclaw.plugin.json');
      const m = p.main || 'index.js';
      process.stdout.write(require('path').resolve('$staging_dir', m));
    " 2>/dev/null || true)"
    if [ -n "$main_file" ] && [ -f "$main_file" ]; then
      if ! node -e "require('$main_file')" >/dev/null 2>&1; then
        log_error "sanity check failed: cannot require plugin entry point"
        return 1
      fi
      log "sanity check passed"
    fi
  fi
}

# -- backup helper --
# Usage: backup_dir <source_dir>
# Prints the backup path. Returns 1 if source doesn't exist (no backup needed).
backup_dir() {
  local src="$1"
  if [ ! -e "$src" ]; then
    return 1
  fi
  local backup="${src}.bak.${INSTALL_TS}"
  # remove stale backup with same timestamp (shouldn't happen)
  rm -rf "$backup"
  mv "$src" "$backup"
  printf "%s" "$backup"
}

# -- clean old backups helper --
cleanup_old_backups() {
  local base_dir="$1"
  local keep_path="${2:-}"
  shopt -s nullglob
  for old_backup in "${base_dir}".bak.*; do
    if [ -n "$keep_path" ] && [ "$old_backup" = "$keep_path" ]; then
      continue
    fi
    if [ -e "$old_backup" ]; then
      rm -rf "$old_backup"
      log "removed old backup: $old_backup"
    fi
  done
  shopt -u nullglob
}

# ============================================================
# Main plugin install
# ============================================================

log "downloading package"
download_to_file "$TGZ_URL" "$TMP_DIR/plugin.tgz"

log "staging main plugin"
STAGED_MAIN="$TMP_DIR/staged_main"
stage_plugin "$TMP_DIR/plugin.tgz" "$STAGED_MAIN"

PLUGIN_NAME="$(read_plugin_id_from_path "$STAGED_MAIN")"
MAIN_PLUGIN_NAME="$PLUGIN_NAME"

log "cleaning legacy config"
"$OPENCLAW_BIN" plugins disable "openclaw-kimi-bridge-connector" >/dev/null 2>&1 || true
cleanup_legacy_plugin_config "$OPENCLAW_CONFIG_PATH"

LEGACY_TARGET_DIR="$(dirname "$TARGET_DIR")/openclaw-kimi-bridge-connector"
if [ "$LEGACY_TARGET_DIR" != "$TARGET_DIR" ] && [ -e "$LEGACY_TARGET_DIR" ]; then
  rm -rf "$LEGACY_TARGET_DIR"
fi

# disable current plugin before swap
"$OPENCLAW_BIN" plugins disable "kimi-claw" >/dev/null 2>&1 || true

# backup existing install (if any)
if MAIN_BACKUP_DIR="$(backup_dir "$TARGET_DIR")"; then
  log "backed up existing install to $MAIN_BACKUP_DIR"
fi
MAIN_ROLLBACK_NEEDED="1"

# atomic swap: move staged dir into final location
mkdir -p "$(dirname "$TARGET_DIR")"
mv "$STAGED_MAIN" "$TARGET_DIR"

log "registering plugin"
"$OPENCLAW_BIN" plugins install -l "$TARGET_DIR" >/dev/null 2>&1 || true
"$OPENCLAW_BIN" plugins enable "$PLUGIN_NAME"

CONFIG_PATCH_JSON="$(build_config_patch_json)"
if [ "$CONFIG_PATCH_JSON" != "{}" ]; then
  MERGED_CONFIG_JSON="$(merge_plugin_config "$OPENCLAW_CONFIG_PATH" "$PLUGIN_NAME" "$CONFIG_PATCH_JSON")"
  "$OPENCLAW_BIN" config set "plugins.entries.$PLUGIN_NAME.config" --json "$MERGED_CONFIG_JSON"
  log "plugin config updated"
else
  log "plugin config kept as-is"
fi

"$OPENCLAW_BIN" config set "plugins.entries.$PLUGIN_NAME.config.bridge.promptTimeoutMs" --json "$PROMPT_TIMEOUT_MS"
log "prompt timeout set to ${PROMPT_TIMEOUT_MS}ms"
patch_local_sync_config_if_exists

# main plugin install succeeded — disable rollback, clean old backups
MAIN_ROLLBACK_NEEDED="0"
log "main plugin installed successfully"
cleanup_old_backups "$TARGET_DIR" "$MAIN_BACKUP_DIR"
if [ -n "$MAIN_BACKUP_DIR" ] && [ -d "$MAIN_BACKUP_DIR" ]; then
  rm -rf "$MAIN_BACKUP_DIR"
  log "removed backup: $MAIN_BACKUP_DIR"
fi

# ============================================================
# Search plugin install (independent — failure does not affect main)
# ============================================================

SEARCH_INSTALL_FAILED="0"
if [ "$SEARCH_PLUGIN_ENABLED" = "1" ]; then
  # Run search install in a subshell so that set -e is preserved inside,
  # but failure doesn't kill the parent script.
  # State changes (SEARCH_BACKUP_DIR, SEARCH_ROLLBACK_NEEDED) are communicated
  # via a state file because subshell variables don't propagate to parent.
  SEARCH_STATE_FILE="$TMP_DIR/search_state"
  (
    set -euo pipefail

    log "downloading search plugin"
    download_to_file "$SEARCH_TGZ_URL" "$TMP_DIR/search.tgz"

    log "staging search plugin"
    STAGED_SEARCH="$TMP_DIR/staged_search"
    stage_plugin "$TMP_DIR/search.tgz" "$STAGED_SEARCH"

    SEARCH_PLUGIN_NAME="$(read_plugin_id_from_path "$STAGED_SEARCH")"

    # disable current search plugin before swap
    "$OPENCLAW_BIN" plugins disable "$SEARCH_PLUGIN_NAME" >/dev/null 2>&1 || true

    # backup existing search install (if any)
    _SEARCH_BACKUP_DIR=""
    if _SEARCH_BACKUP_DIR="$(backup_dir "$SEARCH_TARGET_DIR")"; then
      log "backed up existing search install to $_SEARCH_BACKUP_DIR"
    fi

    # write state so parent can read it for rollback
    printf "SEARCH_BACKUP_DIR=%s\nSEARCH_PLUGIN_NAME_SAVED=%s\n" \
      "$_SEARCH_BACKUP_DIR" "$SEARCH_PLUGIN_NAME" >"$SEARCH_STATE_FILE"

    # atomic swap
    mkdir -p "$(dirname "$SEARCH_TARGET_DIR")"
    mv "$STAGED_SEARCH" "$SEARCH_TARGET_DIR"

    "$OPENCLAW_BIN" plugins install -l "$SEARCH_TARGET_DIR" >/dev/null 2>&1 || true
    "$OPENCLAW_BIN" plugins enable "$SEARCH_PLUGIN_NAME"

    # search plugin install succeeded
    log "search plugin installed successfully"
    cleanup_old_backups "$SEARCH_TARGET_DIR" "$_SEARCH_BACKUP_DIR"
    if [ -n "$_SEARCH_BACKUP_DIR" ] && [ -d "$_SEARCH_BACKUP_DIR" ]; then
      rm -rf "$_SEARCH_BACKUP_DIR"
      log "removed search backup: $_SEARCH_BACKUP_DIR"
    fi

    # mark success so parent knows no rollback needed
    printf "\nSEARCH_OK=1\n" >>"$SEARCH_STATE_FILE"
  )
  search_exit=$?

  # read back state from subshell for rollback if needed
  if [ -f "$SEARCH_STATE_FILE" ]; then
    eval "$(grep -E '^(SEARCH_BACKUP_DIR|SEARCH_PLUGIN_NAME_SAVED|SEARCH_OK)=' "$SEARCH_STATE_FILE" || true)"
  fi

  if [ "$search_exit" -ne 0 ]; then
    SEARCH_INSTALL_FAILED="1"
    # if subshell wrote state but didn't mark OK, we need rollback
    if [ -n "$SEARCH_BACKUP_DIR" ] && [ -d "$SEARCH_BACKUP_DIR" ] && [ "${SEARCH_OK:-0}" != "1" ]; then
      SEARCH_ROLLBACK_NEEDED="1"
    fi
    log_warn "search plugin install failed; main plugin is still working"
  fi
fi

log "restarting gateway"
"$OPENCLAW_BIN" gateway restart >/dev/null 2>&1 || true

if [ "$SEARCH_INSTALL_FAILED" = "1" ]; then
  log "done (main plugin ok, search plugin failed)"
  exit 1
else
  log "done"
fi
