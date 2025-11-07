# Root Cause Analysis: Why French Text Remains in Translated PDFs

## Executive Summary

The translated PDFs contain **significant amounts of French text** despite having a dictionary with 4,338 translation entries. The problem has **two root causes**:

1. **Faulty translations in dictionary** (70+ entries translate French→French, i.e., no actual translation)
2. **Mixed/corrupted translations** (Franglais - partially translated hybrid sentences)

## Detailed Findings

### 1. Dictionary Contains French→French "Translations"

**Problem:** The growing dictionary (`method9_data/translations.json`) contains 70+ entries where French text "translates" to itself.

**Examples:**
```
"CADRE EN ACIER" -> "CADRE EN ACIER"  (should be "STEEL FRAME")
"VOIR 5 / A-171b" -> "VOIR 5 / A-171b"  (should be "SEE 5 / A-171b")
"Porte 221a" -> "Porte 221a"  (should be "Door 221a")
"SDK et associés inc." -> "SDK et associés inc."  (company name, probably OK)
"POUR LES TYPES DE SOFFITES EXTÉRIEURS : VOIR FEUILLE A-501." -> [same]
"COFFRET DE ROBINET AVEC MANOMÈTRES (NON EXHAUSTIF, VOIR DOCUMENTS" -> [same]
```

**Impact:** When the translation script encounters these texts:
- It finds them in the dictionary ✓
- It "translates" them (but gets back the same French text)
- It replaces French with... French
- Result: French remains in final PDF

### 2. Corrupted/Mixed Translations (Franglais)

**Problem:** Many long sentences in the dictionary are partially translated, creating hybrid French-English gibberish.

**Examples from A-001:**
```
"NOTE : L'IDENTIFICATION OFE TYPE...) INDICATES QU'UN OR PLUSIEURS NUMBERS ARE ATTRIBUÉS"
  - Mix of French and English
  - "OFE" (corrupted), "INDICATES" (EN), "QU'UN" (FR), "OR" (EN), "PLUSIEURS" (FR)

"ALL THE DIMENSIONS BY RELATION À L'EXISTANT ARE APPROXIMATE, ELLES ARE"
  - "ALL THE DIMENSIONS" (EN), "À L'EXISTANT" (FR), "ELLES" (FR)

"AVANT OF PROCÉDER À L'EXÉCUTION OF THE TRAVAUX, L'ENTREPRENEUR MUST VERIFY"
  - Random mix throughout

"APPAREIL D'ÉCLAIRAGE ENCASTRÉ NOTN EXHAUSTIF, SEE DOCUMENTS OF ENGINEERING"
  - "APPAREIL D'ÉCLAIRAGE ENCASTRÉ" (FR), "NOTN" (corrupted), "SEE DOCUMENTS" (EN)
```

**Impact:** These create nonsensical hybrid sentences that are neither French nor English.

### 3. Analysis by PDF

#### A-001 - NOTES ET LEGENDS.pdf
- **French/English Ratio:** 14.3% French
- **French spans found:** 67
- **In dictionary but still French:** 25 items
- **NOT in dictionary:** 42 items
- **Pattern:** Mostly long sentences (43 items) with Franglais corruption

#### A-021 - ANALYSE DE CODE.pdf
- **French/English Ratio:** 51.6% French (worst case)
- **French spans found:** 106
- **In dictionary but still French:** 81 items (!!)
- **NOT in dictionary:** 25 items
- **Pattern:** High percentage in dictionary but not translated (shows French→French issue)

#### A-062 - DÉTAILS PORTES ET CADRES.pdf
- **French/English Ratio:** 80.5% French
- **French spans found:** 53
- **In dictionary but still French:** 52 items (!!)
- **NOT in dictionary:** 1 item
- **Pattern:** Almost everything is in dictionary but still appears as French
- **Key examples:**
  - "CADRE EN ACIER" (appears 3+ times)
  - "ÉPAISSEUR CLOISON PLUS 5mm TYP."
  - "PROFILÉ EN U EN ACIER"

#### A-063 - BORDEREAU DES PORTES, CADRES ET OUVERTURES.pdf
- **French/English Ratio:** 66.0% French
- **French spans found:** 38
- **In dictionary but still French:** 37 items (!!)
- **NOT in dictionary:** 1 item
- **Pattern:** Almost perfect detection, but all "Porte XXXa" entries translate to themselves

#### A-171b - PLAN D'WATERPROOFING DES FONDATIONS (INTERFACES).pdf
- **French/English Ratio:** 68.2% French
- **French spans found:** 32
- **In dictionary but still French:** 25 items
- **NOT in dictionary:** 7 items
- **Key examples:**
  - "VOIR X / A-171b" (multiple instances)
  - "Jetée Ouest"
  - "ISOLANT RIGIDE TYPE 4A DE 51 mm"

## Why This Happened

### Root Cause: Manual Translation Workflow Failure

The system works as follows:
1. Extract French text from PDF
2. Check if in dictionary
3. If NOT in dictionary → save to `{PDF}_to_translate.json`
4. **MANUAL STEP:** User/Claude translates the JSON file
5. Save translations as `{PDF}_sentences.json`
6. Add to growing dictionary
7. Apply to PDF

**The problem:** In step 4-5, translations were:
- Not performed (French copied as-is)
- Partially performed (some words translated, others not)
- Corrupted during copy/paste or encoding issues

### Evidence

Looking at `A-062_sentences.json` (line 1-28):
- Contains proper English translations
- But some earlier translations in main dictionary are faulty

Looking at main dictionary:
- 70+ entries where French = English (identity mapping)
- These were likely from early translations where:
  - User copied French instead of translating
  - User thought they were proper nouns (e.g., "Porte 221a")
  - Encoding corruption made verification difficult

## Text Patterns NOT Being Translated

### By Length:
1. **Single words (11 in A-001):** Technical terms, units
2. **Short phrases (2-3 words):** Mostly proper nouns like "MONTRÉAL-TRUDEAU INTERNATIONAL"
3. **Medium phrases (4-8 words):** Mix of untranslated and partially translated
4. **Long sentences (9+ words):** Heavy Franglais corruption

### Common French Words Still Present:
- **VOIR** (4-7 occurrences per PDF) - Should be "SEE"
- **POUR** (1-5 occurrences) - Should be "FOR"
- **DE/DES** (2-27 occurrences) - Should be "OF/OF THE"
- **CADRE/CADRES** (11 in A-062) - Should be "FRAME/FRAMES"
- **PORTE/PORTES** (31 in A-063) - Should be "DOOR/DOORS"

### Example Breakdown (A-062):
```
Total text spans: 207
French detected: 53 (25.6%)
  ├─ In dictionary but still French: 52 (98%!)
  └─ Not in dictionary: 1 (2%)
```

**This means:** The detection works perfectly, the dictionary has entries, but **the entries are bad translations**.

## Recommendations

### Immediate Fix (High Priority)

1. **Clean the dictionary:**
   ```python
   # Find all French→French mappings
   faulty = {k:v for k,v in TRANSLATION_DICT.items() if k == v and has_french(k)}

   # These need retranslation:
   # - CADRE EN ACIER → STEEL FRAME
   # - VOIR X / Y → SEE X / Y
   # - Porte XXXa → Door XXXa
   # - etc.
   ```

2. **Re-translate the 70+ faulty entries:**
   - Export faulty entries to JSON
   - Get proper English translations
   - Update dictionary
   - Re-run translation on all PDFs

3. **Fix Franglais sentences:**
   - Find all long sentences with mixed French/English
   - Re-translate completely
   - Update dictionary

### Medium-Term Fix

4. **Add validation to translation workflow:**
   - After manual translation step, check if translation != original
   - Flag suspicious translations (too similar, still has French words)
   - Prevent identity mappings from entering dictionary

5. **Add quality checks:**
   ```python
   def validate_translation(french, english):
       # Check if too similar
       if french == english:
           return False, "Identity mapping"

       # Check if English still has French
       if has_french_indicators(english):
           return False, "Translation still contains French"

       # Check encoding corruption
       if '�' in english or 'NOTN' in english:
           return False, "Possible encoding corruption"

       return True, "OK"
   ```

### Long-Term Improvement

6. **Use automated translation API:**
   - Google Translate API / DeepL API for initial pass
   - Human review only for technical terms
   - Would prevent identity mapping issue

7. **Implement translation cache verification:**
   - Before adding to growing dictionary, verify it's actually translated
   - Track translation quality metrics

## Expected Outcome After Fix

| PDF | Current French % | Expected After Fix |
|-----|------------------|-------------------|
| A-001 | 14.3% | < 2% |
| A-021 | 51.6% | < 5% |
| A-062 | 80.5% | < 5% |
| A-063 | 66.0% | < 5% |
| A-171b | 68.2% | < 5% |

**Why not 0%?**
- Proper nouns should remain (company names, airport names)
- Technical codes may be bilingual
- Some mixed-language terms are standard in industry
