# Multi-Agent Reverse Trading System (Strategy Draft v4.1)

## التحديث v4.1
- تشغيل على جميع الأزواج (ديناميكياً) عبر UniverseAgent مع تصنيف Tiers.
- مخاطرة ثابتة لكل صفقة = 1% من رأس المال (Equity) (لا مخاطرة ديناميكية حالياً لزيادة الوضوح والتحكم).
- تحديث RiskAgent و حذف الاعتماد على مخاطرة احتمالية متذبذبة.
- إضافة فلترة سيولة (حجم / سبريد) واستبعاد الرموز منخفضة الجودة.
- دعم حدود التعرض حسب الفئة + التحكم في إجمالي التعرض.
- تمهيد لإدخال VotingSignalAgent لاحقاً بدون تغيير جوهر الهيكل.

## تنبيه
هذه الشفرة لأغراض تعليمية. لا تستخدمها في حساب حقيقي قبل:
1. باك تست شامل متعدد الفترات.
2. تشغيل Testnet ≥ 300 صفقة.
3. مراقبة Drawdown & Slippage.
4. مراجعة المخاطر البشرية.

---
## الفكرة
استراتيجية Mean Reversion (Reverse / Exhaustion) تدخل عندما يبتعد السعر عن متوسطه (EMA50) بعدد ATR مع حالات تشبّع (RSI) وفلتر نظام (Regime) يسمح بظروف الانعكاس.

## جديد النسخة
| مجال | تغيير |
|------|-------|
| المخاطرة | ثابتة 1% لكل صفقة (RiskDollar = Equity * 0.01) |
| Universe | إضافة Agent يجلب الرموز ويصنفها (Tier1..Tier4) ويحدّد المسموح |
| التعرض | إجمالي التعرض الكلي MaxTotalExposure + تعرض للفئة |
| التنفيذ | كما هو (مخطط للتطوير لاحقاً: أوامر فعلية + TP/SL شرطية) |
| التريل | نفس مراحل Protect / Expand / Harvest لكن يمكن تعديل α لاحقاً |

## الحساب الأساسي للحجم
``
RiskDollar = Equity * 0.01
StopDistancePct = |Entry - Stop| / Entry
Notional = RiskDollar / StopDistancePct
Quantity = Notional / Entry
``
تُرفض الصفقة إذا StopDistancePct خارج [min_stop_pct, max_stop_pct] أو R الأول < min_r_expectancy.

## UniverseAgent (مبسّط)
- يجلب قائمة رموز (تحتاج دمج REST لاحقاً) – حالياً نموذجية.
- يطبق فلاتر:
  - حجم 24h ≥ volume_24h_min
  - Spread تقديري ≤ spread_max_pct
  - استبعاد رموز محددة بالأنماط
- يحدد Tier ثم ينشر SYMBOLS_UPDATE → DataAgent يحدث قائمته.

## خريطة التدفق
``
RAW_TICK -> FEATURE_VECTOR -> REGIME_STATE -> SIGNAL_PROPOSAL -> MAE_ESTIMATE -> STOP_TARGET_PLAN -> FIXED_RISK_PLAN (1%) -> POSITION_PLAN -> EXEC_STATUS -> (Trail / Performance / Governance / Drift)
``

## TODO لاحقاً
- VotingSignalAgent + Weights per symbol
- Quantile EAE (0.5 / 0.75 / 0.9)
- Correlation / Cluster Exposure
- Slippage Model + تكامل دفتر أوامر حقيقي
- Persistence + Model Registry
- FastAPI / Prometheus Monitoring

## تشغيل سريع (محاكاة)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
``

## ملف Config
راجع `config/agents.yaml` للتعديلات (risk.fixed_per_trade_pct = 0.01 + تفعيل universe).

## تحذير أخير
لا تستخدم أي مفاتيح API حقيقية هنا. جرّب على Testnet أولاً.