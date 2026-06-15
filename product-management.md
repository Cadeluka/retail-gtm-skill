# 产品管理模块详解

> **目标**：医药零售市场产品全生命周期管理
> **定位**：从数据分析到战略决策的产品管理框架

---

## 目录
1. [产品生命周期分析](#1-产品生命周期分析)
2. [产品组合优化](#2-产品组合优化)
3. [新品上市追踪](#3-新品上市追踪)
4. [老品防守策略](#4-老品防守策略)
5. [产品竞争定位](#5-产品竞争定位)
6. [产品淘汰决策](#6-产品淘汰决策)
7. [产品资源配置](#7-产品资源配置)

---

## 1. 产品生命周期分析

**业务问题**：各产品处于生命周期的哪个阶段？如何差异化策略？

**数据源**：连锁sheet（月度时序数据）

**分析方法**：
```python
def analyze_product_lifecycle(df_chain):
    """
    基于BCG矩阵 + 产品生命周期双维度分类

    X轴：市场份额增长（Sell-out YoY）
    Y轴：市场增长率（品类整体增速）
    """
    products = df_chain.groupby('BrandNameE').agg({
        'PHM_SellOutActual': 'sum',
        'PHM_SellOutActualLY': 'sum'
    }).reset_index()

    products['growth_rate'] = (products['PHM_SellOutActual'] -
                               products['PHM_SellOutActualLY']) / products['PHM_SellOutActualLY']
    products['market_share'] = products['PHM_SellOutActual'] / products['PHM_SellOutActual'].sum()

    # 生命周期分类
    def classify_lifecycle(row):
        if row['growth_rate'] > 0.15:
            return '成长期'
        elif row['growth_rate'] > 0.05:
            return '成熟期'
        elif row['growth_rate'] > -0.05:
            return '饱和期'
        else:
            return '衰退期'

    products['lifecycle_stage'] = products.apply(classify_lifecycle, axis=1)

    return products
```

**输出物**：
- 产品生命周期矩阵图（4象限）
- 各产品阶段特征总结
- 阶段迁移预警（例如：F产品从成熟期进入饱和期）

---

## 2. 产品组合优化

**业务问题**：当前产品资源配置是否合理？哪些产品需要加码/削减？

**核心指标**：
```python
# 产品组合健康度评分
def portfolio_health_score(product_df):
    """
    综合评分（0-100分）

    维度1：营收贡献度（40%）
    - 占总Sell-out的比例

    维度2：增长健康度（30%）
    - YoY增长率（负增长扣分）

    维度3：渠道健康度（20%）
    - SI/SO比值（0.8-1.2最优）

    维度4：覆盖广度（10%）
    - 覆盖城市数量 / 总城市数
    """
    scores = {}
    for product in ['F产品', 'C产品', 'R产品', 'N产品', 'B产品']:
        revenue_contribution = ...
        growth_health = ...
        channel_health = ...
        coverage_breadth = ...

        scores[product] = (
            revenue_contribution * 0.4 +
            growth_health * 0.3 +
            channel_health * 0.2 +
            coverage_breadth * 0.1
        )

    return scores
```

**输出物**：
- 产品组合评分矩阵
- 资源配置建议（加码/维持/削减）
- 产品组合重构方案（例如：削减N产品资源，向R产品倾斜）

---

## 3. 新品上市追踪

**业务问题**：R产品上市后表现如何？哪些城市/渠道需要调整？

**核心指标**：
```python
def track_new_product_launch(df_chain, new_product='R产品'):
    """
    新品上市追踪看板

    指标1：上市渗透率
    - 已覆盖城市 / 目标城市数
    - 已覆盖连锁 / 目标连锁数

    指标2：上市增速
    - 月度Sell-out增长曲线
    - vs同类新品benchmark

    指标3：渠道接受度
    - DTP渠道vs院边店vs非院边店的占比
    - Top 10 early adopter连锁

    指标4：复购健康度
    - 连锁客户连续3个月采购比例
    - 连续2个月无采购客户清单
    """
    # 渗透率分析
    city_penetration = df_chain[df_chain['BrandNameE'] == new_product]['CityNameC'].nunique()

    # 增速曲线
    monthly_trend = df_chain[df_chain['BrandNameE'] == new_product] \
        .groupby('YM')['PHM_SellOutActual'].sum()

    # 渠道分布
    channel_mix = df_chain[df_chain['BrandNameE'] == new_product] \
        .groupby('院边店Type')['PHM_SellOutActual'].sum()

    return {
        'penetration': city_penetration,
        'growth_curve': monthly_trend,
        'channel_mix': channel_mix
    }
```

**输出物**：
- 新品上市仪表盘（4个核心指标）
- 渗透地图（已覆盖城市heatmap）
- Early adopter画像（Top 10连锁特征）

---

## 4. 老品防守策略

**业务问题**：F/C产品下滑趋势如何防守？哪些市场是失血点？

**防守战术框架**：
```python
def defend_mature_products(df_chain, mature_products=['F产品', 'C产品']):
    """
    老品防守三战术

    战术1：头部市场锁定
    - 识别Top 20%贡献城市 → 重点资源保护
    - 设置下滑预警线（例如：YoY < -10%）

    战术2：失血市场止损
    - 识别下滑最快的Bottom 20%城市
    - 分析下滑原因（渠道竞争 vs 市场萎缩）

    战术3：成功模式复制
    - 识别正向增长城市（YoY > 5%）
    - 提取成功因素（渠道策略/促销力度）
    - 向同类城市推广
    """

    # 头部市场锁定
    top_cities = df_chain[df_chain['BrandNameE'].isin(mature_products)] \
        .groupby('CityNameC')['PHM_SellOutActual'].sum() \
        .nlargest(10)

    # 失血市场识别
    city_yoy = df_chain[df_chain['BrandNameE'].isin(mature_products)] \
        .groupby('CityNameC').apply(lambda x: (x['PHM_SellOutActual'].sum() -
                                               x['PHM_SellOutActualLY'].sum()) /
                                      x['PHM_SellOutActualLY'].sum())

    bleeding_cities = city_yoy[city_yoy < -0.10]  # 下滑超过10%

    # 成功模式提取
    growing_cities = city_yoy[city_yoy > 0.05]

    return {
        'top_cities_lock': top_cities,
        'bleeding_cities_stop': bleeding_cities,
        'success_patterns_replicate': growing_cities
    }
```

**输出物**：
- F/C产品防守作战地图
- 头部城市保护清单
- 失血城市止损方案
- 成功城市复制手册

---

## 5. 产品竞争定位

**业务问题**：各产品在细分市场的竞争地位如何？如何差异化？

**竞争分析框架**：
```python
def competitive_positioning(df_chain):
    """
    产品竞争定位矩阵

    维度1：市场规模
    - 产品年销售额
    - 市场总量估算（如果有外部数据）

    维度2：增长速度
    - YoY增长率
    - vs市场平均增速

    维度3：渠道依赖
    - Top 5连锁占比（集中度风险）
    - 渠道广度（覆盖城市数）

    维度4：价格带
    - 如果有价格数据：单位价格分析
    - 价格带分布（高端/中端/入门）
    """

    # 市场规模排名
    market_size_ranking = df_chain.groupby('BrandNameE')['PHM_SellOutActual'].sum()

    # 增长速度排名
    growth_ranking = df_chain.groupby('BrandNameE').apply(
        lambda x: (x['PHM_SellOutActual'].sum() - x['PHM_SellOutActualLY'].sum()) /
                 x['PHM_SellOutActualLY'].sum()
    )

    # 渠道集中度风险
    concentration_risk = {}
    for product in df_chain['BrandNameE'].unique():
        product_data = df_chain[df_chain['BrandNameE'] == product]
        top5_share = product_data.groupby('连锁总部')['PHM_SellOutActual'].sum() \
            .nlargest(5).sum() / product_data['PHM_SellOutActual'].sum()
        concentration_risk[product] = top5_share

    return {
        'size_ranking': market_size_ranking,
        'growth_ranking': growth_ranking,
        'concentration_risk': concentration_risk
    }
```

**输出物**：
- 产品竞争定位矩阵（4象限：明星/现金牛/问题/瘦狗）
- 竞争风险评估（高集中度 = 高风险）
- 差异化策略建议

---

## 6. 产品淘汰决策

**业务问题**：哪些产品应该考虑退市？如何平稳过渡？

**淘汰评估框架**：
```python
def evaluate_product_retirement(df_chain):
    """
    产品淘汰决策树

    评估维度1：财务表现
    - 连续3个季度YoY下滑 > 15%？
    - 占总营收 < 5%？

    评估维度2：增长潜力
    - 市场萎缩（品类整体下滑）？
    - 无新产品计划？

    评估维度3：渠道反馈
    - 连锁客户退货率？
    - 渠道主动推单意愿？

    评估维度4：战略价值
    - 是否为引流产品？
    - 是否为组合配套产品？

    决策建议：
    - 立即淘汰：4个维度全部不达标
    - 逐步淘汰：3个维度不达标
    - 观察保留：2个维度不达标
    - 继续投入：≤1个维度不达标
    """

    # 财务表现评估
    for product in df_chain['BrandNameE'].unique():
        product_data = df_chain[df_chain['BrandNameE'] == product]
        # 计算连续季度下滑
        # 计算营收占比
        # ...

    return retirement_recommendations
```

**输出物**：
- 产品淘汰评估矩阵
- 分阶段退市计划
- 替代产品方案

---

## 7. 产品资源配置

**业务问题**：有限的销售/市场资源应该如何分配给各产品？

**资源分配模型**：
```python
def resource_allocation_optimization(df_chain):
    """
    基于BCG矩阵 + 生命周期的资源分配模型

    分配原则：
    1. 明星产品（高增长+高份额）：资源加码（40%预算）
    2. 金牛产品（低增长+高份额）：维持（30%预算）
    3. 问题产品（高增长+低份额）：选择性投入（20%预算）
    4. 瘦狗产品（低增长+低份额）：削减（10%预算）

    资源类型：
    - 销售人力配置（RPM FTE分配）
    - 市场推广费用（促销预算）
    - 渠道激励政策（返点比例）
    """

    # 产品BCG分类
    products_bcg = classify_bcg_matrix(df_chain)

    # 资源分配建议
    allocation_plan = {
        '明星产品': {'budget_share': 0.4, 'headcount_priority': '高'},
        '金牛产品': {'budget_share': 0.3, 'headcount_priority': '中'},
        '问题产品': {'budget_share': 0.2, 'headcount_priority': '低'},
        '瘦狗产品': {'budget_share': 0.1, 'headcount_priority': '最低'}
    }

    return allocation_plan
```

**输出物**：
- 产品资源分配矩阵
- 销售人力配置建议
- 市场费用分配方案
- ROI预估

---

## 与现有分析模块的集成

### 集成点1：与Step 2（7个核心分析模块）联动
- **模块3：产品季度矩阵** → 扩展为 **产品生命周期分析**
- **模块4：产品进销配比** → 输入到 **产品组合优化**

### 集成点2：与Step 3（PPT叙事）联动
- **Part 2新增**：产品管理洞察章节（2-3张）
  - 产品生命周期矩阵图
  - 资源配置建议

### 集成点3：与Step 5（生成PPT）联动
- 使用mck-ppt-design的BCG矩阵图
- 使用组合分析图表（portfolio waterfall）

---

## 待扩展方向（基于案例迭代）

**方向1：定价策略**
- 如果未来有价格数据，可添加产品定价分析模块
- 价格弹性分析 vs 竞品价格对比

**方向2：产品组合协同效应**
- 分析产品间的捆绑销售效应
- 客户购买产品组合分析

**方向3：新产品规划**
- 基于市场gap的新品机会识别
- 新品上市前的市场测试设计

---

## 案例迭代计划

**当前版本**：v1.0 - 基础产品管理框架
**待完善**：基于真实案例不断丰富

**案例收集方向**：
1. 老品下滑防守案例（F产品如何止损）
2. 新品上市成功案例（R产品DTP突破）
3. 产品组合优化案例（资源重新分配决策）
4. 产品淘汰决策案例（N产品退市评估）

随着案例积累，这个模块将成为医药零售产品管理的实战知识库。
