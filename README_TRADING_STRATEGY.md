# نظام تداول متعدد الوكلاء (Multi-Agent Trading System)

هذا الفرع يحتوي على هيكل أوّلي لاستراتيجية “Mean Reversion / Reversal” بنسختين:
1. نسخة Voting (مؤشرات + مصوتين).
2. نسخة Pure Agent (بدون RSI/EMA/ATR، تعتمد أحداث السعر وهيكلة السوق).

## 1. المجلدات

| مجلد | وصف |
|------|-----|
| config/ | ملفات إعداد (مخاطرة، تنفيذ، أوزان، Pure Mode) |
| engine/agents/ | الوكلاء (Agents) |
| engine/core/ | حافلة الأحداث وأساسيات التشغيل |
| engine/utils/ | أدوات مساعدة (توقيع، حماية أوامر...) |
| engine/models/ | (مكان لاحق للنماذج، مثل Quantile EAE) |
| scripts/ | سكربتات تدريب / وسم بيانات (Labeling) / تشغيل |
| dashboard/ | (يمكن لاحقاً إضافة لوحات Streamlit) |

## 2. وضعا التشغيل

### أ. Voting Mode (main_voting.py)
- يعتمد على مصوتين (Deviation, RSI, Divergence, …).
- يدمج نموذج احتمالي (يمكن إضافته لاحقاً).

### ب. Pure Agent Mode (main_pure.py)
- لا يستخدم مؤشرات كلاسيكية.
- إشارات تبنى من: اندفاعات، كسور كاذبة، تسلسل شموع، إرهاق، توازن، جلسات، buckets للتقلب.

## 3. تدفق الإشارة (مبسّط)

```
RAW -> Features/Events -> Signal Proposal -> Stop/Targets -> Risk -> Position Plan -> Execution -> Trail -> Performance
```

## 4. خطوات سريعة للتشغيل (محاكاة محلية)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_strategy.txt

# وضع التصويت (Skeleton)
python main_voting.py

# وضع Pure Agent
python main_pure.py
```

(الكود هنا هيكلي — ستحتاج دمج مصادر بيانات حقيقية (WebSocket) وطبقة تنفيذ API للبورصة.)

## 5. رفع إلى Production (مستقبلاً)

1. إضافة مفاتيح API في .env (لا ترفعها للمستودع).
2. تفعيل ExecutionAgent الحقيقي.
3. ضبط مخاطر منخفضة أولاً (max_risk_pct صغير).
4. مراقبة: drawdown / rejection rate / slippage.

## 6. ملاحظات

- الملفات الحالية لا تُنفِّذ تداول فعلي، بل إطار مرن للتوسعة.
- يمكن إضافة نموذج EAE Quantile في `engine/models/` لاحقاً.
- استخدم `scripts/labeling_script.py` لتحضير بيانات تدريب.

## 7. تحذير مخاطر

tداول آلي محفوف بالمخاطر وقد يؤدي إلى خسائر. استخدم Testnet أولاً.

---

© استراتيجية تجريبية – خصصها وفق احتياجاتك.