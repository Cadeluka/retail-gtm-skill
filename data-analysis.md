# 数据分析模块详解

## 目录
1. [全年业绩总览](#1-全年业绩总览)
2. [区域两极对比](#2-区域两极对比)
3. [产品季度矩阵](#3-产品季度矩阵)
4. [产品进销配比](#4-产品进销配比)
5. [产品潜力分析](#5-产品潜力分析)
6. [KA客户健康度诊断](#6-ka客户健康度诊断)
7. [城市维度产品分析](#7-城市维度产品分析)

---

## 1. 全年业绩总览

**数据源**：连锁sheet  
**输出**：双线趋势图 + 两个KPI大数字

```python
import pandas as pd

def analyze_annual_overview(df_chain):
    """全年Sell-in vs Sell-out月度趋势"""
    # 排除电商（可选，根据业务需要）
    # df = df_chain[df_chain['Ecommerce'] == '非电商']
    df = df_chain
    
    monthly = df.groupby('YM').agg(
        SI=('PHM_SellInActual', 'sum'),
        SO=('PHM_SellOutActual', 'sum'),
        SI_LY=('PHM_SellInActualLY', 'sum'),
        SO_LY=('PHM_SellOutActualLY', 'sum')
    ).reset_index()
    
    monthly['SI_YoY'] = (monthly['SI'] - monthly['SI_LY']) / monthly['SI_LY'].abs()
    monthly['SO_YoY'] = (monthly['SO'] - monthly['SO_LY']) / monthly['SO_LY'].abs()
    monthly['SISO_Ratio'] = monthly['SI'] / monthly['SO']
    
    # 全年汇总
    total_SI = df['PHM_SellInActual'].sum()
    total_SO = df['PHM_SellOutActual'].sum()
    total_SI_LY = df['PHM_SellInActualLY'].sum()
    total_SO_LY = df['PHM_SellOutActualLY'].sum()
    
    summary = {
        'total_SI': total_SI,
        'total_SO': total_SO,
        'SI_YoY_pct': (total_SI - total_SI_LY) / abs(total_SI_LY),
        'SO_YoY_pct': (total_SO - total_SO_LY) / abs(total_SO_LY),
        'annual_SISO': total_SI / total_SO
    }
    
    return monthly, summary
```

**核心洞察模板**：
- "全年Sell-in [X]亿，同比[+/-XX%]；Sell-out [X]亿，同比[+/-XX%]"
- 若 SI降幅 > SO降幅："Sell-in降幅大于Sell-out，渠道主动控货"
- 若某月出现SI<SO："Q[X]渠道进入去库存周期，出现剪刀差"
- 关注异常月份（如7月纯销高峰）

---

## 2. 区域两极对比

**数据源**：连锁sheet  
**输出**：省份/城市Sell-in增长贡献瀑布图

```python
def analyze_regional_performance(df_chain):
    """识别明星市场 vs 问题市场"""
    regional = df_chain.groupby('ProvinceNameC').agg(
        SI=('PHM_SellInActual', 'sum'),
        SI_LY=('PHM_SellInActualLY', 'sum'),
        SO=('PHM_SellOutActual', 'sum'),
        SO_LY=('PHM_SellOutActualLY', 'sum')
    ).reset_index()
    
    regional['SI_delta'] = regional['SI'] - regional['SI_LY']
    regional['SI_growth'] = regional['SI_delta'] / regional['SI_LY'].abs()
    regional['contribution_pct'] = regional['SI_delta'] / regional['SI_delta'].sum()
    
    regional = regional.sort_values('SI_delta', ascending=False)
    return regional
```

**核心洞察模板**：
- 识别出"[省份A]逆势增长+X%"（明星）vs "[省份B]暴跌-XX%"（问题）
- "市场下滑不是共性问题，需具体针对客户和产品进行拆解"
- "下滑/增长主要集中在哪几个区域"

---

## 3. 产品季度矩阵

**数据源**：连锁sheet（按YM判断季度：1-3月=Q1，4-6月=Q2，7-9月=Q3，10-12月=Q4）

```python
def analyze_product_quarterly_matrix(df_chain):
    """分季度×分产品同比矩阵"""
    df = df_chain.copy()
    
    # 季度映射
    month = df['YM'].astype(str).str[-2:].astype(int)
    df['Quarter'] = pd.cut(month, bins=[0,3,6,9,12], labels=['Q1','Q2','Q3','Q4'])
    
    matrix = df.groupby(['Quarter', 'BrandNameE']).agg(
        SO=('PHM_SellOutActual', 'sum'),
        SO_LY=('PHM_SellOutActualLY', 'sum')
    ).reset_index()
    
    matrix['delta'] = matrix['SO'] - matrix['SO_LY']
    matrix['growth'] = matrix['delta'] / matrix['SO_LY'].abs()
    
    # 透视成矩阵
    pivot_delta = matrix.pivot(index='BrandNameE', columns='Quarter', values='delta')
    pivot_growth = matrix.pivot(index='BrandNameE', columns='Quarter', values='growth')
    
    return pivot_delta, pivot_growth
```

**PPT中的标准呈现格式**（表格）：
```
产品  | Q1           | Q2           | Q3          | Q4         | 全年
F     | -2,448(-23%) | -2,648(-24%) | -1,706(-18%)| -346(-6%)  | -7,148(-19%)
C     | ...
R     | 431(+53%)    | ...
```

**核心洞察模板**：
- "Q1+Q2的下滑贡献了全年的约70%，需要提前布局动销"
- "F产品贡献了最大下滑，但后续下滑趋势得以延缓"
- "R产品前三季度高速增长，但Q4出现放缓，需持续关注"

---

## 4. 产品进销配比

**数据源**：连锁sheet（全年汇总）

```python
def analyze_product_siso(df_chain):
    """各产品Sell-in vs Sell-out配比"""
    product = df_chain.groupby('BrandNameE').agg(
        SI=('PHM_SellInActual', 'sum'),
        SI_LY=('PHM_SellInActualLY', 'sum'),
        SO=('PHM_SellOutActual', 'sum'),
        SO_LY=('PHM_SellOutActualLY', 'sum')
    ).reset_index()
    
    product['SI_delta'] = product['SI'] - product['SI_LY']
    product['SO_delta'] = product['SO'] - product['SO_LY']
    product['SI_growth'] = product['SI_delta'] / product['SI_LY'].abs()
    product['SO_growth'] = product['SO_delta'] / product['SO_LY'].abs()
    product['SISO_ratio'] = product['SI'] / product['SO']
    
    return product
```

**核心洞察模板**：
- R产品：若SO > SI → "侧面证明该产品渠道库存健康，存在进一步发展潜力"
- F/C产品：SI和SO均大幅下滑 → "需聚焦头部KA的动销合作"
- 识别"SI下滑 > SO下滑"的产品 → 渠道主动去库存信号

---

## 5. 产品潜力分析

**数据源**：门店sheet（R产品，区分院边店Type）

```python
def analyze_r_product_dtp(df_store):
    """R产品DTP vs 非DTP渠道拆解"""
    r_stores = df_store[df_store['BrandNameE'] == 'R产品'].copy()
    
    # 按城市×渠道类型汇总
    city_channel = r_stores.groupby(['CityNameC', '院边店Type']).agg(
        SO=('PHM_SellOutActual', 'sum'),
        SO_LY=('PHM_SellOutActualLY', 'sum')
    ).reset_index()
    
    city_channel['delta'] = city_channel['SO'] - city_channel['SO_LY']
    city_channel['growth'] = city_channel['delta'] / city_channel['SO_LY'].abs()
    
    # 按城市汇总（用于BCG矩阵定位）
    city_total = r_stores.groupby('CityNameC').agg(
        SO=('PHM_SellOutActual', 'sum'),
        SO_LY=('PHM_SellOutActualLY', 'sum')
    ).reset_index()
    city_total['growth'] = (city_total['SO'] - city_total['SO_LY']) / city_total['SO_LY'].abs()
    
    # BCG矩阵分类
    so_median = city_total['SO'].median()
    growth_median = city_total['growth'].median()
    
    def classify_bcg(row):
        high_so = row['SO'] > so_median
        high_growth = row['growth'] > growth_median
        if high_so and high_growth: return '明星市场'
        if high_so and not high_growth: return '现金牛'
        if not high_so and high_growth: return '问题市场'
        return '低潜市场'
    
    city_total['BCG'] = city_total.apply(classify_bcg, axis=1)
    
    return city_channel, city_total
```

**核心洞察模板**：
- "R产品基本分布在DTP院边店，DTP增长金额远高于社区店"
- "聚焦[长沙/广州]等城市头部DTP连锁，复制成功合作模式"
- BCG矩阵标注：哪些城市是明星（重点投入）、哪些是现金牛（维护）

---

## 6. KA客户健康度诊断

**数据源**：连锁sheet（全年汇总）

```python
def analyze_ka_health(df_chain):
    """核心连锁客户贡献 + 健康度诊断"""
    # 全年汇总（非电商）
    df = df_chain[df_chain['Ecommerce'] == '非电商']
    
    ka = df.groupby('连锁总部').agg(
        SI=('PHM_SellInActual', 'sum'),
        SI_LY=('PHM_SellInActualLY', 'sum'),
        SO=('PHM_SellOutActual', 'sum'),
        SO_LY=('PHM_SellOutActualLY', 'sum')
    ).reset_index()
    
    ka['SI_delta'] = ka['SI'] - ka['SI_LY']
    ka['SO_delta'] = ka['SO'] - ka['SO_LY']
    ka['SO_growth'] = ka['SO_delta'] / ka['SO_LY'].abs()
    ka['SISO'] = ka['SI'] / ka['SO'].replace(0, float('nan'))
    
    # Top下滑客户（按SO delta升序）
    top_declining = ka.nsmallest(10, 'SO_delta')
    
    # 下滑贡献集中度：Top2贡献了多少%
    total_decline = ka[ka['SO_delta'] < 0]['SO_delta'].sum()
    top2_decline = ka.nsmallest(2, 'SO_delta')['SO_delta'].sum()
    concentration = top2_decline / total_decline if total_decline != 0 else 0
    
    # 进销比散点图数据
    scatter_data = ka[['连锁总部', 'SO', 'SISO']].dropna()
    
    return ka, top_declining, concentration, scatter_data
```

**核心洞察模板**：
- "整体下滑并非市场普遍疲软，而是主要由[客户A]和[客户B]造成"
- "两者合计贡献XX%的下滑"
- "其他客户总体能贡献XXXX万增量"（重要的正面信号）
- 散点图象限解读：进销比>1.0 + 高纯销 = 良性蓄水；进销比<1.0 + 高纯销 = 核心伙伴

---

## 7. 城市维度产品分析

**数据源**：连锁sheet（按产品分别做城市拆解）

```python
def analyze_city_product(df_chain, product='F产品'):
    """指定产品的城市表现总览"""
    df = df_chain[df_chain['BrandNameE'] == product]
    
    city = df.groupby('CityNameC').agg(
        SO=('PHM_SellOutActual', 'sum'),
        SO_LY=('PHM_SellOutActualLY', 'sum')
    ).reset_index()
    
    city['delta'] = city['SO'] - city['SO_LY']
    city['growth'] = city['delta'] / city['SO_LY'].abs()
    city = city.sort_values('SO', ascending=False)
    
    return city
```

**F产品核心洞察模板**：
- "[城市]是最大占比且保持增长"（明星守卫）
- "[城市A]和[城市B]虽然体量大，但跌幅惊人，是主要失血点"
- "Top5以外市场整体下跌XX%，说明F产品下滑具有全国性"

**C产品核心洞察模板**：
- "[城市]腰斩式下跌（-XX%），需高度关注"
- "[城市A]和[城市B]逆势增长，证明该产品在一线/新一线城市仍有竞争力"

---

## 分析优先级建议

若时间有限，优先做模块 **1 > 6 > 3 > 5**，这四个模块支撑PPT的核心叙事逻辑。
