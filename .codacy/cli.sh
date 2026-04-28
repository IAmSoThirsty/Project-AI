#!/usr/bin/env bash

set -euo pipefail

fatal() {
    echo "$*" >&2
    exit 1
}

bin_name="codacy-cli-v2"
os_name="$(uname -s)"
arch="$(uname -m)"

case "$arch" in
    x86_64) arch="amd64" ;;
    x86) arch="386" ;;
    aarch64|arm64) arch="arm64" ;;
esac

if [ -z "${CODACY_CLI_V2_TMP_FOLDER:-}" ]; then
    if [ "$os_name" = "Linux" ]; then
        CODACY_CLI_V2_TMP_FOLDER="$HOME/.cache/codacy/codacy-cli-v2"
    elif [ "$os_name" = "Darwin" ]; then
        CODACY_CLI_V2_TMP_FOLDER="$HOME/Library/Caches/Codacy/codacy-cli-v2"
    else
        CODACY_CLI_V2_TMP_FOLDER=".codacy-cli-v2"
    fi
fi

version_file="$CODACY_CLI_V2_TMP_FOLDER/version.yaml"

get_version_from_yaml() {
    if [ -f "$version_file" ]; then
        local version
        version="$(grep -o 'version: *"[^"]*"' "$version_file" | cut -d'"' -f2 || true)"
        if [ -n "$version" ]; then
            echo "$version"
            return 0
        fi
    fi
    return 1
}

handle_rate_limit() {
    local response="$1"
    if echo "$response" | grep -q "API rate limit exceeded"; then
        fatal "Error: GitHub API rate limit exceeded. Please try again later"
    fi
}

get_latest_version() {
    local response
    if [ -n "${GH_TOKEN:-}" ]; then
        response="$(curl -Lq --header "Authorization: Bearer $GH_TOKEN" "https://api.github.com/repos/codacy/codacy-cli-v2/releases/latest" 2>/dev/null || true)"
    else
        response="$(curl -Lq "https://api.github.com/repos/codacy/codacy-cli-v2/releases/latest" 2>/dev/null || true)"
    fi

    handle_rate_limit "$response"
    local version
    version="$(echo "$response" | grep -m 1 tag_name | cut -d'"' -f4 || true)"
    if [ -z "$version" ]; then
        fatal "Error: Unable to resolve latest Codacy CLI version"
    fi
    echo "$version"
}

download_file() {
    local url="$1"

    echo "Downloading from URL: ${url}"
    if command -v curl >/dev/null 2>&1; then
        curl -# -LS "$url" -O
    elif command -v wget >/dev/null 2>&1; then
        wget "$url"
    else
        fatal "Error: Could not find curl or wget, please install one."
    fi
}

download() {
    local url="$1"
    local output_folder="$2"

    (cd "$output_folder" && download_file "$url")
}

download_cli() {
    local suffix
    suffix="$(echo "$os_name" | tr '[:upper:]' '[:lower:]')"

    local bin_folder="$1"
    local bin_path="$2"
    local version="$3"

    if [ ! -f "$bin_path" ]; then
        echo "📥 Downloading CLI version $version..."

        local remote_file
        remote_file="codacy-cli-v2_${version}_${suffix}_${arch}.tar.gz"
        local url
        url="https://github.com/codacy/codacy-cli-v2/releases/download/${version}/${remote_file}"

        download "$url" "$bin_folder"
        tar xzfv "${bin_folder}/${remote_file}" -C "${bin_folder}"
    fi
}

if [ -n "${CODACY_CLI_V2_VERSION:-}" ] && [ "${1:-}" = "update" ]; then
    echo "⚠️  Warning: Performing update with forced version $CODACY_CLI_V2_VERSION"
    echo "    Unset CODACY_CLI_V2_VERSION to use the latest version"
fi

if [ ! -f "$version_file" ] || [ "${1:-}" = "update" ]; then
    echo "ℹ️  Fetching latest version..."
    version="$(get_latest_version)"
    mkdir -p "$CODACY_CLI_V2_TMP_FOLDER"
    echo "version: \"$version\"" > "$version_file"
fi

if [ -n "${CODACY_CLI_V2_VERSION:-}" ]; then
    version="$CODACY_CLI_V2_VERSION"
else
    version="$(get_version_from_yaml)"
fi

if [ -z "$version" ]; then
    fatal "Error: Invalid Codacy CLI version"
fi

bin_folder="${CODACY_CLI_V2_TMP_FOLDER}/${version}"
mkdir -p "$bin_folder"
bin_path="$bin_folder/$bin_name"

download_cli "$bin_folder" "$bin_path" "$version"
chmod +x "$bin_path"

if [ "$#" -eq 1 ] && [ "$1" = "download" ]; then
    echo "Codacy cli v2 download succeeded"
else
    "$bin_path" "$@"
fi