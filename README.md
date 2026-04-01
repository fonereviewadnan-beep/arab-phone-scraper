# 📱 Arab Phone Prices Scraper

سكريبت بايثون يسحب أسعار الهواتف من مواقع عربية متعددة ويحفظها في ملف JSON واحد جاهز للاستخدام في ووردبريس.

---

## ✨ المميزات

| الميزة | التفاصيل |
|--------|----------|
| 🌍 الدول | 17+ دولة عربية (مصر، السعودية، الإمارات، المغرب، الأردن، العراق، سوريا…) |
| 🛒 المصادر | Jumia · Noon · OpenSooq |
| 📱 الهواتف | 40+ هاتف (Samsung, iPhone, Honor, Xiaomi, OPPO, Realme…) |
| 🔄 التحديث | تلقائي يوميًا عبر GitHub Actions |
| 📄 المخرج | ملف `prices_arab.json` مرتب وجاهز |
| 🛡️ الحماية | User-Agent rotation + delays لتجنب الحظر |
| 🧠 ذكي | يفلتر الإكسسوارات تلقائيًا (كفرات، شواحن، سماعات) |

---

## 📁 هيكل المشروع

```
arab-phone-scraper/
├── scraper.py                  ← الكود الرئيسي
├── requirements.txt            ← المكتبات المطلوبة
├── prices_arab.json            ← الملف الناتج (يتحدث تلقائيًا)
├── README.md                   ← التعليمات
└── .github/
    └── workflows/
        └── daily-scrape.yml    ← جدولة GitHub Actions
```

---

## 🚀 التشغيل المحلي

```bash
# 1. تثبيت المكتبات
pip install -r requirements.txt

# 2. تشغيل السكريبت
python scraper.py
```

سيُنتج ملف `prices_arab.json` في نفس المجلد.

---

## 📄 شكل الـ JSON الناتج

```json
[
  {
    "phone_name": "Honor Magic 6 Pro",
    "price_eg": "35999",
    "price_sa": "4499",
    "price_ae": "3999",
    "price_sy": "15900000",
    "price_ma": "",
    "last_updated": "2026-04-01"
  }
]
```

- `price_XX` → السعر بالعملة المحلية (فارغ إذا مش موجود)
- `last_updated` → تاريخ آخر تحديث

---

## ⚙️ التشغيل التلقائي (GitHub Actions)

1. ارفع المشروع على GitHub
2. الـ workflow موجود في `.github/workflows/daily-scrape.yml`
3. يشتغل تلقائيًا كل يوم الساعة 6 صباحًا UTC
4. ممكن تشغله يدويًا من تبويب **Actions** → **Run workflow**

> ⚠️ تأكد إن **Settings → Actions → General → Workflow permissions** مضبوطة على **Read and write**

---

## ➕ إضافة هاتف جديد

افتح `scraper.py` وأضف اسم الهاتف في قائمة `PHONES_TO_TRACK`:

```python
PHONES_TO_TRACK = [
    "Samsung Galaxy S24 Ultra",
    "iPhone 15 Pro Max",
    # أضف هنا ↓
    "Samsung Galaxy S25 Ultra",
]
```

---

## 🌍 الدول المدعومة

| الكود | الدولة | العملة | Jumia | Noon | OpenSooq |
|-------|--------|--------|:-----:|:----:|:--------:|
| eg | مصر | EGP | ✅ | ✅ | ✅ |
| sa | السعودية | SAR | — | ✅ | ✅ |
| ae | الإمارات | AED | — | ✅ | ✅ |
| ma | المغرب | MAD | ✅ | — | ✅ |
| dz | الجزائر | DZD | ✅ | — | ✅ |
| sy | سوريا | SYP | — | — | ✅ |
| jo | الأردن | JOD | — | — | ✅ |
| iq | العراق | IQD | — | — | ✅ |
| kw | الكويت | KWD | — | — | ✅ |
| bh | البحرين | BHD | — | — | ✅ |
| om | عمان | OMR | — | — | ✅ |
| ly | ليبيا | LYD | — | — | ✅ |
| tn | تونس | TND | — | — | ✅ |
| sd | السودان | SDG | — | — | ✅ |
| lb | لبنان | LBP | — | — | ✅ |
| ps | فلسطين | ILS | — | — | ✅ |
| ye | اليمن | YER | — | — | ✅ |

---

## 📝 ملاحظات

- **Noon** يستخدم JavaScript بشكل كبير → السكريبت يحاول API الداخلي + `__NEXT_DATA__` + JSON-LD
- **OpenSooq** عنده حماية من البوتات → النتائج ممكن تكون محدودة في بعض الدول
- **Jumia** متاح فقط في مصر والمغرب والجزائر (من الدول العربية)
- السكريبت يحتفظ بالأسعار القديمة إذا الـ run الجديد ما لقى سعر

---

## 📜 الرخصة

MIT License
