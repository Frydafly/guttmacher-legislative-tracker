# Tracking Status Views Guide

## Overview
We have **5 specialized views** for understanding what fields were tracked when across the 21 years (2002-2023) of historical data.

## The Views

### 1. `tracking_completeness_matrix` ⭐ **RECOMMENDED**
**Purpose**: Visual matrix showing field tracking status by year
**Format**: ✅ = Tracked, ⚠️ = Partially tracked, ❌ = Not tracked

```sql
SELECT data_year, bill_type_tracked, introduced_date_tracked, 
       contraception_tracked, period_products_tracked, incarceration_tracked
FROM `tracking_completeness_matrix` 
ORDER BY data_year;
```

**Sample Output**:
```
2002: BillType=❌ IntroDate=❌ Contraception=✅ Period=❌ Incarceration=❌
2006: BillType=✅ IntroDate=❌ Contraception=❌ Period=❌ Incarceration=❌
2016: BillType=✅ IntroDate=✅ Contraception=✅ Period=❌ Incarceration=❌
2019: BillType=✅ IntroDate=⚠️ Contraception=✅ Period=✅ Incarceration=✅
2023: BillType=✅ IntroDate=✅ Contraception=✅ Period=✅ Incarceration=✅
```

### 2. `realistic_field_tracking_by_year`
**Purpose**: Shows realistic tracking patterns accounting for FALSE defaults
**Use Case**: Understanding actual field availability vs defaulted values

```sql
SELECT data_year, contraception_tracking_status, period_products_tracking_status,
       incarceration_tracking_status, intent_tracking_status
FROM `realistic_field_tracking_by_year` 
ORDER BY data_year;
```

### 3. `field_tracking_completeness_by_year`
**Purpose**: Detailed percentage tracking by field and year
**Use Case**: Precise tracking percentages for each field

```sql
SELECT data_year, contraception_tracking_pct, period_products_tracking_pct, 
       incarceration_tracking_pct, intent_tracking_pct
FROM `field_tracking_completeness_by_year` 
ORDER BY data_year;
```

### 4. `corrected_policy_tracking`
**Purpose**: Policy fields with proper NULL patterns (intermediate view)
**Use Case**: Getting corrected field values for analysis

```sql
SELECT data_year, contraception_corrected, period_products_corrected, 
       incarceration_corrected, positive_corrected
FROM `corrected_policy_tracking` 
WHERE data_year = 2023;
```

### 5. `bills_with_consolidated_intent` 
**Purpose**: Adds consolidated intent field and tracking indicators
**Use Case**: Using single intent field instead of separate booleans

```sql
SELECT data_year, intent_consolidated, intent_tracking_era,
       period_products_tracking_status, incarceration_tracking_status
FROM `bills_with_consolidated_intent` 
WHERE data_year >= 2019;
```

## Key Tracking Patterns

### Core Fields (Always Available)
- `state`: ✅ All years
- `bill_number`: ✅ All years  
- `description`: ✅ All years

### Evolved Fields
- `bill_type`: ❌ 2002-2005, ✅ 2006+
- `introduced_date`: ❌ 2002-2015, ✅ 2016+
- `internal_summary`: ❌ 2002-2018, ✅ 2019+

### Status Fields
- `introduced`, `enacted`, `dead`, `pending`: ❌ 2002-2005, ✅ 2006+

### Intent Fields
- `positive`, `neutral`: ❌ 2002-2005, ✅ 2006+
- `restrictive`: ❌ 2002-2008, ✅ 2009+
- `intent_consolidated`: ❌ 2002-2005, ✅ 2006+

### Policy Category Fields
- `abortion`: ✅ All years
- `contraception`: ✅ 2002-2005, ❌ 2006-2008, ✅ 2009+
- `minors`: ⚠️ 2002-2009, ✅ 2010+
- `sex_education`: ❌ 2002-2005, ✅ 2006+
- `emergency_contraception`: ❌ 2002-2008, ✅ 2009+
- `pregnancy`: ❌ 2002-2009, ✅ 2010+
- `period_products`: ❌ 2002-2018, ✅ 2019+
- `incarceration`: ❌ 2002-2018, ✅ 2019+

## Common Use Cases

### 1. Check what fields are available for a specific year
```sql
SELECT * FROM `tracking_completeness_matrix` WHERE data_year = 2016;
```

### 2. Find when a field started being tracked
```sql
SELECT data_year, period_products_tracked 
FROM `tracking_completeness_matrix` 
WHERE period_products_tracked = '✅' 
ORDER BY data_year LIMIT 1;
```

### 3. Get percentage tracking for contraception over time
```sql
SELECT data_year, contraception_tracking_pct 
FROM `field_tracking_completeness_by_year` 
ORDER BY data_year;
```

### 4. Use consolidated intent for analysis
```sql
SELECT intent_consolidated, COUNT(*) as bills
FROM `bills_with_consolidated_intent` 
WHERE data_year = 2023 
GROUP BY intent_consolidated;
```

## Important Notes

### NULL vs FALSE Distinction
- **NULL**: Field was not tracked that year
- **FALSE**: Field was tracked but marked as negative/not applicable
- **TRUE**: Field was tracked and marked as positive/applicable

### Data Quality Evolution
- **2002-2005**: Basic tracking, many fields NULL
- **2006-2008**: Modern status tracking, contraception gap
- **2009-2015**: Full intent tracking, contraception resumed
- **2016-2018**: Date tracking added
- **2019-2023**: Emerging categories (period products, incarceration)

### Best Practices
1. **Always check tracking status** before analysis
2. **Use `tracking_completeness_matrix`** for quick overview
3. **Use `comprehensive_bills_authentic`** for corrected data
4. **Consider tracking evolution** when interpreting trends
5. **Use `intent_consolidated`** instead of separate boolean fields

---

**Quick Reference**: For most use cases, start with `tracking_completeness_matrix` to understand what's available, then use `comprehensive_bills_authentic` for actual analysis.