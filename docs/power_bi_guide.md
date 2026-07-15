# Power BI 交互式看板搭建指南

> 前提：已运行 `python main.py analyze`，产出在 `outputs/data/` 和 `outputs/figures/` 中。

---

## 方式 A：REST API 一键推送（推荐）

利用 Power BI REST API ，Python 分析完成后自动推送数据集到 Power BI Service，无需手动导入 CSV。

### A.1 一次性配置

#### Step 1：注册 Azure AD 应用

1. 登录 [Azure Portal](https://portal.azure.com/) → Microsoft Entra ID → 应用注册 → 新注册
2. 名称随意（如 `retail-analytics-pbi`），**重定向 URI 选"Web"并填写 `https://login.microsoftonline.com/common/oauth2/nativeclient`**
3. 注册完成后记录 `client_id` 和 `tenant_id`

#### Step 2：创建客户端密码

1. 应用 → 证书和密码 → 新建客户端密码
2. 记录 `client_secret`（只显示一次，务必保存）

#### Step 3：授权 API 权限

1. 应用 → API 权限 → 添加权限 → Power BI Service
2. 勾选 `Dataset.ReadWrite.All` → 添加
3. 点击"代表组织授予管理员同意"（需管理员权限）

#### Step 4：获取工作区 ID

1. 打开 [Power BI Service](https://app.powerbi.com/)
2. 进入目标工作区 → URL 中的 `/groups/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` 即为 `workspace_id`

#### Step 5：配置凭证

两种方式任选其一：

**方式一：环境变量（推荐 CI/CD）**

```powershell
$env:PBI_CLIENT_ID="你的client_id"
$env:PBI_CLIENT_SECRET="你的client_secret"
$env:PBI_TENANT_ID="你的tenant_id"
$env:PBI_WORKSPACE_ID="你的workspace_id"
```

**方式二：配置文件**

```bash
cp pbi_config.example.json pbi_config.json
# 编辑 pbi_config.json，填入真实凭证
```

### A.2 推送数据

```bash
python main.py analyze   # 先执行分析
python main.py push      # 推送到 Power BI Service
```

推送成功后：
1. 打开 [Power BI Service](https://app.powerbi.com/) → 工作区 → 数据集
2. 找到 `Global_Retail_Analytics` 数据集
3. 点击"创建报表" → 基于在线数据集直接搭建看板
4. 后续数据更新只需 `python main.py analyze && python main.py push` 即可刷新

---

## How to 验证: 没装Python的团队也能快速上手

    - 方案1：Power Query + Power BI Desktop
    - 方案2：Power BI Service 在线看板

## 方式 B：手动 CSV 导入（无需 Azure 配置）

### B.1 打开 Power BI Desktop → 获取数据 → 文本/CSV

依次导入以下文件（`outputs/data/` 目录下）：

| 文件名 | 内容 | 看板用途 |
|--------|------|----------|
| `regional_market.csv` | 各市场销售额/利润/利润率/份额 | 区域销售主表 |
| `regional_region.csv` | 各区域汇总 | 区域层级钻取 |
| `regional_country.csv` | 各国汇总 | 国家层级钻取 |
| `category_category.csv` | 各品类汇总 | 品类分析 |
| `category_sub_category.csv` | 各子品类汇总 | 子品类钻取 |
| `repurchase_customer_segments.csv` | 客户分层统计 | 客户分析 |
| `repurchase_repurchase_summary.csv` | 复购率核心指标 | KPI 卡片 |
| `logistics_ship_mode.csv` | 运输方式物流时效 | 物流分析 |
| `logistics_order_priority.csv` | 订单优先级时效 | 优先级维度 |
| `logistics_delay_analysis.csv` | 延迟订单分布 | 延迟热力图 |

### B.2 关键列说明

| 列名 | 含义 | 建议用途 |
|------|------|----------|
| `Market`/`Region`/`Country` | 区域维度（index列导入后自动为第一列） | 切片器、地图、饼图 |
| `Category`/`Sub-Category` | 品类维度 | 切片器、柱状图 |
| `Total_Sales` | 总销售额 | KPI、趋势图 |
| `Total_Profit` | 总利润 | KPI、对比图 |
| `Avg_Profit_Rate` | 平均利润率 | 条件格式 |
| `Sales_Share` | 销售额占比 | 饼图、树状图 |
| `Is_LowPerformance` | 低效标记（是/否） | 条件格式红色高亮、筛选器 |
| `Is_LowSales` | 低销标记（是/否） | 条件格式、优先级筛选 |
| `Segment` | 客户分层 | 切片器、次数分布 |
| `Ship_Mode` | 运输方式 | 切片器、柱状图 |
| `Avg_ShippingDays` | 平均物流天数 | KPI、趋势图 |
| `Delay_Order_Count` | 延迟订单数 | 热力图、问题聚焦 |

---

## 二、看板页面设计（4 页）

### Page 1：销售总览

| 区域 | 可视化类型 | 数据来源 | 说明 |
|------|-----------|----------|------|
| 顶部 | 卡片（3个） | `regional_market` | 总销售额、总利润、总订单数 |
| 左 | 柱形图 | `regional_market` | Market 销售额 vs 利润双轴 |
| 右 | 饼图 | `regional_market` | 各 Market 销售额占比 |
| 下左 | 地图 | `regional_country` | Country 维度销售额热力图 |
| 下右 | 表 | `regional_market` | 明细表：Market、销售额、利润、利润率、Sales_Share、Is_LowPerformance |

**交互设置**：
- 添加 Market 切片器（下拉单选/多选）
- 表视图对 `Is_LowPerformance = "是"` 行设置条件格式 → 红色背景

### Page 2：品类分析

| 区域 | 可视化类型 | 数据来源 | 说明 |
|------|-----------|----------|------|
| 左 | 树状图 | `category_category` | Category 按 Sales_Share 面积 |
| 右 | 条形图 | `category_sub_category` | Top 15 Sub-Category 销售额 |
| 下左 | 散点图 | `category_sub_category` | 销售额 vs 利润率（按品类着色） |
| 下右 | 表 | `category_sub_category` | 明细表：Sub-Category、销售额、利润、利润率、Avg_Discount、Is_LowSales |

**交互设置**：
- 添加 Category 切片器
- `Is_LowSales = "是"` 行红色高亮 → 一眼定位低销品类
- 散点图 hover 显示具体子品类名称

### Page 3：客户复购

| 区域 | 可视化类型 | 数据来源 | 说明 |
|------|-----------|----------|------|
| 顶部 | 卡片（4个） | `repurchase_repurchase_summary` | 总客户数、复购客户数、复购率、一次性占比 |
| 左 | 饼图 | `repurchase_customer_segments` | Segment 人数占比 |
| 右 | 柱形图 | `repurchase_customer_segments` | 各分层贡献销售额 |
| 下 | 表 | `repurchase_customer_segments` | 明细表：Segment、人数、人均订单、总销售额、平均生命周期 |

### Page 4：物流时效

| 区域 | 可视化类型 | 数据来源 | 说明 |
|------|-----------|----------|------|
| 左 | 柱形图 | `logistics_ship_mode` | Ship Mode 平均物流天数 |
| 右 | 柱形图 | `logistics_order_priority` | Order Priority 平均物流天数 |
| 下左 | 柱形图 | `logistics_delay_analysis` | 各运输方式延迟订单数（P95以上） |
| 下右 | 表 | `logistics_ship_mode` | 明细表：Ship Mode、平均天数、中位数、最大天数 |

**交互设置**：
- 添加 Ship Mode 切片器
- 延迟订单数添加数据标签 → 直观显示问题严重程度

---

## 三、跨页面联动与钻取

### 3.1 切片器联动

所有页面的切片器互相同步：
1. 在 Power BI 中选中任一页面的 Market 切片器
2. 菜单栏 → 格式 → 编辑交互
3. 对其他页面的可视化选择"筛选"（漏斗图标）
4. 这样切换 Market 后，品类、客户、物流页面同步过滤

### 3.2 下钻路径

```
Market(页面1) → 点击某个 Market → 下钻到 Country(页面1下表)
Region → Country 二层下钻
Category(页面2) → 点击某个 Category → Sub-Category 条形图过滤
```

### 3.3 书签导航

在每页添加统一的导航按钮，实现单页应用式的跨页跳转：

1. 插入 → 按钮 → 空白按钮，命名"销售总览"
2. 按钮 → 操作 → 类型"书签"，选择对应页面的书签
3. 复制按钮到每个页面

---

## 四、条件格式与告警

### 4.1 低效/低销红色高亮

对包含 `Is_LowPerformance` / `Is_LowSales` 列的表视觉对象：
1. 格式 → 条件格式 → 背景色
2. 格式样式：规则
3. 字段：`Is_LowPerformance`，值"是" → 红色(#E15759, 透明度30%)

### 4.2 KPI 阈值告警

在 KPI 卡片中：
- 利润率目标：设置目标值为 15%，低于显示红色
- 复购率目标：设置目标值为 30%

---

## 五、数据刷新

每次运行 `python main.py analyze` 后：
1. 打开 Power BI Desktop
2. 主页 → 刷新 → 自动重载所有 CSV
3. 如需自动刷新，将 CSV 放在 OneDrive/SharePoint，配置 Power BI Service 计划刷新

---

## 六、发布与分享

1. Power BI Desktop → 发布 → 选择工作区
2. Power BI Service 中配置仪表板
3. 分享链接给团队成员，支持网页端/移动端查看
4. 支持导出 PDF / PowerPoint
