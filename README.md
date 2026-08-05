# 🐍 كامورو — Camorro v2.0

**وكيل اختبار الاختراق بالذكاء الاصطناعي — يعمل محليًا 100% على جهازك**

كامورو مساعد هكر ذكي مبني على نموذج LLM محلي (Ollama)، يتكلم الدارجة المغربية وجميع اللغات، يحلل كل شيء، وينفذ أدوات الاختراق بنفسه خطوة بخطوة، ويكتب سكريبتات كاملة جاهزة للعمل. لا يحتاج إنترنت إجباري، وبياناتك لا تغادر جهازك أبدًا.

---

## ✨ المميزات

- 🤖 يعتمد على نموذج LLM محلي (Ollama) — يعمل بدون إنترنت
- 🗣️ يرد بالدارجة المغربية / العربية / الإنجليزية / الفرنسية حسب لغة المستخدم
- 🛠️ **14 أداة** تغطي دورة الاختراق الكاملة: استطلاع، فحص، استغلال، بحث عن ثغرات
- 🔍 بحث مباشر في قاعدة **NVD** الرسمية (ثغرات CVE) + **Exploit-DB** (أكواد استغلال جاهزة)
- 📁 يقرأ ويكتب الملفات في مساحة عمل آمنة (workspace)
- 🌐 واجهة ويب عربية RTL + واجهة طرفية (CLI)
- 🛡️ نظام حماية مزدوج: وضع عادي محمي + وضع `--unrestricted` كامل بدون قيود
- 📊 يستخرج ملخصًا منظمًا للمنافذ المفتوحة من مخرجات nmap تلقائيًا
- 🧠 يدعم نماذج التفكير العميق (deepseek-r1) مع تنظيف تلقائي لوسوم التفكير

---

## 📦 التثبيت

### 1. ثبّت المتطلبات الأساسية

```bash
# Python 3.10+ (موجود غالبًا)
python3 --version

# Ollama — محرك النماذج المحلي
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. حمّل نموذجًا قويًا للأدوات

```bash
# 🔥 الأفضل لتنفيذ الأدوات وكتابة السكريبتات بدون رفض
ollama pull dolphin-llama3:8b

# بدائل حسب قدرات جهازك:
# ollama pull qwen2.5:14b      # ممتاز للعربية وتعدد اللغات (8GB+ رام)
# ollama pull dolphin-mistral:7b   # خفيف وسريع (4-8GB رام)
# ollama pull qwen2.5:7b       # لجهاز ضعيف
```

### 3. ثبّت أدوات الاختراق

```bash
chmod +x install_tools.sh
./install_tools.sh
```

أو يدويًا على Kali:

```bash
sudo apt update -y
sudo apt install -y nmap whois dnsutils dnsenum masscan netcat-openbsd curl wget git \
    sqlmap exploitdb hydra john hashcat metasploit-framework nikto gobuster wpscan \
    enum4linux smbclient seclists dirb
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/ffuf/ffuf/v2@latest
sudo cp ~/go/bin/{subfinder,nuclei,httpx,ffuf} /usr/local/bin/
nuclei -update-templates
```

### 4. ثبّت حزم بايثون

```bash
pip3 install -r requirements.txt
# أو:
pip3 install flask requests python-dotenv
```

---

## 🚀 التشغيل

### الواجهة الطرفية (CLI)

```bash
# الوضع العادي (مع حماية النظام)
python3 -m camorro.main --model dolphin-llama3:8b

# الوضع الكامل بدون قيود 🔥
python3 -m camorro.main --model dolphin-llama3:8b --unrestricted --yes
```

### خادم الويب

```bash
# تشغيل خادم الويب العربي
python3 -m camorro.server --model dolphin-llama3:8b

# خادم ويب بالوضع الكامل
python3 -m camorro.server --model dolphin-llama3:8b --unrestricted

# ثم افتح المتصفح على:
# http://127.0.0.1:5000
```

---

## ⚙️ الأوضاع الثلاثة

| الوضع | الأمر | السلوك |
|---|---|---|
| **عادي** | بدون وسائط إضافية | يمنع أوامر تدمير النظام (rm -rf /, mkfs, dd...) والملفات محصورة في مجلد workspace |
| **تأكيد تلقائي** | `--yes` | يسمح بكل الأوامر عدا أنماط التدمير، بدون طلب تأكيد |
| **كامل 🔥** | `--unrestricted` | لا قيود إطلاقًا: أي أمر، أي مسار، أي ملف، بدون حجب |

---

## 🧰 الأدوات الـ14

| الفئة | الأداة | الوظيفة |
|---|---|---|
| تنفيذ | `run_command` | تنفيذ أي أمر على الطرفية (nmap, sqlmap, hydra, curl, python, msfconsole...) |
| ملفات | `read_file` | قراءة محتوى ملف من مساحة العمل |
| ملفات | `write_file` | كتابة سكريبت/تقرير/ملف في مساحة العمل |
| استطلاع | `subdomain_enum` | تعداد النطاقات الفرعية (subfinder) مع فحص عميق recursive |
| استطلاع | `dns_lookup` | تحليل DNS كامل: A, AAAA, MX, TXT, NS, SOA, CNAME + اختبار Zone Transfer |
| استطلاع | `whois_lookup` | جلب معلومات whois لنطاق أو IP |
| استطلاع | `http_probe` | اكتشاف المواقع الحية: الحالة، العنوان، التقنيات |
| فحص | `nmap_scan` | فحص المنافذ والخدمات مع اكتشاف الإصدارات (-sC -sV) وفحص شامل (-A -p-) |
| فحص | `dir_fuzz` | اكتشاف المسارات والملفات المخفية (ffuf) مع دعم الامتدادات |
| استغلال | `sqlmap_run` | فحص واستغلال حقن SQL تلقائيًا |
| استغلال | `web_scan` | فحص ثغرات الموقع (nuclei) مع كل القوالب واختيار مستوى الخطورة |
| استغلال | `http_request` | طلب HTTP مخصص بتحكم كامل بالهيدرز والكوكيز والبيانات |
| بحث ثغرات | `cve_search` | البحث في قاعدة NVD الرسمية عن ثغرات CVE لأي برنامج/إصدار |
| بحث ثغرات | `exploit_search` | البحث عن أكواد استغلال جاهزة في Exploit-DB (searchsploit) |

---

## 💬 أمثلة استخدام

```bash
# استطلاع كامل لهدف
> امسحلي نطاق example.com وجيبلي كل النطاقات الفرعية والمنافذ المفتوحة

# فحص موقع
> فحص الموقع https://target.com بالـ nuclei وجيبلي الثغرات الحرجة

# بحث عن ثغرات
> ابحثلي عن ثغرات CVE في Apache 2.4.49 وجيبلي أكواد استغلال جاهزة

# حقن SQL
> جرّب sqlmap على https://target.com/page?id=1 واستخرج قواعد البيانات

# سكريبت مخصص
> اكتبلي سكريبت Python يفحص حقن SQL على كل معاملات الموقع
```

---

## 🔧 متغيرات البيئة (اختياري)

```bash
export CAMORRO_MODEL="dolphin-llama3:8b"        # النموذج الافتراضي
export CAMORRO_LLM_URL="http://localhost:11434"  # رابط Ollama أو خادم OpenAI
export CAMORRO_API_KEY="sk-..."                  # فقط لخوادم OpenAI API
```

---

## 📁 بنية المشروع

```
camorro/
├── camorro/
│   ├── __init__.py          # تعريف الحزمة
│   ├── main.py              # الواجهة الطرفية (CLI)
│   ├── server.py            # خادم الويب (Flask)
│   ├── agent.py             # حلقة التفكير والتنفيذ
│   ├── llm.py               # الاتصال بالنموذج (Ollama/OpenAI)
│   ├── prompts.py           # تعليمات النظام + مخطط الأدوات الـ14
│   ├── utils.py             # دوال مساعدة (تنفيذ، تحليل، JSON)
│   └── tools/
│       ├── __init__.py      # تجميع المنفذ الكامل
│       ├── executor.py      # الأساس: أوامر + ملفات + نظام الحماية
│       ├── recon.py         # الاستطلاع: subfinder, dig, whois, httpx
│       ├── scanning.py      # الفحص: nmap, ffuf
│       ├── exploitation.py  # الاستغلال: sqlmap, nuclei, HTTP
│       └── vulnsearch.py    # البحث: NVD + Exploit-DB
├── web/
│   └── index.html           # واجهة عربية RTL كاملة
├── requirements.txt
├── install_tools.sh
└── README.md
```

---

## 🧠 النماذج المدعومة

| النموذج | الحجم | التوصية |
|---|---|---|
| `dolphin-llama3:8b` | 4.7GB | ✅ الأفضل لتنفيذ الأدوات وكتابة السكريبتات بدون رفض |
| `qwen2.5:14b` | 9GB | ممتاز للعربية وتعدد اللغات |
| `dolphin-mistral:7b` | 4.1GB | خفيف وسريع للأجهزة الضعيفة |
| `qwen2.5:7b` | 4.7GB | بديل خفيف متعدد اللغات |
| `dolphin-mixtral:8x7b` | 26GB | الأقوى — يحتاج 48GB+ رام |
| `deepseek-r1:7b` | 4.7GB | تفكير عميق خطوة بخطوة (مع تنظيف تلقائي لوسوم التفكير) |

---

## ⚠️ ملاحظات مهمة

- 🎯 الأداة مخصصة لاختبار **الأصول المصرح بها فقط**: اختبار الاختراق، تقييم الثغرات، البحث الأكاديمي، والتدريب.
- 🛡️ الوضع العادي يحميك من الأوامر المدمرة للنظام — استعمل `--unrestricted` فقط عندما تكون متأكدًا مما تفعله.
- 🌐 خادم الويب يرتبط افتراضيًا بـ `127.0.0.1` — لا تعرضه على الشبكة العامة بدون جدار حماية.
- ⏱️ بعض الفحوصات (nmap شامل، sqlmap، nuclei) تأخذ وقتًا طويلًا — الصبر مطلوب.
- 🔄 الأدوات الخارجية (subfinder, nuclei, httpx, ffuf) يجب تثبيتها — الأداة تخبرك إذا كان أي منها ناقصًا.

---

## 🛠️ حل المشاكل الشائعة

| المشكلة | الحل |
|---|---|
| `Connection refused` على 11434 | تأكد أن Ollama شغال: `ollama serve` |
| النموذج ما يجاوبش بالعربية | حمّل qwen2.5:14b: `ollama pull qwen2.5:14b` |
| `subfinder not found` | شغّل `install_tools.sh` أو ثبّته يدويًا |
| الأدوات بطيئة | قلل `--iterations` أو استعمل فحوصات أقل عمقًا |
| الذاكرة ممتلئة | استعمل نموذج أصغر: `ollama pull dolphin-mistral:7b` |

---

## 📄 الرخصة

مشروع مفتوح المصدر للاستخدام التعليمي والأمني المصرح به. المسؤولية على المستخدم في تطبيق الاستخدام القانوني.

---

**صُنع بحب 🐍 — كامورو جاهز يساعدك في كل فحوصاتك الأمنية!**
