#!/bin/bash
# ============================================================
# install_tools.sh — تثبيت كل أدوات كامورو (Debian/Kali/Ubuntu)
# ============================================================
set -e

echo "[+] تحديث الحزم..."
sudo apt update -y && sudo apt upgrade -y

echo "[+] أدوات الفحص والاستطلاع..."
sudo apt install -y nmap whois dnsutils dnsenum masscan netcat-openbsd \
    curl wget git python3 python3-pip build-essential

echo "[+] أدوات Go (subfinder, nuclei, httpx, ffuf)..."
if ! command -v go &>/dev/null; then
    echo "[!] ثبّت Go أولاً من https://go.dev/dl/ ثم أعد التشغيل"
    exit 1
fi
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/ffuf/ffuf/v2@latest
sudo cp ~/go/bin/{subfinder,nuclei,httpx,ffuf} /usr/local/bin/ 2>/dev/null || true

echo "[+] أدوات الاستغلال..."
sudo apt install -y sqlmap exploitdb hydra john hashcat metasploit-framework \
    nikto gobuster wpscan enum4linux smbclient seclists dirb

echo "[+] تحديث قوالب nuclei..."
nuclei -update-templates || true

echo "[+] تثبيت حزم بايثون..."
pip3 install -r requirements.txt

echo ""
echo "[✔] تم تثبيت كل شيء!"
echo "    شغّل: python3 -m camorro.main --model dolphin-llama3:8b --unrestricted"
