# Retail Data GTM

面向医药零售业务的 AI GTM 战略分析 Skill。它将原始进销存 Excel 数据转化为可追溯的数据洞察、战略诊断和可执行的增长方案。

本项目不只回答“发生了什么”，还会继续追问：

- 为什么会发生？
- 哪些问题最值得优先解决？
- 应该由谁在什么时间采取什么行动？
- 如何把结论组织成管理层可决策的报告或演示文稿？

## 核心能力

- Sell-in / Sell-out 趋势与进销比分析
- 区域、城市和渠道表现诊断
- KA 客户健康度与风险识别
- 产品季节性、生命周期和组合分析
- 新品上市追踪与老品防守策略
- BCG、MECE、SMART、5 Whys 和优先级矩阵
- GTM 战略、资源配置和实施路线图
- 战略诊断报告、Excel 分析结果和 PPT 故事线

## 工作方法

Skill 采用三阶段分析路径：

```text
原始业务数据
    ↓
数据洞察：发生了什么？
    ↓
战略诊断：为什么发生，什么最重要？
    ↓
解决方案：应该怎么做？
```

分析强调从证据到建议的完整推理链：

```text
数据事实 → 异常或机会 → 根因假设 → 战略问题 → 优先级 → 行动方案
```

## 适用场景

- 季度或年度零售业务回顾
- GTM 策略制定
- 渠道健康度诊断
- KA 客户管理
- 产品组合与资源配置
- 新品上市复盘
- 老品下滑防守
- 医药零售 DTP / 院边店分析
- 管理层汇报和战略 PPT 准备

## 分析模块

### 数据洞察

1. 全年业务表现总览
2. 区域两极对比
3. 产品季节性矩阵
4. 产品进销匹配分析
5. 产品与城市增长潜力
6. KA 客户健康度
7. 城市维度产品表现

### 战略诊断

- 用 SMART 原则定义核心问题
- 用 MECE 和逻辑树拆解议题
- 用“影响力 × 可行性”矩阵确定优先级
- 用 5 Whys 追溯根因
- 区分相关关系、因果关系和待验证假设

### 产品管理

- 产品生命周期判断
- 产品组合健康度评估
- 新品渗透率和增长追踪
- 老品防守与失血市场止损
- 产品竞争定位
- 产品淘汰和资源配置建议

## 目录结构

```text
retail-data-gtm/
├── skill.md
├── README.md
├── references/
│   ├── data-analysis.md
│   ├── ppt-narrative.md
│   ├── product-management.md
│   └── strategic-diagnosis.md
└── scripts/
    └── analyze.py
```

## 安装

### Claude Code

将整个目录放入：

```text
~/.claude/skills/retail-data-gtm/
```

Windows 示例：

```text
C:\Users\<用户名>\.claude\skills\retail-data-gtm\
```

### Codex 或其他 Agent

将目录复制到 Agent 能读取的 skills 目录，并在该 Agent 的技能索引或系统说明中注册 `skill.md`。

## 使用方式

安装后，可以直接向 Agent 提出业务任务并提供 Excel 数据。

示例提示词：

```text
使用 retail-data-gtm 分析这份零售进销数据。
请识别增长机会、渠道风险和 Top 3 战略议题，
并输出管理层摘要、行动计划和 PPT 故事线。
```

```text
分析各产品的 Sell-in / Sell-out、KA 客户健康度和城市表现。
区分数据事实、原因假设和待验证事项，不要把相关性直接写成因果关系。
```

```text
基于这份年度数据制定明年的医药零售 GTM 策略，
明确优先市场、重点客户、资源配置、里程碑和风险。
```

## 数据要求

分析脚本默认读取包含以下工作表的 Excel 文件：

- `连锁`：月度 × 连锁客户 × 产品数据
- `门店`：门店 × 产品数据，可包含 DTP / 院边店分类

核心字段包括：

| 字段 | 含义 |
|---|---|
| `YM` | 年月，建议使用 `YYYYMM` |
| `ProvinceNameC` | 省份 |
| `CityNameC` | 城市 |
| `BrandNameE` | 产品名称 |
| `Ecommerce` | 是否为电商渠道 |
| `连锁总部` | 连锁客户标识 |
| `TargetInsType` | 覆盖类型 |
| `院边店Type` | 门店类型 |
| `PHM_SellInActual` | 本期 Sell-in |
| `PHM_SellInActualLY` | 上年同期 Sell-in |
| `PHM_SellOutActual` | 本期 Sell-out |
| `PHM_SellOutActualLY` | 上年同期 Sell-out |

字段名称或数据结构不一致时，应先完成映射和口径确认，再运行分析。

## 运行分析脚本

安装 Python 依赖：

```bash
pip install pandas openpyxl
```

运行：

```bash
python scripts/analyze.py path/to/retail-data.xlsx
```

脚本会输出 JSON 格式的分析结果，供报告、工作簿或 PPT 内容生成使用。

## 预期产出

根据任务范围，可生成：

- 战略诊断 Markdown / Word 报告
- 多工作表 Excel 分析结果
- 18–22 页管理层战略演示
- GTM 行动清单
- 实施路线图与里程碑
- 风险登记表
- 30 秒电梯陈述

## 分析原则

本 Skill 遵循以下质量标准：

- 每项关键结论必须有数据支持
- 明确数据范围、定义、计算口径和假设
- 不将单月波动直接判断为长期趋势
- 不将相关性直接解释为因果关系
- 同时报告绝对值、相对变化和比较基准
- 每项建议应包含责任人、时间、资源和衡量指标
- 数据不足时明确标注，不虚构结论

## 方法论

本项目综合使用：

- McKinsey 7-Step Problem Solving
- Pyramid Principle
- MECE
- BCG Matrix
- SMART Goals
- 5 Whys
- Impact × Feasibility Matrix

## 隐私与合规

零售数据可能包含客户、销售、库存、渠道和商业策略等敏感信息。

- 不要向公开仓库提交真实业务数据
- 不要提交客户名称、合同价格或个人信息
- 示例数据应先匿名化或使用合成数据
- 使用云端模型前，应遵守所在组织的数据安全政策
- AI 生成的策略建议应由业务负责人复核后再用于决策

建议在仓库中加入以下 `.gitignore` 规则：

```gitignore
*.xlsx
*.xls
*.csv
data/
output/
__pycache__/
*.pyc
```

## 版本

当前版本：`3.0.0`

## License

当前 Skill 标注为内部使用。在公开发布、转载或商业使用前，请由项目维护者补充明确的开源许可证和授权范围。

