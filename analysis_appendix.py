#!/usr/bin/env python3
"""
Web Appendix Analysis — CNKI AI-Reputation Replication Study
Generates all supplementary results needed for Web Appendix A1–C.
Outputs: appendix_results.json
"""

import zipfile
import xml.etree.ElementTree as ET
import re
import json
import math
import sys
from datetime import date, datetime
from collections import Counter

try:
    import numpy as np
    import pandas as pd
    from scipy import stats
    import statsmodels.formula.api as smf
    import statsmodels.api as sm
    print("Dependencies OK.")
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install",
                    "numpy", "pandas", "scipy", "statsmodels"], check=True)
    import numpy as np
    import pandas as pd
    from scipy import stats
    import statsmodels.formula.api as smf
    import statsmodels.api as sm

# ─── Constants ────────────────────────────────────────────────────────────────
NEW_DOCX = '/root/.claude/uploads/370674e4-caa7-461a-ab9b-cc8104dd780e/1ae3e22b-___DOCX___.docx'
OUTPUT_JSON = '/home/user/replication-corner/appendix_results.json'
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
           '南昌大学', '中国地质大学', '武汉理工大学', '华中师范大学',
           '中南财经政法大学', '湖南师范大学', '暨南大学', '广州大学', '汕头大学',
           '广西大学', '西南财经大学', '贵州大学', '西藏大学', '长安大学',
           '西北大学', '西北师范大学', '宁夏大学', '青海大学', '石河子大学',
           '中国石油大学', '辽宁工程技术大学', '上海财经大学',
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

# Marketing/management journal keywords (B7 sub-sample filter)
MKTG_MGMT_KW = ['管理', '营销', '市场', '商学', '工商', '经济管理',
                 '商业', '战略', '组织', '企业']

# Topic classification keywords
TOPIC_KW = {
    'AI_Digital': ['人工智能', '数字化', '大语言模型', '生成式', 'ChatGPT',
                   '数字经济', '数智', '智能化', '机器学习', '算法'],
    'SupplyChain': ['供应链', '物流', '采购', '运营管理', '库存', '制造'],
    'ESG_Green': ['碳排放', '绿色', 'ESG', '可持续', '环境', '双碳', '低碳'],
    'Governance': ['公司治理', '董事会', '股权', '高管', '股东', '产权'],
    'Marketing': ['营销', '消费者', '品牌', '顾客', '电商', '价格', '市场营销'],
    'Innovation': ['创新', '创业', '技术创新', '研发', '专利', '知识产权'],
}


# ─── Parse DOCX ───────────────────────────────────────────────────────────────
def parse_docx(path):
    with zipfile.ZipFile(path) as z:
        with z.open('word/document.xml') as f:
            tree = ET.parse(f)
    root = tree.getroot()
    ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    all_text = []
    for t in root.iter(f'{{{ns}}}t'):
        if t.text:
            all_text.append(t.text)
    return ''.join(all_text)


def parse_chunk(text, idx):
    text = text.strip()
    if not text:
        return None
    if idx > 0:
        text = re.sub(r'^\d+\s+', '', text, count=1)
    js = re.split(r'【期刊】\s*', text, maxsplit=1)
    if len(js) < 2:
        return None
    pre = re.sub(r'(网络首发|免费|付费)\s*', '', js[0]).strip()
    post = js[1].strip()
    inst_pat = re.compile(
        r'[一-鿿]{2,}(?:大学|学院|研究院|研究所|研究中心|学校|机构|'
        r'部门|委员会|协会|实验室|中心|出版社|银行|证监会|发改委|基金|公司|局|厅|所|院)'
        r'[一-鿿（）【】\-]*'
    )
    insts = list(dict.fromkeys(inst_pat.findall(pre)))
    dm = re.search(r'(\d{4}-\d{2}-\d{2})', post)
    date_str = dm.group(1) if dm else None
    journal = post[:dm.start()].strip() if dm else (post.split()[0] if post.split() else '')
    dl = re.search(r'下载\s+(\d+)', post)
    ci = re.search(r'被引\s+(\d+)', post)
    ab = re.search(r'摘要[：:]\s*(.*?)(?:关键词[：:]|$)', post, re.DOTALL)
    kw = re.search(r'关键词[：:]\s*(.*?)(?:下载|原版阅读|HTML阅读|收藏|引用|$)', post, re.DOTALL)
    tr = pre
    for i in insts:
        tr = tr.replace(i, ' ')
    tp = re.split(r'\s{2,}', tr.strip())
    return {
        'title': tp[0].strip() if tp else pre[:80],
        'journal': journal,
        'date_str': date_str,
        'downloads': int(dl.group(1)) if dl else 0,
        'citations': int(ci.group(1)) if ci else 0,
        'abstract': ab.group(1).strip() if ab else '',
        'keywords': kw.group(1).strip() if kw else '',
        'institutions': insts,
    }


print("Parsing DOCX...")
full = parse_docx(NEW_DOCX)
chunks = re.split(r'CNKI AI阅读\s*', full)
articles = [r for r in (parse_chunk(c, i) for i, c in enumerate(chunks)) if r]
print(f"  Parsed {len(articles)} articles from {len(chunks)} chunks")

# ─── Prestige coding ──────────────────────────────────────────────────────────
prestige_map = {}
for n in C9:
    prestige_map[n] = 4
for n in TIER985:
    if n not in prestige_map:
        prestige_map[n] = 3
for n in TIER211:
    if n not in prestige_map:
        prestige_map[n] = 2


def get_prestige(insts, mode='max'):
    """mode='max' returns highest tier; mode='first' returns first institution's tier."""
    if mode == 'first':
        insts = insts[:1]
    best = 1
    for inst in insts:
        for uni, tier in prestige_map.items():
            if uni in inst:
                best = max(best, tier)
    return best


def ai_score(abstract):
    return sum(1 for m in AI_MARKERS if m in abstract) / len(AI_MARKERS)


def classify_topic(title, abstract, keywords):
    text = title + abstract + keywords
    for topic, kws in TOPIC_KW.items():
        if any(k in text for k in kws):
            return topic
    return 'Other'


def is_mktg_mgmt_journal(journal_name):
    return any(k in journal_name for k in MKTG_MGMT_KW)


# ─── Build records DataFrame ──────────────────────────────────────────────────
records = []
for a in articles:
    if not a['date_str']:
        continue
    try:
        pub_date = datetime.strptime(a['date_str'], '%Y-%m-%d').date()
    except Exception:
        continue
    year = pub_date.year
    if year < 2023 or year > 2026:
        continue
    if len(a['abstract']) < 20:
        continue
    age_days = max((COLLECTION_DATE - pub_date).days, 0)
    records.append({
        'title': a['title'],
        'journal': a['journal'],
        'year': year,
        'downloads': a['downloads'],
        'citations': a['citations'],
        'prestige_score': get_prestige(a['institutions'], 'max'),
        'prestige_first': get_prestige(a['institutions'], 'first'),
        'ai_score': ai_score(a['abstract']),
        'abstract_length': len(a['abstract']),
        'log_downloads': math.log(a['downloads'] + 1),
        'log_citations': math.log(a['citations'] + 1),
        'log_age': math.log(age_days + 1),
        'log_abs_length': math.log(len(a['abstract']) + 1),
        'is_mktg_mgmt': int(is_mktg_mgmt_journal(a['journal'])),
        'topic': classify_topic(a['title'], a['abstract'], a['keywords']),
        'institutions': a['institutions'],
    })

df = pd.DataFrame(records)
df['prestige_z'] = (df['prestige_score'] - df['prestige_score'].mean()) / df['prestige_score'].std()
df['prestige_first_z'] = (df['prestige_first'] - df['prestige_first'].mean()) / df['prestige_first'].std()
df['ai_z'] = (df['ai_score'] - df['ai_score'].mean()) / df['ai_score'].std()
df['Prestige_High'] = (df['prestige_score'] >= 2).astype(int)
df['Prestige_High_first'] = (df['prestige_first'] >= 2).astype(int)
df['ai_binary'] = (df['ai_score'] > df['ai_score'].median()).astype(int)

N = len(df)
print(f"  Analytic sample: N={N}")
print(f"  Year dist: {df['year'].value_counts().sort_index().to_dict()}")
print(f"  Marketing/mgmt journals: {df['is_mktg_mgmt'].sum()} ({100*df['is_mktg_mgmt'].mean():.1f}%)")
print(f"  Topic dist: {df['topic'].value_counts().to_dict()}")


# ─── Regression helpers ───────────────────────────────────────────────────────
def fit(formula, data, cov='HC3'):
    return smf.ols(formula, data=data).fit(cov_type=cov)


def full_table(result, prestige_var, ai_var='ai_z'):
    """Return all coefficients with SE, p, CI for full appendix table."""
    out = {}
    inter = f'{prestige_var}:{ai_var}'
    if inter not in result.params.index:
        inter = f'{ai_var}:{prestige_var}'
    ci = result.conf_int()
    for var in result.params.index:
        out[var] = {
            'beta': round(float(result.params[var]), 4),
            'se': round(float(result.bse[var]), 4),
            'p': round(float(result.pvalues[var]), 4),
            'ci_lo': round(float(ci.loc[var, 0]), 4),
            'ci_hi': round(float(ci.loc[var, 1]), 4),
        }
    return {
        'coefficients': out,
        'r2': round(float(result.rsquared), 4),
        'adj_r2': round(float(result.rsquared_adj), 4),
        'n': int(result.nobs),
        'focal_prestige': prestige_var,
        'focal_ai': ai_var,
        'focal_interaction': inter,
        'beta_prestige': round(float(result.params.get(prestige_var, np.nan)), 3),
        'se_prestige': round(float(result.bse.get(prestige_var, np.nan)), 3),
        'p_prestige': round(float(result.pvalues.get(prestige_var, np.nan)), 4),
        'beta_ai': round(float(result.params.get(ai_var, np.nan)), 3),
        'se_ai': round(float(result.bse.get(ai_var, np.nan)), 3),
        'p_ai': round(float(result.pvalues.get(ai_var, np.nan)), 4),
        'beta_interaction': round(float(result.params.get(inter, np.nan)), 3),
        'se_interaction': round(float(result.bse.get(inter, np.nan)), 3),
        'p_interaction': round(float(result.pvalues.get(inter, np.nan)), 4),
        'ci_interaction_lo': round(float(ci.loc[inter, 0]) if inter in ci.index else np.nan, 3),
        'ci_interaction_hi': round(float(ci.loc[inter, 1]) if inter in ci.index else np.nan, 3),
    }


BASE = 'log_age + log_abs_length + C(year)'
F1 = f'log_downloads ~ Prestige_High + ai_z + Prestige_High:ai_z + {BASE}'
F2 = f'log_citations ~ Prestige_High + ai_z + Prestige_High:ai_z + {BASE}'
F3 = f'log_downloads ~ prestige_z + ai_z + prestige_z:ai_z + {BASE}'
F4 = f'log_citations ~ prestige_z + ai_z + prestige_z:ai_z + {BASE}'

print("\nRunning main regressions (B1)...")
m1 = fit(F1, df); t1 = full_table(m1, 'Prestige_High')
m2 = fit(F2, df); t2 = full_table(m2, 'Prestige_High')
m3 = fit(F3, df); t3 = full_table(m3, 'prestige_z')
m4 = fit(F4, df); t4 = full_table(m4, 'prestige_z')
print(f"  Eq1 β_AI={t1['beta_ai']}, β_int={t1['beta_interaction']}, R²={t1['r2']}")

# ─── Robustness (B2) ──────────────────────────────────────────────────────────
print("Running robustness specs (B2)...")
# Spec2: binary AI
r2 = fit(f'log_downloads ~ Prestige_High + ai_binary + Prestige_High:ai_binary + {BASE}', df)
t_r2 = full_table(r2, 'Prestige_High', 'ai_binary')

# Spec3: exclude 2026
df_no26 = df[df['year'] != 2026].copy()
r3 = fit(F1, df_no26)
t_r3 = full_table(r3, 'Prestige_High')
t_r3['n'] = len(df_no26)

# Spec4: trim top 5% downloads
q95 = df['downloads'].quantile(0.95)
df_trim = df[df['downloads'] <= q95].copy()
r4 = fit(F1, df_trim)
t_r4 = full_table(r4, 'Prestige_High')
t_r4['download_cutoff'] = round(float(q95), 1)

# Spec5: citations baseline (binary prestige)
t_r5 = t2.copy()

# Spec6: downloads continuous prestige
t_r6 = t3.copy()

# ─── First-author prestige sensitivity (A3) ───────────────────────────────────
print("Running first-author prestige sensitivity (A3)...")
F1_first = f'log_downloads ~ Prestige_High_first + ai_z + Prestige_High_first:ai_z + {BASE}'
F2_first = f'log_citations ~ Prestige_High_first + ai_z + Prestige_High_first:ai_z + {BASE}'
m1f = fit(F1_first, df); t1f = full_table(m1f, 'Prestige_High_first')
m2f = fit(F2_first, df); t2f = full_table(m2f, 'Prestige_High_first')
first_author_pct_high = round(100 * df['Prestige_High_first'].mean(), 1)
print(f"  First-author high-prestige: {first_author_pct_high}%")
print(f"  β_int (downloads)={t1f['beta_interaction']}, β_int (citations)={t2f['beta_interaction']}")

# ─── Topic FE models (B6) ─────────────────────────────────────────────────────
print("Running topic FE models (B6)...")
df_topic = pd.get_dummies(df, columns=['topic'], prefix='T', drop_first=True)
topic_cols = [c for c in df_topic.columns if c.startswith('T_')]
topic_str = ' + '.join(topic_cols)
F1_tfe = f'log_downloads ~ Prestige_High + ai_z + Prestige_High:ai_z + {BASE} + {topic_str}'
F2_tfe = f'log_citations ~ Prestige_High + ai_z + Prestige_High:ai_z + {BASE} + {topic_str}'
m1t = fit(F1_tfe, df_topic); t1t = full_table(m1t, 'Prestige_High')
m2t = fit(F2_tfe, df_topic); t2t = full_table(m2t, 'Prestige_High')
print(f"  Topic FE: β_int (dl)={t1t['beta_interaction']}, β_int (ci)={t2t['beta_interaction']}")

# ─── Negative-binomial models (B5) ───────────────────────────────────────────
print("Running negative-binomial models (B5)...")
CTRL_VARS = ['log_age', 'log_abs_length']
year_dummies = pd.get_dummies(df['year'], prefix='year', drop_first=True)
df_nb = pd.concat([df, year_dummies], axis=1)
year_cols = [c for c in df_nb.columns if c.startswith('year_')]


def fit_nb(y_col, prestige_col, df_nb):
    X_cols = [prestige_col, 'ai_z', 'log_age', 'log_abs_length'] + year_cols
    X = sm.add_constant(df_nb[X_cols].astype(float))
    X[f'{prestige_col}_x_ai'] = df_nb[prestige_col] * df_nb['ai_z']
    col_order = ['const'] + X_cols + [f'{prestige_col}_x_ai']
    X = X[col_order]
    y = df_nb[y_col].astype(int)
    try:
        nb_model = sm.NegativeBinomial(y, X)
        nb_result = nb_model.fit(method='bfgs', maxiter=200, disp=0)
        inter_name = f'{prestige_col}_x_ai'
        return {
            'beta_prestige': round(float(nb_result.params[prestige_col]), 3),
            'se_prestige': round(float(nb_result.bse[prestige_col]), 3),
            'p_prestige': round(float(nb_result.pvalues[prestige_col]), 4),
            'beta_ai': round(float(nb_result.params['ai_z']), 3),
            'se_ai': round(float(nb_result.bse['ai_z']), 3),
            'p_ai': round(float(nb_result.pvalues['ai_z']), 4),
            'beta_interaction': round(float(nb_result.params[inter_name]), 3),
            'se_interaction': round(float(nb_result.bse[inter_name]), 3),
            'p_interaction': round(float(nb_result.pvalues[inter_name]), 4),
            'irr_ai': round(float(np.exp(nb_result.params['ai_z'])), 3),
            'irr_prestige': round(float(np.exp(nb_result.params[prestige_col])), 3),
            'irr_interaction': round(float(np.exp(nb_result.params[inter_name])), 3),
            'aic': round(float(nb_result.aic), 2),
            'n': int(len(y)),
        }
    except Exception as e:
        print(f"    NB failed: {e}")
        return {'error': str(e)}


nb1 = fit_nb('downloads', 'Prestige_High', df_nb)
nb2 = fit_nb('citations', 'Prestige_High', df_nb)
print(f"  NB downloads: β_int={nb1.get('beta_interaction', 'ERR')}, IRR_AI={nb1.get('irr_ai', 'ERR')}")
print(f"  NB citations: β_int={nb2.get('beta_interaction', 'ERR')}, IRR_AI={nb2.get('irr_ai', 'ERR')}")

# ─── Marketing/management sub-sample (B7) ────────────────────────────────────
print("Running marketing/management sub-sample (B7)...")
df_mm = df[df['is_mktg_mgmt'] == 1].copy()
N_mm = len(df_mm)
print(f"  Marketing/mgmt sub-sample: N={N_mm}")
if N_mm > 50:
    m1mm = fit(F1, df_mm); t1mm = full_table(m1mm, 'Prestige_High')
    m2mm = fit(F2, df_mm); t2mm = full_table(m2mm, 'Prestige_High')
    print(f"  β_int (dl)={t1mm['beta_interaction']}, β_int (ci)={t2mm['beta_interaction']}")
else:
    t1mm = {'note': f'Insufficient N={N_mm}'}
    t2mm = {'note': f'Insufficient N={N_mm}'}

# ─── Descriptive statistics ───────────────────────────────────────────────────
ai_by_year = df.groupby('year')['ai_score'].agg(['mean', 'median', 'std']).round(4)
ai_by_tier = df.groupby('prestige_score')['ai_score'].agg(['mean', 'median', 'count']).round(4)
pct_high_by_year = df.groupby('year')['Prestige_High'].mean().round(4)
topic_dist = df['topic'].value_counts().to_dict()
journal_mm_list = sorted(df[df['is_mktg_mgmt'] == 1]['journal'].value_counts().head(30).to_dict().items(),
                          key=lambda x: -x[1])

# AI score distribution by decile
ai_deciles = np.percentile(df['ai_score'], [10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

# Marker frequency table
marker_freq = {}
for m in AI_MARKERS:
    count = df.apply(lambda row: 1 if m in row.get('abstract', '') else 0, axis=1).sum() \
        if 'abstract' in df.columns else 0
marker_freq_list = []
for a in articles:
    if not a.get('date_str'):
        continue
    try:
        y = datetime.strptime(a['date_str'], '%Y-%m-%d').year
    except Exception:
        continue
    if y < 2023 or y > 2026 or len(a.get('abstract', '')) < 20:
        continue
    for m in AI_MARKERS:
        if m in a['abstract']:
            marker_freq[m] = marker_freq.get(m, 0) + 1

marker_table = sorted(marker_freq.items(), key=lambda x: -x[1])

# Correlations
def pr(x, y):
    m = ~(np.isnan(x) | np.isnan(y))
    r, p = stats.pearsonr(x[m], y[m])
    return round(float(r), 4), round(float(p), 4)

r_pa, p_pa = pr(df['prestige_score'].values, df['ai_score'].values)
r_pd, p_pd = pr(df['prestige_score'].values, df['log_downloads'].values)
r_pc, p_pc = pr(df['prestige_score'].values, df['log_citations'].values)
r_ad, p_ad = pr(df['ai_score'].values, df['log_downloads'].values)
r_ac, p_ac = pr(df['ai_score'].values, df['log_citations'].values)
r_agd, p_agd = pr(df['log_age'].values, df['log_downloads'].values)
r_agc, p_agc = pr(df['log_age'].values, df['log_citations'].values)

# ─── Assemble output ──────────────────────────────────────────────────────────
output = {
    'meta': {
        'N_raw_chunks': len(chunks),
        'N_parsed': len(articles),
        'N_analytic': N,
        'N_mktg_mgmt': N_mm,
        'pct_mktg_mgmt': round(100 * N_mm / N, 1),
        'collection_date': str(COLLECTION_DATE),
    },
    'year_distribution': df['year'].value_counts().sort_index().astype(int).to_dict(),
    'prestige_tier_distribution': df['prestige_score'].value_counts().sort_index().astype(int).to_dict(),
    'prestige_high_n': int(df['Prestige_High'].sum()),
    'prestige_high_pct': round(100 * df['Prestige_High'].mean(), 2),
    'prestige_first_high_pct': first_author_pct_high,
    'topic_distribution': {k: int(v) for k, v in topic_dist.items()},
    'ai_score_mean': round(float(df['ai_score'].mean()), 4),
    'ai_score_sd': round(float(df['ai_score'].std()), 4),
    'ai_score_median': round(float(df['ai_score'].median()), 4),
    'ai_score_max': round(float(df['ai_score'].max()), 4),
    'ai_score_deciles': [round(float(x), 4) for x in ai_deciles],
    'ai_by_year': {str(k): {'mean': float(v['mean']), 'median': float(v['median']),
                              'sd': float(v['std'])}
                   for k, v in ai_by_year.iterrows()},
    'ai_by_prestige_tier': {str(int(k)): {'mean': float(v['mean']), 'median': float(v['median']),
                                            'n': int(v['count'])}
                             for k, v in ai_by_tier.iterrows()},
    'marker_frequency': {m: c for m, c in marker_table},
    'correlations': {
        'r_prestige_ai': r_pa, 'p_prestige_ai': p_pa,
        'r_prestige_downloads': r_pd, 'p_prestige_downloads': p_pd,
        'r_prestige_citations': r_pc, 'p_prestige_citations': p_pc,
        'r_ai_downloads': r_ad, 'p_ai_downloads': p_ad,
        'r_ai_citations': r_ac, 'p_ai_citations': p_ac,
        'r_age_downloads': r_agd, 'p_age_downloads': p_agd,
        'r_age_citations': r_agc, 'p_age_citations': p_agc,
    },
    'B1_main_regressions': {
        'eq1_downloads_binary': t1,
        'eq2_citations_binary': t2,
        'eq3_downloads_continuous': t3,
        'eq4_citations_continuous': t4,
    },
    'B2_robustness': {
        'spec1_baseline_downloads': {
            'beta_prestige': t1['beta_prestige'], 'se_prestige': t1['se_prestige'], 'p_prestige': t1['p_prestige'],
            'beta_ai': t1['beta_ai'], 'se_ai': t1['se_ai'], 'p_ai': t1['p_ai'],
            'beta_interaction': t1['beta_interaction'], 'se_interaction': t1['se_interaction'],
            'p_interaction': t1['p_interaction'], 'r2': t1['r2'], 'n': t1['n'],
        },
        'spec2_binary_ai': t_r2,
        'spec3_excl_2026': t_r3,
        'spec4_trim_top5': t_r4,
        'spec5_citations_baseline': t_r5,
        'spec6_continuous_prestige': t_r6,
    },
    'A3_first_author_prestige': {
        'downloads': t1f,
        'citations': t2f,
    },
    'B5_negative_binomial': {
        'nb1_downloads': nb1,
        'nb2_citations': nb2,
    },
    'B6_topic_FE': {
        'topic_dummies_used': topic_cols,
        'downloads': t1t,
        'citations': t2t,
    },
    'B7_mktg_mgmt_subsample': {
        'n': N_mm,
        'pct_of_full': round(100 * N_mm / N, 1),
        'top_journals': [{'journal': j, 'n': c} for j, c in journal_mm_list],
        'downloads': t1mm,
        'citations': t2mm,
    },
    'pct_high_by_year': {str(k): float(v) for k, v in pct_high_by_year.items()},
}

with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nSaved to {OUTPUT_JSON}")
print("=" * 60)
print(f"N analytic = {N}")
print(f"Main Eq1: β_prestige={t1['beta_prestige']} (p={t1['p_prestige']}), "
      f"β_AI={t1['beta_ai']} (p={t1['p_ai']}), β_int={t1['beta_interaction']} (p={t1['p_interaction']})")
print(f"NB Eq1: β_AI={nb1.get('beta_ai','?')} (IRR={nb1.get('irr_ai','?')}), "
      f"β_int={nb1.get('beta_interaction','?')}")
print(f"Mktg sub (N={N_mm}): β_int(dl)={t1mm.get('beta_interaction','?')}")
print(f"First-author: β_int(dl)={t1f['beta_interaction']}")
print(f"Topic FE: β_int(dl)={t1t['beta_interaction']}")
print("=" * 60)
