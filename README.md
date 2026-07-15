# 全球零售运营数据分析与可视化决策看板

## 快速开始

```bash
pip install -r requirements.txt
python main.py analyze    # 全量分析（清洗 → 四维分析 → 图表 → 报告）
streamlit run app.py      # 启动自托管交互式看板 → http://localhost:8501
```

## 可视化看板（三种方式）

| 方式 | 命令 | 部署 | 依赖 |
|------|------|------|------|
| **Streamlit 自托管**（推荐） | `streamlit run app.py` | 自己服务器 | 仅需 Python |
| Power BI API 推送 | `python main.py push` | Power BI Service (云) | Azure AD |
| Power BI 手动导入 | 导入 `outputs/data/*.csv` | Power BI Desktop | 无 |

### Streamlit 看板特性

- 侧边栏全局筛选器：Market / Category / Ship Mode 联动
- 4 个分析页面：销售总览、品类分析、客户复购、物流时效
- Plotly 交互图表：支持缩放、hover 详情、图例切换
- 低效/低销红色高亮预警
- 部署到自己服务器，团队浏览器直接访问

## 项目结构

```
├── app.py                     # Streamlit 看板入口
├── main.py                    # CLI 入口 (analyze / report / push)
├── setup.py / requirements.txt
│
├── pages/                     # Streamlit 多页面
│   ├── 1_销售总览.py
│   ├── 2_品类分析.py
│   ├── 3_客户复购.py
│   └── 4_物流时效.py
│
├── data/
│   ├── raw/                   # 原始数据 (Excel + CSV)
│   └── processed/             # 清洗后缓存
│
├── src/
│   ├── config.py
│   ├── data/make_dataset.py   # 数据清洗
│   ├── analysis/dimensions.py # 四维分析 + 问题定位
│   ├── visualization/visualize.py  # Matplotlib 静态图表
│   ├── dashboard/loader.py    # Streamlit 数据加载
│   └── powerbi/               # Power BI REST API 推送
│       ├── auth.py
│       └── push_data.py
│
├── outputs/
│   ├── data/                  # 分析结果 CSV
│   ├── reports/               # 分析报告
│   └── figures/               # 图表 PNG
│
├── docs/
│   └── power_bi_guide.md      # Power BI + Azure 配置指南
│
└── tests/
    └── test_pipeline.py
```

## 四大分析维度

| 维度 | 核心指标 | 产出 |
|------|---------|------|
| 区域销售 | Market/Region/Country 销售额、利润、利润率 | 低效区域标记 |
| 品类销量 | Category/Sub-Category 销量、利润、份额 | 低销品类标记 |
| 客户复购 | 客户分层(高频/中频/低频/一次性) + 复购率 | 复购指标表 |
| 物流时效 | Ship Mode 平均天数、高延迟订单分布 | 延迟渠道标记 |

## 闭环机制

- `data/processed/` 缓存清洗数据，二次运行跳过清洗
- `outputs/data/` 保存分析结果 CSV，`report` / Streamlit 直接复用
- Streamlit `@st.cache_data` 1小时缓存，同一次会话数据只加载一次
- 全流程日志记录时间与关键指标
