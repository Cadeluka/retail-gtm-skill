"""
零售RMM GTM战略分析 - 核心计算脚本
用法：python analyze.py <excel_file_path>
输出：JSON格式的各模块分析结果，可直接用于PPT内容填充
"""

import pandas as pd
import json
import sys
import warnings
warnings.filterwarnings('ignore')


def load_data(filepath):
    """读取数据沙盘Excel"""
    xl = pd.read_excel(filepath, sheet_name=None)
    df_chain = xl.get('连锁')
    df_store = xl.get('门店')
    
    if df_chain is None or df_store is None:
        raise ValueError("Excel文件中未找到'连锁'或'门店'Sheet，请检查文件格式")
    
    return df_chain, df_store


def safe_growth(current, prior):
    """安全计算增长率（处理除零和NaN）"""
    if pd.isna(prior) or prior == 0:
        return None
    return (current - prior) / abs(prior)


def fmt_wan(value):
    """格式化为万元（保留1位小数）"""
    return round(value / 10000, 1) if not pd.isna(value) else 0


def fmt_pct(value):
    """格式化百分比"""
    if value is None or pd.isna(value):
        return "N/A"
    return f"{'+' if value > 0 else ''}{value:.1%}"


# ─── 模块1：全年业绩总览 ───────────────────────────────────────────────────

def module1_annual_overview(df_chain):
    df = df_chain.copy()
    
    monthly = df.groupby('YM').agg(
        SI=('PHM_SellInActual', 'sum'),
        SO=('PHM_SellOutActual', 'sum'),
        SI_LY=('PHM_SellInActualLY', 'sum'),
        SO_LY=('PHM_SellOutActualLY', 'sum')
    ).reset_index().sort_values('YM')
    
    total_SI = df['PHM_SellInActual'].sum()
    total_SO = df['PHM_SellOutActual'].sum()
    total_SI_LY = df['PHM_SellInActualLY'].sum()
    total_SO_LY = df['PHM_SellOutActualLY'].sum()
    
    return {
        'kpi': {
            'total_SI_wan': fmt_wan(total_SI),
            'total_SO_wan': fmt_wan(total_SO),
            'SI_yoy': fmt_pct(safe_growth(total_SI, total_SI_LY)),
            'SO_yoy': fmt_pct(safe_growth(total_SO, total_SO_LY)),
            'annual_siso_ratio': round(total_SI / total_SO, 3) if total_SO != 0 else None
        },
        'monthly_trend': monthly.to_dict(orient='records')
    }


# ─── 模块2：区域表现 ──────────────────────────────────────────────────────

def module2_regional(df_chain):
    regional = df_chain.groupby('ProvinceNameC').agg(
        SI=('PHM_SellInActual', 'sum'),
        SI_LY=('PHM_SellInActualLY', 'sum'),
        SO=('PHM_SellOutActual', 'sum'),
        SO_LY=('PHM_SellOutActualLY', 'sum')
    ).reset_index()
    
    regional['SI_delta_wan'] = (regional['SI'] - regional['SI_LY']).apply(fmt_wan)
    regional['SI_growth'] = regional.apply(lambda r: fmt_pct(safe_growth(r['SI'], r['SI_LY'])), axis=1)
    regional['SO_growth'] = regional.apply(lambda r: fmt_pct(safe_growth(r['SO'], r['SO_LY'])), axis=1)
    regional = regional.sort_values('SI_delta_wan', ascending=False)
    
    return regional[['ProvinceNameC', 'SI_delta_wan', 'SI_growth', 'SO_growth']].to_dict(orient='records')


# ─── 模块3：产品季度矩阵 ──────────────────────────────────────────────────

def module3_product_quarterly(df_chain):
    df = df_chain.copy()
    month = df['YM'].astype(str).str[-2:].astype(int)
    df['Quarter'] = pd.cut(month, bins=[0,3,6,9,12], labels=['Q1','Q2','Q3','Q4'])
    
    matrix = df.groupby(['BrandNameE', 'Quarter']).agg(
        SO=('PHM_SellOutActual', 'sum'),
        SO_LY=('PHM_SellOutActualLY', 'sum')
    ).reset_index()
    
    matrix['delta_wan'] = (matrix['SO'] - matrix['SO_LY']).apply(fmt_wan)
    matrix['growth'] = matrix.apply(lambda r: safe_growth(r['SO'], r['SO_LY']), axis=1)
    
    result = {}
    for product in matrix['BrandNameE'].unique():
        prod_data = matrix[matrix['BrandNameE'] == product]
        result[product] = {}
        for _, row in prod_data.iterrows():
            q = str(row['Quarter'])
            result[product][q] = {
                'delta_wan': row['delta_wan'],
                'growth': fmt_pct(row['growth'])
            }
    
    # 全年汇总
    annual = df.groupby('BrandNameE').agg(
        SO=('PHM_SellOutActual', 'sum'),
        SO_LY=('PHM_SellOutActualLY', 'sum')
    ).reset_index()
    annual['delta_wan'] = (annual['SO'] - annual['SO_LY']).apply(fmt_wan)
    annual['growth'] = annual.apply(lambda r: fmt_pct(safe_growth(r['SO'], r['SO_LY'])), axis=1)
    
    for _, row in annual.iterrows():
        if row['BrandNameE'] in result:
            result[row['BrandNameE']]['全年'] = {
                'delta_wan': row['delta_wan'],
                'growth': row['growth']
            }
    
    # Q1+Q2 贡献率
    q1q2 = matrix[matrix['Quarter'].isin(['Q1','Q2'])]['delta_wan'].sum()
    total = matrix['delta_wan'].sum()
    q1q2_contribution = f"{q1q2/total:.0%}" if total != 0 else "N/A"
    
    return {'matrix': result, 'q1q2_contribution': q1q2_contribution}


# ─── 模块4：产品进销配比 ──────────────────────────────────────────────────

def module4_product_siso(df_chain):
    product = df_chain.groupby('BrandNameE').agg(
        SI=('PHM_SellInActual', 'sum'),
        SI_LY=('PHM_SellInActualLY', 'sum'),
        SO=('PHM_SellOutActual', 'sum'),
        SO_LY=('PHM_SellOutActualLY', 'sum')
    ).reset_index()
    
    product['SI_wan'] = product['SI'].apply(fmt_wan)
    product['SO_wan'] = product['SO'].apply(fmt_wan)
    product['SI_delta_wan'] = (product['SI'] - product['SI_LY']).apply(fmt_wan)
    product['SO_delta_wan'] = (product['SO'] - product['SO_LY']).apply(fmt_wan)
    product['SI_growth'] = product.apply(lambda r: fmt_pct(safe_growth(r['SI'], r['SI_LY'])), axis=1)
    product['SO_growth'] = product.apply(lambda r: fmt_pct(safe_growth(r['SO'], r['SO_LY'])), axis=1)
    product['SISO'] = (product['SI'] / product['SO'].replace(0, float('nan'))).round(2)
    
    return product[['BrandNameE','SI_wan','SO_wan','SI_delta_wan','SO_delta_wan',
                     'SI_growth','SO_growth','SISO']].to_dict(orient='records')


# ─── 模块5：产品潜力分析 ──────────────────────────────────────────────────

def module5_r_dtp(df_store):
    r = df_store[df_store['BrandNameE'] == 'R产品'].copy()
    
    # 按城市×渠道类型
    channel = r.groupby(['CityNameC', '院边店Type']).agg(
        SO=('PHM_SellOutActual', 'sum'),
        SO_LY=('PHM_SellOutActualLY', 'sum')
    ).reset_index()
    channel['SO_wan'] = channel['SO'].apply(fmt_wan)
    channel['growth'] = channel.apply(lambda row: fmt_pct(safe_growth(row['SO'], row['SO_LY'])), axis=1)
    
    # 城市汇总 + BCG
    city = r.groupby('CityNameC').agg(
        SO=('PHM_SellOutActual', 'sum'),
        SO_LY=('PHM_SellOutActualLY', 'sum')
    ).reset_index()
    city['SO_wan'] = city['SO'].apply(fmt_wan)
    city['growth_raw'] = city.apply(lambda row: safe_growth(row['SO'], row['SO_LY']), axis=1)
    city['growth'] = city['growth_raw'].apply(fmt_pct)
    
    so_med = city['SO'].median()
    growth_med = city['growth_raw'].median()
    
    def bcg(row):
        h_so = row['SO'] > so_med
        h_g = (row['growth_raw'] or 0) > (growth_med or 0)
        if h_so and h_g: return '明星市场'
        if h_so and not h_g: return '现金牛'
        if not h_so and h_g: return '问题市场'
        return '低潜市场'
    
    city['BCG'] = city.apply(bcg, axis=1)
    city = city.sort_values('SO', ascending=False)
    
    return {
        'city_channel': channel.to_dict(orient='records'),
        'city_bcg': city[['CityNameC','SO_wan','growth','BCG']].to_dict(orient='records')
    }


# ─── 模块6：KA客户健康度 ──────────────────────────────────────────────────

def module6_ka_health(df_chain):
    ka = df_chain.groupby('连锁总部').agg(
        SI=('PHM_SellInActual', 'sum'),
        SI_LY=('PHM_SellInActualLY', 'sum'),
        SO=('PHM_SellOutActual', 'sum'),
        SO_LY=('PHM_SellOutActualLY', 'sum')
    ).reset_index()
    
    ka['SO_delta'] = ka['SO'] - ka['SO_LY']
    ka['SO_delta_wan'] = ka['SO_delta'].apply(fmt_wan)
    ka['SO_wan'] = ka['SO'].apply(fmt_wan)
    ka['SO_growth'] = ka.apply(lambda r: fmt_pct(safe_growth(r['SO'], r['SO_LY'])), axis=1)
    ka['SISO'] = (ka['SI'] / ka['SO'].replace(0, float('nan'))).round(2)
    
    # Top下滑客户
    declining = ka[ka['SO_delta'] < 0].nsmallest(10, 'SO_delta')
    
    # 下滑集中度
    total_decline = ka[ka['SO_delta'] < 0]['SO_delta'].sum()
    top2_decline = ka.nsmallest(2, 'SO_delta')['SO_delta'].sum()
    top2_concentration = fmt_pct(top2_decline / total_decline) if total_decline != 0 else "N/A"
    
    # 其他客户增量
    other_growth = ka[~ka['连锁总部'].isin(ka.nsmallest(2, 'SO_delta')['连锁总部'])]['SO_delta'].sum()
    
    return {
        'top10_declining': declining[['连锁总部','SO_wan','SO_delta_wan','SO_growth','SISO']].to_dict(orient='records'),
        'top2_concentration': top2_concentration,
        'other_clients_growth_wan': fmt_wan(other_growth) if other_growth > 0 else 0,
        'scatter_data': ka[['连锁总部','SO_wan','SISO']].dropna().to_dict(orient='records')
    }


# ─── 模块7：城市维度（F/C产品）─────────────────────────────────────────────

def module7_city_product(df_chain, products=('F产品', 'C产品')):
    result = {}
    for prod in products:
        df = df_chain[df_chain['BrandNameE'] == prod]
        city = df.groupby('CityNameC').agg(
            SO=('PHM_SellOutActual', 'sum'),
            SO_LY=('PHM_SellOutActualLY', 'sum')
        ).reset_index()
        city['SO_wan'] = city['SO'].apply(fmt_wan)
        city['delta_wan'] = (city['SO'] - city['SO_LY']).apply(fmt_wan)
        city['growth'] = city.apply(lambda r: fmt_pct(safe_growth(r['SO'], r['SO_LY'])), axis=1)
        city = city.sort_values('SO', ascending=False)
        result[prod] = city[['CityNameC','SO_wan','delta_wan','growth']].to_dict(orient='records')
    return result


# ─── 主函数 ──────────────────────────────────────────────────────────────

def run_full_analysis(filepath):
    print(f"📊 读取数据：{filepath}")
    df_chain, df_store = load_data(filepath)
    
    print("🔍 执行7个分析模块...")
    results = {
        'module1_annual': module1_annual_overview(df_chain),
        'module2_regional': module2_regional(df_chain),
        'module3_quarterly': module3_product_quarterly(df_chain),
        'module4_siso': module4_product_siso(df_chain),
        'module5_r_dtp': module5_r_dtp(df_store),
        'module6_ka': module6_ka_health(df_chain),
        'module7_city': module7_city_product(df_chain),
    }
    
    print("✅ 分析完成")
    return results


if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else '零售RMM_数据沙盘_虚拟.xlsx'
    results = run_full_analysis(filepath)
    print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
