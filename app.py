import streamlit as st
import requests
import pandas as pd

# 1. 页面基本配置
st.set_page_config(page_title="全球技术服务中心周报", layout="wide", page_icon="📊")

# 2. 飞书凭据与配置
APP_ID = "cli_aa2529e038f81be3"
APP_SECRET = "gKBRXaqMIYKGGqc9RkyH0b11V4Dk4PSY"
APP_TOKEN = "JqHKw49V3izuZKkm9s8ccGwNnmb"

TABLE_ID = "tblfMcfAnXH3luI7"  # 项目全生命周期总表
VIEW_DELIVERY = "vewSu37vul"    # 交付中项目视图
VIEW_MAINT = "vew4u7e0fo"       # 运维中项目视图
VIEW_FINISH = "vewwcbPapg"      # 已完结项目视图

# 安全渲染 HTML 的辅助函数（彻底去除行首空格，防止被 Markdown 当成代码块）
def render_html(html_str):
    cleaned = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)

# 3. 注入同事 HTML 中的完整核心视觉样式
render_html("""
<style>
/* 全局背景微光渐变与网格 */
.stApp {
    background: radial-gradient(60% 52% at 12% 8%,rgba(99,102,241,.16),transparent 70%),
                radial-gradient(55% 46% at 90% 6%,rgba(56,189,248,.15),transparent 70%),
                radial-gradient(58% 50% at 92% 92%,rgba(168,85,247,.15),transparent 70%),
                radial-gradient(55% 46% at 6% 94%,rgba(59,130,246,.15),transparent 70%),
                linear-gradient(135deg,#EEF2FF,#F5F8FF 46%,#FAF5FF) !important;
    font-family: 'PingFang SC','SF Pro Display',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    color: #1E293B;
}

/* 顶部大标题与渐变文字 */
.report-header {
    font-size: 30px;
    font-weight: 800;
    margin-bottom: 20px;
    background: linear-gradient(120deg,#4338CA,#0284C7 50%,#7C3AED);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    display: inline-block;
}

/* 磨砂玻璃卡片 */
.card-stack {
    display: flex;
    flex-direction: column;
    gap: 22px;
}
.card {
    position: relative;
    padding: 24px 28px;
    border-radius: 20px;
    background: rgba(255,255,255,.88);
    border: 1px solid rgba(255,255,255,.95);
    backdrop-filter: blur(22px) saturate(180%);
    -webkit-backdrop-filter: blur(22px) saturate(180%);
    box-shadow: 0 10px 30px rgba(15,23,42,.06);
    transition: transform .25s ease, box-shadow .25s ease;
}
.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 40px rgba(15,23,42,.1);
}

/* 卡片标题与胶囊标签 */
.card-title {
    font-size: 22px;
    font-weight: 800;
    color: #0F172A;
    margin: 0 0 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid #E2E8F0;
}
.tag {
    display: inline-block;
    padding: 3px 12px;
    font-size: 14px;
    font-weight: 700;
    border-radius: 99px;
    color: #312E81;
    background: #EEF2FF;
    border: 1px solid #C7D2FE;
}
.tag-success {
    color: #065F46;
    background: #ECFDF5;
    border-color: #A7F3D0;
}
.tag-muted {
    color: #334155;
    background: #F1F5F9;
    border-color: #CBD5E1;
}

/* 流光动画进度条 */
.progress-wrapper {
    margin: 16px 0 12px;
}
.progress-header {
    display: flex;
    justify-content: space-between;
    font-size: 16px;
    font-weight: 800;
    color: #1E293B;
    margin-bottom: 8px;
}
.progress-bg {
    width: 100%;
    height: 12px;
    border-radius: 99px;
    background: #E2E8F0;
    box-shadow: inset 0 2px 4px rgba(15,23,42,.1);
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    border-radius: 99px;
    position: relative;
    overflow: hidden;
    background: linear-gradient(90deg,#4F46E5,#2563EB,#0284C7,#7C3AED,#4F46E5);
    background-size: 300% 100%;
    animation: flow 4s linear infinite;
}
@keyframes flow {
    to { background-position: 300% 0; }
}

/* 双栏栅格排版 */
.grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    align-items: stretch;
}
@media (max-width: 900px) {
    .grid-2 { grid-template-columns: 1fr; }
}

/* 字段与排版样式 */
.field-row {
    margin-bottom: 12px;
    font-size: 16px;
    line-height: 1.6;
    color: #1E293B;
}
.label {
    color: #3730A3;
    font-weight: 800;
    display: inline-block;
    margin-right: 6px;
}
.value {
    color: #1E293B;
    font-weight: 500;
}
.target-red {
    color: #DC2626;
    font-weight: 700;
}

/* 高亮区块通用 */
.highlight-block {
    padding: 16px 18px;
    border-radius: 16px;
    background: rgba(248,250,252,.92);
    border: 1px solid #E2E8F0;
    border-left: 5px solid #6366F1;
}

/* 运维专属浅蓝高亮区块 */
.highlight-attention {
    border-color: #BFDBFE;
    border-left: 5px solid #1D4ED8;
    background: #EFF6FF;
}
.highlight-attention .label {
    color: #1D4ED8;
}

.risk-text {
    display: block;
    margin-top: 6px;
    padding: 8px 12px;
    border-radius: 10px;
    color: #991B1B;
    font-weight: 700;
    font-size: 15px;
    line-height: 1.5;
    background: #FEE2E2;
    border: 1px solid #FCA5A5;
}

/* 进度说明表格 */
.spec-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin-top: 14px;
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid #E2E8F0;
    background: #fff;
}
.spec-table th, .spec-table td {
    padding: 10px 16px;
    font-size: 15px;
    border-bottom: 1px solid #E2E8F0;
}
.spec-table th {
    font-weight: 800;
    color: #1E1B4B;
    background: #EEF2FF;
}
</style>
""")

# 4. 辅助函数：清洗特殊对象
def clean_cell_value(val):
    if val is None:
        return ""
    if isinstance(val, list):
        texts = []
        for item in val:
            if isinstance(item, dict):
                if "text" in item:
                    texts.append(str(item["text"]))
                elif "name" in item:
                    texts.append(str(item["name"]))
                elif "text_arr" in item and isinstance(item["text_arr"], list):
                    texts.extend([str(t) for t in item["text_arr"] if t])
            elif isinstance(item, (str, int, float)):
                texts.append(str(item))
        return " / ".join(texts) if texts else ""
    return val

# 5. 飞书数据拉取（带缓存）
@st.cache_data(ttl=180)
def fetch_feishu_view(table_id, view_id):
    token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    t_res = requests.post(token_url, json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=10).json()
    if t_res.get("code") != 0:
        return pd.DataFrame()
    token = t_res["tenant_access_token"]
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/records"
    headers = {"Authorization": f"Bearer {token}"}
    
    all_records = []
    page_token = ""
    while True:
        params = {"page_size": 100, "view_id": view_id}
        if page_token:
            params["page_token"] = page_token
        res = requests.get(url, headers=headers, params=params, timeout=15).json()
        if res.get("code") != 0:
            break
        items = res.get("data", {}).get("items", [])
        all_records.extend(items)
        if not res.get("data", {}).get("has_more", False):
            break
        page_token = res.get("data", {}).get("page_token")
        
    if not all_records:
        return pd.DataFrame()
        
    df = pd.DataFrame([r.get("fields", {}) for r in all_records])
    df = df.map(clean_cell_value)
    return df

# 格式化文本与换行
def fmt_txt(val):
    if not val or pd.isna(val) or str(val).strip().lower() in ["none", "nan", ""]:
        return "-"
    return str(val).strip().replace("\r\n", "<br>").replace("\n", "<br>")

# 解析完成进度百分比
def fmt_progress(val):
    if not val or pd.isna(val) or str(val).strip().lower() in ["none", "nan", ""]:
        return 0.0, "0%"
    try:
        num = float(str(val).replace("%", "").strip())
        pct = round(num * 100, 1) if num <= 1.0 else round(num, 1)
        pct_int = int(pct) if pct.is_integer() else pct
        return min(max(pct, 0.0), 100.0), f"{pct_int}%"
    except Exception:
        return 0.0, "0%"

# 6. 顶部布局
col_title, col_btn = st.columns([5, 1])
with col_title:
    render_html('<div class="report-header">📊 GTS 部门周会汇报大屏</div>')
with col_btn:
    if st.button("🔄 刷新最新数据", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 四大分类标签页
tab1, tab2, tab3, tab4 = st.tabs(["📦 交付中项目", "🔧 运维中项目", "🏁 已完结/挂起项目", "📑 其他事项汇总"])

# ==================== Tab 1：交付中项目 ====================
with tab1:
    with st.spinner("正在拉取【交付中项目】最新汇报数据..."):
        df_del = fetch_feishu_view(TABLE_ID, VIEW_DELIVERY)
        
    if df_del.empty:
        st.info("暂未获取到交付中项目数据。")
    else:
        # 顶部 KPI 指标
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("交付事项总数", f"{len(df_del)} 项")
        
        avg_num = 0
        if "完成进度" in df_del.columns:
            nums = [fmt_progress(x)[0] for x in df_del["完成进度"]]
            avg_num = round(sum(nums) / len(nums), 1) if nums else 0
        kpi2.metric("整体平均完成进度", f"{avg_num}%")
        
        bu_cnt = df_del["BU"].nunique() if "BU" in df_del.columns else 1
        kpi3.metric("涉及业务板块", f"{bu_cnt} 个")
        
        st.write("")
        
        # 汇报卡片流
        cards_html = ['<div class="card-stack">']
        for _, row in df_del.iterrows():
            p_name = row.get("项目名称") or "未命名项目"
            bu = row.get("BU") or "爱泊车"
            status = row.get("项目状态") or "交付中"
            
            p_width, p_label = fmt_progress(row.get("完成进度"))
            c_sign = fmt_txt(row.get("合同签订时间"))
            c_acc = fmt_txt(row.get("计划验收时间"))
            c_desc = fmt_txt(row.get("交付内容"))
            c_done = fmt_txt(row.get("已完成事项"))
            
            s_prog = fmt_txt(row.get("项目进度-软件侧"))
            h_prog = fmt_txt(row.get("项目进度-硬件侧"))
            d_supp = fmt_txt(row.get("项目进度-交付支持") or row.get("交付支持"))
            risk = row.get("风险点和协调项")
            
            if risk and str(risk).strip() not in ["-", "", "None", "nan"]:
                risk_html = f'<span class="risk-text">{fmt_txt(risk)}</span>'
            else:
                risk_html = '<span class="value">-</span>'
                
            card_item = f"""
            <div class="card">
                <div class="card-title">
                    <span>{p_name} <span class="tag">{bu}</span></span>
                    <span class="tag tag-success">{status}</span>
                </div>
                <div class="progress-wrapper">
                    <div class="progress-header">
                        <span>整体完成进度</span>
                        <span>{p_label}</span>
                    </div>
                    <div class="progress-bg">
                        <div class="progress-fill" style="width: {p_width}%;"></div>
                    </div>
                </div>
                <div class="grid-2" style="margin-top:16px;">
                    <div>
                        <div class="grid-2" style="gap:12px;margin-bottom:12px;">
                            <div class="field-row"><span class="label">合同签订:</span> <span class="value">{c_sign}</span></div>
                            <div class="field-row"><span class="label">计划验收:</span> <span class="value">{c_acc}</span></div>
                        </div>
                        <div class="field-row"><span class="label">交付内容:</span><br><span class="value">{c_desc}</span></div>
                        <div class="field-row"><span class="label">已完成事项:</span><br><span class="value">{c_done}</span></div>
                    </div>
                    <div class="highlight-block" style="margin-top:0;">
                        <div class="field-row"><span class="label">软件侧进度:</span><br><span class="value">{s_prog}</span></div>
                        <div class="field-row"><span class="label">硬件侧进度:</span><br><span class="value">{h_prog}</span></div>
                        <div class="field-row"><span class="label">交付支持:</span><br><span class="value">{d_supp}</span></div>
                        <div class="field-row" style="margin-bottom:0;"><span class="label">风险协调项:</span><br>{risk_html}</div>
                    </div>
                </div>
            </div>
            """
            cards_html.append(card_item)
            
        cards_html.append('</div>')
        render_html("\n".join(cards_html))
        
        # 底部“项目完成进度”说明对照表
        render_html("""
        <div class="card" style="max-width:760px;margin:32px auto 10px;">
            <div class="card-title" style="border-bottom:none;margin-bottom:0;padding-bottom:0;">“项目完成进度”说明</div>
            <table class="spec-table">
                <tr><th style="width:68px;text-align:center;">序号</th><th>阶段</th><th style="width:150px;text-align:right;">完成占比</th></tr>
                <tr><td style="text-align:center;">1</td><td>产研启动会</td><td style="text-align:right;">5%</td></tr>
                <tr><td style="text-align:center;">2</td><td>服务器初始化</td><td style="text-align:right;">6%--10%</td></tr>
                <tr><td style="text-align:center;">3</td><td>系统部署</td><td style="text-align:right;">11%--30%</td></tr>
                <tr><td style="text-align:center;">4</td><td>全量测试</td><td style="text-align:right;">31%--40%</td></tr>
                <tr><td style="text-align:center;">5</td><td>定制化开发</td><td style="text-align:right;">41%--60%</td></tr>
                <tr><td style="text-align:center;">6</td><td>试运行</td><td style="text-align:right;">61%--80%</td></tr>
                <tr><td style="text-align:center;">7</td><td>商用</td><td style="text-align:right;">81%--90%</td></tr>
                <tr><td style="text-align:center;">8</td><td>初验</td><td style="text-align:right;">91%--95%</td></tr>
                <tr><td style="text-align:center;">9</td><td>终验</td><td style="text-align:right;">96%--100%</td></tr>
            </table>
        </div>
        """)

# ==================== Tab 2：运维中项目（同事卡片样式升级） ====================
with tab2:
    with st.spinner("正在拉取【运维中项目】最新汇报数据..."):
        df_maint = fetch_feishu_view(TABLE_ID, VIEW_MAINT)
        
    if df_maint.empty:
        st.info("暂无运维中项目。")
    else:
        # 顶部 KPI 指标
        m_kpi1, m_kpi2 = st.columns(2)
        m_kpi1.metric("在保运维项目总数", f"{len(df_maint)} 项")
        m_bu_cnt = df_maint["BU"].nunique() if "BU" in df_maint.columns else 1
        m_kpi2.metric("涉及业务板块", f"{m_bu_cnt} 个")
        
        st.write("")
        
        # 运维汇报卡片流
        maint_cards = ['<div class="card-stack">']
        for _, row in df_maint.iterrows():
            p_name = row.get("项目名称") or "未命名项目"
            bu = row.get("BU") or "-"
            
            s_date = fmt_txt(row.get("运维开始时间"))
            e_date = fmt_txt(row.get("运维结束时间"))
            cycle = f"{s_date} ~ {e_date}" if s_date != "-" or e_date != "-" else "- ~ -"
            
            remark = fmt_txt(row.get("备注说明"))
            progress_matters = fmt_txt(row.get("本周进度及关注事项"))
            
            card_item = f"""
            <div class="card">
                <div class="card-title">
                    <span>{p_name} <span class="tag">{bu}</span></span>
                </div>
                <div class="grid-2" style="margin-top:14px;">
                    <div>
                        <div class="field-row"><span class="label">运维周期:</span> <span class="value">{cycle}</span></div>
                        <div class="field-row" style="margin-top:12px;"><span class="label">备注说明:</span><br><span class="value">{remark}</span></div>
                    </div>
                    <div class="highlight-block highlight-attention" style="margin-top:0;">
                        <div class="field-row" style="margin-bottom:0;">
                            <span class="label">本周进度及关注事项:</span><br><br>
                            <span class="value">{progress_matters}</span>
                        </div>
                    </div>
                </div>
            </div>
            """
            maint_cards.append(card_item)
            
        maint_cards.append('</div>')
        render_html("\n".join(maint_cards))

# ==================== Tab 3：已完结/挂起项目（紧凑卡片流） ====================
with tab3:
    with st.spinner("正在拉取【已完结/挂起项目】最新数据..."):
        df_fin = fetch_feishu_view(TABLE_ID, VIEW_FINISH)
        
    if df_fin.empty:
        st.info("暂无已完结或挂起项目。")
    else:
        st.markdown(f"**共计 {len(df_fin)} 个已完结或挂起项目**")
        st.write("")
        
        fin_cards = ['<div class="card-stack">']
        for _, row in df_fin.iterrows():
            p_name = row.get("项目名称") or "未命名项目"
            bu = row.get("BU") or "爱泊车"
            
            # 状态字段兼容判断
            status = row.get("项目状态(完结)") or row.get("项目状态") or "项目结束"
            remark = fmt_txt(row.get("备注说明"))
            
            card_item = f"""
            <div class="card" style="padding: 20px 24px;">
                <div class="card-title" style="padding-bottom: 8px; margin-bottom: 12px;">
                    <span>{p_name} <span class="tag">{bu}</span></span>
                    <span class="tag tag-muted">{status}</span>
                </div>
                <div class="field-row" style="margin-bottom:0;">
                    <span class="label">备注说明:</span> <span class="value">{remark}</span>
                </div>
            </div>
            """
            fin_cards.append(card_item)
            
        fin_cards.append('</div>')
        render_html("\n".join(fin_cards))

# ==================== Tab 4：其他事项汇总（待接入） ====================
with tab4:
    st.info("💡 接下来准备进入第三步：接入【其他事项汇总】（包含客户服务组、IT组、交付研发组的自研产品计划，以及接诉即办 ECharts 环形图）。")
