#!/usr/bin/env python3
"""
CNKI Chinese Academic Articles Analysis
Parses DOCX, codes institutional prestige, computes AI-style scores,
runs OLS regressions, and outputs JSON summary.
"""

import zipfile
import xml.etree.ElementTree as ET
import re
import json
import math
import sys
from datetime import date, datetime
from collections import Counter

# ─── ensure dependencies ───────────────────────────────────────────────────
try:
    import numpy as np
    import pandas as pd
    from scipy import stats
    import statsmodels.formula.api as smf
    print("All dependencies available.")
except ImportError as e:
    print(f"Missing dependency: {e}. Installing...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "numpy", "pandas",
                    "scipy", "statsmodels"], check=True)
    import numpy as np
    import pandas as pd
    from scipy import stats
    import statsmodels.formula.api as smf
    print("Dependencies installed and imported.")

# ─── constants ─────────────────────────────────────────────────────────────
DOCX_PATH = '/root/.claude/uploads/b89b636f-485a-462c-8d5c-a185cf6c4799/cfa401ae-___DOCX___.docx'
OUTPUT_PATH = '/home/user/replication-corner/analysis_results.json'
COLLECTION_DATE = date(2026, 6, 5)

C9 = ['清华大学', '北京大学', '复旦大学', '上海交通大学', '浙江大学',
       '中国科学技术大学', '南京大学', '西安交通大学', '哈尔滨工业大学']

TIER985 = ['中国人民大学', '北京航空航天大学', '北京理工大学', '北京师范大学',
           '南开大学', '天津大学', '大连理工大学', '吉林大学', '同济大学',
           '华东师范大学', '东南大学', '中国海洋大学', '山东大学', '武汉大学',
           '华中科技大学', '湖南大学', '中南大学', '中山大学', '华南理工大学',
           '四川大学', '电子科技大学', '重庆大学', '西北工业大学', '兰州大学',
           '东北大学', '中央民族大学', '西北农林科技大学', '国防科技大学',
           '中国农业大学', '厦门大学', '中南财经政法大学', '华中农业大学',
           '西南交通大学', '西南大学', '云南大学', '郑州大学', '新疆大学',
           '海南大学', '东华大学']

TIER211 = ['北京工业大学', '北京科技大学', '北京化工大学', '北京邮电大学',
           '中国传媒大学', '中央财经大学', '对外经济贸易大学', '北京外国语大学',
           '首都师范大学', '北京交通大学', '北京林业大学', '中国政法大学',
           '华北电力大学', '河北工业大学', '太原理工大学', '内蒙古大学',
           '辽宁大学', '大连海事大学', '延边大学', '东北师范大学', '东北农业大学',
           '东北林业大学', '华东理工大学', '上海大学', '苏州大学', '南京理工大学',
           '南京航空航天大学', '南京师范大学', '南京农业大学', '河海大学',
           '中国矿业大学', '扬州大学', '安徽大学', '合肥工业大学', '福州大学',
           '南昌大学', '中国地质大学', '武汉理工大学', '华中师范大学', '华中农业大学',
           '中南财经政法大学', '湖南师范大学', '暨南大学', '广州大学', '汕头大学',
           '广西大学', '西南财经大学', '贵州大学', '西藏大学', '长安大学',
           '西北大学', '西北师范大学', '宁夏大学', '青海大学', '石河子大学',
           '中国石油大学', '中国地质大学', '辽宁工程技术大学', '上海财经大学',
           '浙江工业大学', '浙江师范大学', '山西大学', '山东师范大学', '济南大学',
           '安徽师范大学', '江西师范大学', '湖南农业大学', '海南师范大学',
           '重庆医科大学', '贵州师范大学', '华侨大学', '西南民族大学',
           '广西民族大学', '内蒙古农业大学', '新疆农业大学', '宁波大学',
           '湖北大学', '中国药科大学', '南京中医药大学', '天津医科大学',
           '首都医科大学']

AI_MARKERS = ['机制分析', '异质性分析', '稳健性检验', '研究发现', '实证研究',
              '中介效应', '调节效应', '研究结论', '进一步分析', '双重差分',
              '固定效应', '面板数据', '基准回归', '理论贡献', '实践启示',
              '结果表明', '研究表明', '数据表明', '验证了', '本研究',
              '研究发现如下', '创新性地', '系统性地']

# ─── Step A: Parse full text ───────────────────────────────────────────────
print("\n=== Step A: Parsing DOCX ===")
with zipfile.ZipFile(DOCX_PATH) as z:
    with z.open('word/document.xml') as f:
        tree = ET.parse(f)
root = tree.getroot()
ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
all_text = []
for t in root.iter(f'{{{ns}}}t'):
    if t.text:
        all_text.append(t.text)
full = ''.join(all_text)
print(f"Total text length: {len(full):,} characters")

# Split by CNKI AI阅读 separator
# First article is before first separator; subsequent articles follow
raw_chunks = re.split(r'CNKI AI阅读\s*', full)
print(f"Raw chunks after split: {len(raw_chunks)}")

# The first chunk IS article 1 (no preceding separator)
# Each chunk after stripping has article content
# Format: "[number] title ... 【期刊】 journal date ... 下载 N [被引 N] 摘要： ... 关键词： ..."


def parse_chunk(chunk_text, chunk_idx):
    """Parse one article chunk. Returns dict or None on failure."""
    text = chunk_text.strip()
    if not text:
        return None

    # Strip leading article number (e.g. "2 " or "114 ")
    # First chunk (idx=0) has no leading number
    if chunk_idx > 0:
        text = re.sub(r'^\d+\s+', '', text, count=1)

    # ── Split on 【期刊】 ──────────────────────────────────────────────
    journal_split = re.split(r'【期刊】\s*', text, maxsplit=1)
    if len(journal_split) < 2:
        return None

    pre_journal = journal_split[0].strip()
    post_journal = journal_split[1].strip()

    # ── Extract title ────────────────────────────────────────────────
    # Title is everything up to first author name / institution block
    # Heuristic: title ends before first Chinese name-like pattern or institution
    # The pre_journal block: "title [网络首发] [免费] author1 inst1 author2 inst2..."
    # Remove badges
    pre_journal_clean = re.sub(r'(网络首发|免费|付费)\s*', '', pre_journal).strip()

    # ── Extract institutions ─────────────────────────────────────────
    # Institutions are strings containing 大学, 学院, 研究院, 研究所, etc.
    # Authors are typically 2-4 character Chinese names
    inst_pattern = re.compile(
        r'[一-鿿]{2,}(?:大学|学院|研究院|研究所|研究中心|学校|机构|'
        r'部门|委员会|协会|实验室|中心|出版社|银行|证监会|发改委|基金|公司|局|厅|所|院)'
        r'[一-鿿（）【】\-]*'
    )
    institutions = inst_pattern.findall(pre_journal_clean)
    # Deduplicate preserving order
    seen = set()
    unique_insts = []
    for inst in institutions:
        if inst not in seen:
            seen.add(inst)
            unique_insts.append(inst)

    # ── Parse journal, date, downloads, citations ────────────────────
    # post_journal: "journal_name date [时间] 下载 N [被引 N] 摘要： ... 关键词：..."

    # Extract date (YYYY-MM-DD or YYYY-MM-DD HH:MM)
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', post_journal)
    date_str = date_match.group(1) if date_match else None

    # Extract journal name (text before the date)
    if date_match:
        journal_name = post_journal[:date_match.start()].strip()
    else:
        journal_name = post_journal.split()[0] if post_journal.split() else ''

    # Extract downloads
    dl_match = re.search(r'下载\s+(\d+)', post_journal)
    downloads = int(dl_match.group(1)) if dl_match else 0

    # Extract citations (被引 N)
    cite_match = re.search(r'被引\s+(\d+)', post_journal)
    citations = int(cite_match.group(1)) if cite_match else 0

    # ── Extract abstract ─────────────────────────────────────────────
    abs_match = re.search(r'摘要[：:]\s*(.*?)(?:关键词[：:]|$)', post_journal, re.DOTALL)
    abstract = abs_match.group(1).strip() if abs_match else ''

    # ── Extract keywords ─────────────────────────────────────────────
    kw_match = re.search(r'关键词[：:]\s*(.*?)(?:下载|原版阅读|HTML阅读|收藏|引用|$)',
                          post_journal, re.DOTALL)
    keywords = kw_match.group(1).strip() if kw_match else ''

    # ── Build title ──────────────────────────────────────────────────
    # Title = pre_journal_clean minus institution/author segments
    # Remove institutions from the string to isolate title
    title_raw = pre_journal_clean
    for inst in unique_insts:
        title_raw = title_raw.replace(inst, ' ')
    # Remove short name-like tokens (2-4 chars, no punctuation) that look like authors
    # Title is the longest continuous segment at the beginning
    title_parts = re.split(r'\s{2,}', title_raw.strip())
    title = title_parts[0].strip() if title_parts else pre_journal_clean[:80]

    return {
        'title': title,
        'journal': journal_name,
        'date_str': date_str,
        'downloads': downloads,
        'citations': citations,
        'abstract': abstract,
        'keywords': keywords,
        'institutions': unique_insts,
        'raw_pre': pre_journal_clean[:200],  # for debugging
    }


articles = []
failed = 0
for i, chunk in enumerate(raw_chunks):
    result = parse_chunk(chunk, i)
    if result is not None:
        articles.append(result)
    else:
        failed += 1

print(f"Successfully parsed: {len(articles)}")
print(f"Failed/empty: {failed}")

# Show sample
print("\nSample article 0:")
a = articles[0]
print(f"  Journal: {a['journal']}")
print(f"  Date: {a['date_str']}")
print(f"  Downloads: {a['downloads']}, Citations: {a['citations']}")
print(f"  Abstract length: {len(a['abstract'])}")
print(f"  Institutions: {a['institutions'][:3]}")

N_TOTAL = len(articles)

# ─── Step B: Institutional Prestige ───────────────────────────────────────
print("\n=== Step B: Coding Institutional Prestige ===")

# Build lookup: name -> tier
prestige_map = {}
for name in C9:
    prestige_map[name] = 4
for name in TIER985:
    if name not in prestige_map:
        prestige_map[name] = 3
for name in TIER211:
    if name not in prestige_map:
        prestige_map[name] = 2


def get_prestige(institutions):
    """Return max prestige tier across all institutions. 1 if none match."""
    best = 1
    for inst in institutions:
        for uni_name, tier in prestige_map.items():
            if uni_name in inst:
                best = max(best, tier)
    return best


for a in articles:
    a['prestige_score'] = get_prestige(a['institutions'])

prestige_counts = Counter(a['prestige_score'] for a in articles)
print(f"Prestige distribution (all {N_TOTAL}):")
for tier in [1, 2, 3, 4]:
    print(f"  Tier {tier}: {prestige_counts.get(tier, 0)}")

# ─── Step C: AI-Style Score ────────────────────────────────────────────────
print("\n=== Step C: Computing AI-Style Scores ===")


def ai_style_score(abstract):
    count = sum(1 for marker in AI_MARKERS if marker in abstract)
    return count / len(AI_MARKERS)


for a in articles:
    a['ai_score'] = ai_style_score(a['abstract'])

ai_scores = [a['ai_score'] for a in articles]
print(f"AI score stats — mean: {np.mean(ai_scores):.4f}, "
      f"median: {np.median(ai_scores):.4f}, "
      f"max: {np.max(ai_scores):.4f}")

# ─── Step D: Compute Other Variables ──────────────────────────────────────
print("\n=== Step D: Computing Variables ===")


def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        return None


records = []
for a in articles:
    pub_date = parse_date(a['date_str'])
    if pub_date is None:
        continue

    year = pub_date.year
    age_days = (COLLECTION_DATE - pub_date).days
    if age_days < 0:
        age_days = 0

    log_downloads = math.log(a['downloads'] + 1)
    log_citations = math.log(a['citations'] + 1)
    log_age = math.log(age_days + 1)
    abstract_length = len(a['abstract'])
    log_abs_length = math.log(abstract_length + 1)

    records.append({
        'title': a['title'],
        'journal': a['journal'],
        'date_str': a['date_str'],
        'year': year,
        'downloads': a['downloads'],
        'citations': a['citations'],
        'prestige_score': a['prestige_score'],
        'ai_score': a['ai_score'],
        'abstract_length': abstract_length,
        'log_downloads': log_downloads,
        'log_citations': log_citations,
        'log_age': log_age,
        'log_abs_length': log_abs_length,
        'institutions': a['institutions'],
    })

df_all = pd.DataFrame(records)
print(f"Records with valid date: {len(df_all)}")
print(f"Year distribution:\n{df_all['year'].value_counts().sort_index()}")

# ─── Step E: Filter Sample ────────────────────────────────────────────────
print("\n=== Step E: Filtering Sample ===")

df = df_all[
    (df_all['year'] >= 2023) &
    (df_all['year'] <= 2026) &
    (df_all['abstract_length'] > 20)
].copy()

print(f"Analytic sample size: {len(df)}")
print(f"Year distribution in analytic sample:\n{df['year'].value_counts().sort_index()}")

# Standardize variables
df['prestige_z'] = (df['prestige_score'] - df['prestige_score'].mean()) / df['prestige_score'].std()
df['ai_z'] = (df['ai_score'] - df['ai_score'].mean()) / df['ai_score'].std()
df['Prestige_High'] = (df['prestige_score'] >= 2).astype(int)

N_ANALYTIC = len(df)

# ─── Step F: OLS Regressions ──────────────────────────────────────────────
print("\n=== Step F: Running OLS Regressions ===")


def fit_hc3(formula, data):
    """Fit OLS with HC3 robust standard errors, return result with pandas Series params."""
    return smf.ols(formula, data=data).fit(cov_type='HC3')


def extract_reg_results(result, prestige_var, ai_var='ai_z'):
    """Extract key regression statistics from HC3-fitted model."""
    params = result.params
    bse = result.bse
    pvals = result.pvalues
    conf = result.conf_int()

    # Interaction term name — statsmodels uses colon notation
    inter_var = f'{prestige_var}:{ai_var}'
    # statsmodels may order it either way
    if inter_var not in params.index:
        inter_var = f'{ai_var}:{prestige_var}'

    def safe_get(name, default=np.nan):
        return float(params.get(name, default))

    def safe_se(name, default=np.nan):
        return float(bse.get(name, default))

    def safe_p(name, default=np.nan):
        return float(pvals.get(name, default))

    def safe_ci_lo(name, default=np.nan):
        try:
            return float(conf.loc[name, 0])
        except Exception:
            return default

    def safe_ci_hi(name, default=np.nan):
        try:
            return float(conf.loc[name, 1])
        except Exception:
            return default

    return {
        'beta_prestige': round(safe_get(prestige_var), 3),
        'se_prestige': round(safe_se(prestige_var), 3),
        'p_prestige': round(safe_p(prestige_var), 4),
        'beta_ai': round(safe_get(ai_var), 3),
        'se_ai': round(safe_se(ai_var), 3),
        'p_ai': round(safe_p(ai_var), 4),
        'beta_interaction': round(safe_get(inter_var), 3),
        'se_interaction': round(safe_se(inter_var), 3),
        'p_interaction': round(safe_p(inter_var), 4),
        'ci_interaction_lo': round(safe_ci_lo(inter_var), 3),
        'ci_interaction_hi': round(safe_ci_hi(inter_var), 3),
        'r2': round(float(result.rsquared), 4),
        'adj_r2': round(float(result.rsquared_adj), 4),
    }


# Eq1: binary prestige, log_downloads
print("  Eq1: Prestige_High ~ log_downloads ...")
formula1 = 'log_downloads ~ Prestige_High + ai_z + Prestige_High:ai_z + log_age + log_abs_length + C(year)'
model1 = fit_hc3(formula1, df)
eq1_results = extract_reg_results(model1, 'Prestige_High')
print(f"    β_prestige={eq1_results['beta_prestige']}, β_ai={eq1_results['beta_ai']}, "
      f"β_interaction={eq1_results['beta_interaction']}, R²={eq1_results['r2']}")

# Eq2: binary prestige, log_citations
print("  Eq2: Prestige_High ~ log_citations ...")
formula2 = 'log_citations ~ Prestige_High + ai_z + Prestige_High:ai_z + log_age + log_abs_length + C(year)'
model2 = fit_hc3(formula2, df)
eq2_results = extract_reg_results(model2, 'Prestige_High')
print(f"    β_prestige={eq2_results['beta_prestige']}, β_ai={eq2_results['beta_ai']}, "
      f"β_interaction={eq2_results['beta_interaction']}, R²={eq2_results['r2']}")

# Eq3: continuous prestige, log_downloads
print("  Eq3: prestige_z ~ log_downloads ...")
formula3 = 'log_downloads ~ prestige_z + ai_z + prestige_z:ai_z + log_age + log_abs_length + C(year)'
model3 = fit_hc3(formula3, df)
eq3_results = extract_reg_results(model3, 'prestige_z')
print(f"    β_prestige={eq3_results['beta_prestige']}, β_ai={eq3_results['beta_ai']}, "
      f"β_interaction={eq3_results['beta_interaction']}, R²={eq3_results['r2']}")

# Eq4: continuous prestige, log_citations
print("  Eq4: prestige_z ~ log_citations ...")
formula4 = 'log_citations ~ prestige_z + ai_z + prestige_z:ai_z + log_age + log_abs_length + C(year)'
model4 = fit_hc3(formula4, df)
eq4_results = extract_reg_results(model4, 'prestige_z')
print(f"    β_prestige={eq4_results['beta_prestige']}, β_ai={eq4_results['beta_ai']}, "
      f"β_interaction={eq4_results['beta_interaction']}, R²={eq4_results['r2']}")

# ─── Robustness checks ────────────────────────────────────────────────────
print("\n=== Robustness Checks ===")

# Spec 2: AI binary (above median)
ai_median = df['ai_score'].median()
df['ai_binary'] = (df['ai_score'] > ai_median).astype(int)
print(f"  Spec2: AI binary (threshold={ai_median:.4f}) ...")
formula_r2 = 'log_downloads ~ Prestige_High + ai_binary + Prestige_High:ai_binary + log_age + log_abs_length + C(year)'
model_r2 = smf.ols(formula_r2, data=df).fit(cov_type='HC3')
inter_key = 'Prestige_High:ai_binary'
spec2_results = {
    'beta_prestige': round(float(model_r2.params.get('Prestige_High', np.nan)), 3),
    'se_prestige': round(float(model_r2.bse.get('Prestige_High', np.nan)), 3),
    'p_prestige': round(float(model_r2.pvalues.get('Prestige_High', np.nan)), 4),
    'beta_ai_binary': round(float(model_r2.params.get('ai_binary', np.nan)), 3),
    'se_ai_binary': round(float(model_r2.bse.get('ai_binary', np.nan)), 3),
    'p_ai_binary': round(float(model_r2.pvalues.get('ai_binary', np.nan)), 4),
    'beta_interaction': round(float(model_r2.params.get(inter_key, np.nan)), 3),
    'se_interaction': round(float(model_r2.bse.get(inter_key, np.nan)), 3),
    'p_interaction': round(float(model_r2.pvalues.get(inter_key, np.nan)), 4),
    'r2': round(float(model_r2.rsquared), 4),
    'adj_r2': round(float(model_r2.rsquared_adj), 4),
}
print(f"    β_interaction={spec2_results['beta_interaction']}, R²={spec2_results['r2']}")

# Spec 3: Exclude 2026
df_no2026 = df[df['year'] != 2026].copy()
print(f"  Spec3: Excluding 2026 (N={len(df_no2026)}) ...")
if len(df_no2026) > 10 and df_no2026['year'].nunique() > 1:
    formula_r3 = 'log_downloads ~ Prestige_High + ai_z + Prestige_High:ai_z + log_age + log_abs_length + C(year)'
    model_r3 = smf.ols(formula_r3, data=df_no2026).fit(cov_type='HC3')
    inter_key3 = 'Prestige_High:ai_z'
    if inter_key3 not in model_r3.params.index:
        inter_key3 = 'ai_z:Prestige_High'
    spec3_results = {
        'n': len(df_no2026),
        'beta_prestige': round(float(model_r3.params.get('Prestige_High', np.nan)), 3),
        'se_prestige': round(float(model_r3.bse.get('Prestige_High', np.nan)), 3),
        'p_prestige': round(float(model_r3.pvalues.get('Prestige_High', np.nan)), 4),
        'beta_ai': round(float(model_r3.params.get('ai_z', np.nan)), 3),
        'se_ai': round(float(model_r3.bse.get('ai_z', np.nan)), 3),
        'p_ai': round(float(model_r3.pvalues.get('ai_z', np.nan)), 4),
        'beta_interaction': round(float(model_r3.params.get(inter_key3, np.nan)), 3),
        'se_interaction': round(float(model_r3.bse.get(inter_key3, np.nan)), 3),
        'p_interaction': round(float(model_r3.pvalues.get(inter_key3, np.nan)), 4),
        'r2': round(float(model_r3.rsquared), 4),
        'adj_r2': round(float(model_r3.rsquared_adj), 4),
    }
else:
    spec3_results = {'note': 'insufficient data after excluding 2026'}
print(f"    β_interaction={spec3_results.get('beta_interaction', 'N/A')}, R²={spec3_results.get('r2', 'N/A')}")

# Spec 4: Trim top 5% downloads
q95 = df['downloads'].quantile(0.95)
df_trim = df[df['downloads'] <= q95].copy()
print(f"  Spec4: Trim top 5% downloads (cutoff={q95}, N={len(df_trim)}) ...")
formula_r4 = 'log_downloads ~ Prestige_High + ai_z + Prestige_High:ai_z + log_age + log_abs_length + C(year)'
model_r4 = smf.ols(formula_r4, data=df_trim).fit(cov_type='HC3')
inter_key4 = 'Prestige_High:ai_z'
if inter_key4 not in model_r4.params.index:
    inter_key4 = 'ai_z:Prestige_High'
spec4_results = {
    'n': len(df_trim),
    'download_cutoff': float(q95),
    'beta_prestige': round(float(model_r4.params.get('Prestige_High', np.nan)), 3),
    'se_prestige': round(float(model_r4.bse.get('Prestige_High', np.nan)), 3),
    'p_prestige': round(float(model_r4.pvalues.get('Prestige_High', np.nan)), 4),
    'beta_ai': round(float(model_r4.params.get('ai_z', np.nan)), 3),
    'se_ai': round(float(model_r4.bse.get('ai_z', np.nan)), 3),
    'p_ai': round(float(model_r4.pvalues.get('ai_z', np.nan)), 4),
    'beta_interaction': round(float(model_r4.params.get(inter_key4, np.nan)), 3),
    'se_interaction': round(float(model_r4.bse.get(inter_key4, np.nan)), 3),
    'p_interaction': round(float(model_r4.pvalues.get(inter_key4, np.nan)), 4),
    'r2': round(float(model_r4.rsquared), 4),
    'adj_r2': round(float(model_r4.rsquared_adj), 4),
}
print(f"    β_interaction={spec4_results['beta_interaction']}, R²={spec4_results['r2']}")

# ─── Correlations ─────────────────────────────────────────────────────────
print("\n=== Computing Correlations ===")


def pearson_r_p(x, y):
    mask = ~(np.isnan(x) | np.isnan(y))
    if mask.sum() < 3:
        return np.nan, np.nan
    r, p = stats.pearsonr(x[mask], y[mask])
    return float(r), float(p)


prestige_arr = df['prestige_score'].values
ai_arr = df['ai_score'].values
log_dl_arr = df['log_downloads'].values
log_ci_arr = df['log_citations'].values
log_age_arr = df['log_age'].values

r_pa, p_pa = pearson_r_p(prestige_arr, ai_arr)
r_pd, p_pd = pearson_r_p(prestige_arr, log_dl_arr)
r_pc, p_pc = pearson_r_p(prestige_arr, log_ci_arr)
r_ad, p_ad = pearson_r_p(ai_arr, log_dl_arr)
r_ac, p_ac = pearson_r_p(ai_arr, log_ci_arr)
r_aged, p_aged = pearson_r_p(log_age_arr, log_dl_arr)
r_agec, p_agec = pearson_r_p(log_age_arr, log_ci_arr)

print(f"  r(prestige, ai)={r_pa:.3f} p={p_pa:.4f}")
print(f"  r(prestige, log_downloads)={r_pd:.3f} p={p_pd:.4f}")
print(f"  r(ai, log_downloads)={r_ad:.3f} p={p_ad:.4f}")

# ─── Descriptive Statistics ────────────────────────────────────────────────
print("\n=== Descriptive Statistics ===")

year_dist = df['year'].value_counts().sort_index().to_dict()
year_dist = {str(k): int(v) for k, v in year_dist.items()}

prestige_tier_dist = df['prestige_score'].value_counts().sort_index().to_dict()
prestige_tier_dist = {str(k): int(v) for k, v in prestige_tier_dist.items()}

prestige_high_n = int(df['Prestige_High'].sum())
prestige_high_pct = round(prestige_high_n / N_ANALYTIC * 100, 2)

zero_citations_n = int((df['citations'] == 0).sum())
zero_citations_pct = round(zero_citations_n / N_ANALYTIC * 100, 2)

ai_high = df[df['Prestige_High'] == 1]['ai_score']
ai_low = df[df['Prestige_High'] == 0]['ai_score']

# Top institutions
all_insts = []
for idx, row in df.iterrows():
    all_insts.extend(row['institutions'])
inst_counter = Counter(all_insts)
top_institutions = [inst for inst, count in inst_counter.most_common(20)]

print(f"N analytic: {N_ANALYTIC}")
print(f"Prestige High: {prestige_high_n} ({prestige_high_pct}%)")
print(f"Zero citations: {zero_citations_n} ({zero_citations_pct}%)")
print(f"AI score mean: {df['ai_score'].mean():.4f}, sd: {df['ai_score'].std():.4f}")

# ─── Step G: Build JSON Output ─────────────────────────────────────────────
print("\n=== Step G: Writing JSON Output ===")


def r(x, decimals=4):
    """Round to decimals, handle NaN."""
    if isinstance(x, float) and math.isnan(x):
        return None
    return round(float(x), decimals)


output = {
    "N_total_parsed": N_TOTAL,
    "N_analytic": N_ANALYTIC,
    "zero_citations_n": zero_citations_n,
    "zero_citations_pct": zero_citations_pct,
    "year_distribution": year_dist,
    "prestige_high_n": prestige_high_n,
    "prestige_high_pct": prestige_high_pct,
    "prestige_tier_dist": prestige_tier_dist,

    "ai_score_mean": r(df['ai_score'].mean()),
    "ai_score_sd": r(df['ai_score'].std()),
    "ai_score_min": r(df['ai_score'].min()),
    "ai_score_median": r(df['ai_score'].median()),
    "ai_score_max": r(df['ai_score'].max()),

    "downloads_mean": r(df['downloads'].mean()),
    "downloads_sd": r(df['downloads'].std()),
    "log_downloads_mean": r(df['log_downloads'].mean()),
    "log_downloads_sd": r(df['log_downloads'].std()),
    "log_downloads_min": r(df['log_downloads'].min()),
    "log_downloads_max": r(df['log_downloads'].max()),
    "log_downloads_median": r(df['log_downloads'].median()),

    "citations_mean": r(df['citations'].mean()),
    "log_citations_mean": r(df['log_citations'].mean()),
    "log_citations_sd": r(df['log_citations'].std()),
    "log_citations_min": r(df['log_citations'].min()),
    "log_citations_max": r(df['log_citations'].max()),
    "log_citations_median": r(df['log_citations'].median()),

    "log_age_mean": r(df['log_age'].mean()),
    "log_age_sd": r(df['log_age'].std()),
    "log_age_min": r(df['log_age'].min()),
    "log_age_max": r(df['log_age'].max()),
    "log_age_median": r(df['log_age'].median()),

    "abs_length_mean": r(df['abstract_length'].mean()),
    "log_abs_length_mean": r(df['log_abs_length'].mean()),
    "log_abs_length_sd": r(df['log_abs_length'].std()),
    "log_abs_length_min": r(df['log_abs_length'].min()),
    "log_abs_length_max": r(df['log_abs_length'].max()),
    "log_abs_length_median": r(df['log_abs_length'].median()),

    "correlations": {
        "r_prestige_ai": r(r_pa),
        "r_prestige_downloads": r(r_pd),
        "r_prestige_citations": r(r_pc),
        "r_ai_downloads": r(r_ad),
        "r_ai_citations": r(r_ac),
        "r_age_downloads": r(r_aged),
        "r_age_citations": r(r_agec),
        "p_prestige_ai": r(p_pa),
        "p_prestige_downloads": r(p_pd),
        "p_prestige_citations": r(p_pc),
        "p_ai_downloads": r(p_ad),
        "p_ai_citations": r(p_ac),
        "p_age_downloads": r(p_aged),
        "p_age_citations": r(p_agec),
    },

    "ai_score_by_prestige": {
        "high_mean": r(float(ai_high.mean())),
        "low_mean": r(float(ai_low.mean())),
    },

    "eq1_downloads": eq1_results,
    "eq2_citations": eq2_results,
    "eq3_downloads_cont": eq3_results,
    "eq4_citations_cont": eq4_results,

    "robustness": {
        "spec2_ai_binary_downloads": spec2_results,
        "spec3_excl_2026_downloads": spec3_results,
        "spec4_trim_top5_downloads": spec4_results,
    },

    "top_institutions_sample": top_institutions,
}

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nJSON saved to: {OUTPUT_PATH}")

# ─── Final Summary ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("ANALYSIS SUMMARY")
print("=" * 60)
print(f"Total articles parsed:        {N_TOTAL}")
print(f"Analytic sample (2023-2026):  {N_ANALYTIC}")
print(f"Zero-citation articles:       {zero_citations_n} ({zero_citations_pct}%)")
print(f"\nYear distribution:")
for yr, n in sorted(year_dist.items()):
    print(f"  {yr}: {n}")
print(f"\nPrestige tier distribution:")
for tier in ['1', '2', '3', '4']:
    print(f"  Tier {tier}: {prestige_tier_dist.get(tier, 0)}")
print(f"Prestige_High (≥2): {prestige_high_n} ({prestige_high_pct}%)")
print(f"\nAI-style score:")
print(f"  Mean={df['ai_score'].mean():.4f}, SD={df['ai_score'].std():.4f}, "
      f"Median={df['ai_score'].median():.4f}")
print(f"  High-prestige mean={ai_high.mean():.4f}, Low-prestige mean={ai_low.mean():.4f}")
print(f"\nDownloads: mean={df['downloads'].mean():.1f}, SD={df['downloads'].std():.1f}")
print(f"Citations: mean={df['citations'].mean():.2f} (log_mean={df['log_citations'].mean():.4f})")
print(f"\nKey Correlations:")
print(f"  r(prestige, AI score) = {r_pa:.3f} (p={p_pa:.4f})")
print(f"  r(AI score, log_downloads) = {r_ad:.3f} (p={p_ad:.4f})")
print(f"  r(AI score, log_citations) = {r_ac:.3f} (p={p_ac:.4f})")
print(f"\nRegression Results (HC3 SEs):")
print(f"  Eq1 (binary prestige × AI → downloads): "
      f"β_interact={eq1_results['beta_interaction']}, "
      f"p={eq1_results['p_interaction']}, R²={eq1_results['r2']}")
print(f"  Eq2 (binary prestige × AI → citations): "
      f"β_interact={eq2_results['beta_interaction']}, "
      f"p={eq2_results['p_interaction']}, R²={eq2_results['r2']}")
print(f"  Eq3 (continuous prestige × AI → downloads): "
      f"β_interact={eq3_results['beta_interaction']}, "
      f"p={eq3_results['p_interaction']}, R²={eq3_results['r2']}")
print(f"  Eq4 (continuous prestige × AI → citations): "
      f"β_interact={eq4_results['beta_interaction']}, "
      f"p={eq4_results['p_interaction']}, R²={eq4_results['r2']}")
print(f"\nTop 10 institutions in sample:")
for inst, cnt in inst_counter.most_common(10):
    print(f"  {inst}: {cnt}")
print("=" * 60)
