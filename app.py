import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import json

# 1. 页面基本设置
st.set_page_config(page_title="全球技术服务中心周报", layout="wide", page_icon="📊")

# 2. 飞书凭据与多表配置
APP_ID = "cli_aa2529e038f81be3"
APP_SECRET = "gKBRXaqMIYKGGqc9RkyH0b11V4Dk4PSY"
APP_TOKEN = "JqHKw49V3izuZKkm9s8ccGwNnmb"

# 表格 1：项目全生命周期总表
TABLE_LIFE_ID = "tblfMcfAnXH3luI7"
VIEW_DELIVERY = "vewSu37vul"    # 交付中项目
VIEW_MAINT = "vew4u7e0fo"       # 运维中项目
VIEW_FINISH = "vewwcbPapg"      # 已完结/挂起项目

# 表格 2：GTS自研产品与重点专项
TABLE_DEV_ID = "tblYtSIkGK07Na1M"
VIEW_DEV_PROD = "vewV4IWr91"    # 自研产品
VIEW_DEV_SPEC = "vew1aFFPXR"    # 重点专项

# 表格 3：部门非交付事项
TABLE_NON_DEL_ID = "tbl9DVGuvIB6dOas"
VIEW_NON_DEL = "vewCXHSZWx"

# 表格 4：接诉即办专项分析
TABLE_COMPLAINT_ID = "tblGj9QwAXsYOOrn"
VIEW_COMPLAINT = "vewiedoaqM"

# 安全渲染 HTML 的辅助函数（消除缩进空格，防止被 Markdown 误识别为代码块）
def render_html(html_str):
    cleaned = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)

# 3. 注入完整 UI 样式
render_html("""
<style>
.stApp {
    background: radial-gradient(60% 52% at 12% 8%,rgba(99,102,241,.16),transparent 70%),
                radial-gradient(55% 46% at 90% 6%,rgba(56,189,248,.15),transparent 70%),
                radial-gradient(58% 50% at 92% 92%,rgba(168,85,247,.15),transparent 70%),
                radial-gradient(55% 46% at 6% 94%,rgba(59,130,246,.15),transparent 70%),
                linear-gradient(135deg,#EEF2FF,#F5F8FF 46%,#FAF5FF) !important;
    font-family: 'PingFang SC','SF Pro Display',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    color: #1E293B;
}
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
.section-title {
    font-size: 24px;
    font-weight: 800;
    padding-bottom: 10px;
    margin: 32px 0 18px;
    position: relative;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-title:first-child { margin-top: 6px; }
.section-title::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: 0;
    width: 72px;
    height: 4px;
    border-radius: 4px;
    background: linear-gradient(90deg,#4F46E5,#0284C7);
}
.grad-text {
    background: linear-gradient(120deg,#4338CA,#0284C7 50%,#7C3AED);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}
.card-stack { display: flex; flex-direction: column; gap: 22px; }
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
.card:hover { transform: translateY(-2px); box-shadow: 0 16px 40px rgba(15,23,42,.1); }
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
.product-title {
    font-size: 23px;
    font-weight: 800;
    background: linear-gradient(120deg,#4338CA,#0284C7);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}
.block-title { margin: 0 0 18px; font-size: 22px; font-weight: 800; color: #0F172A; }
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
.tag-success { color: #065F46; background: #ECFDF5; border-color: #A7F3D0; }
.tag-muted { color: #334155; background: #F1F5F9; border-color: #CBD5E1; }
.progress-wrapper { margin: 16px 0 12px; }
.progress-header { display: flex; justify-content: space-between; font-size: 16px; font-weight: 800; color: #1E293B; margin-bottom: 8px; }
.progress-bg { width: 100%; height: 12px; border-radius: 99px; background: #E2E8F0; box-shadow: inset 0 2px 4px rgba(15,23,42,.1); overflow: hidden; }
.progress-fill {
    height: 100%;
    border-radius: 99px;
    position: relative;
    overflow: hidden;
    background: linear-gradient(90deg,#4F46E5,#2563EB,#0284C7,#7C3AED,#4F46E5);
    background-size: 300% 100%;
    animation: flow 4s linear infinite;
}
@keyframes flow { to { background-position: 300% 0; } }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: stretch; }
@media (max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } }
.field-row { margin-bottom: 12px; font-size: 16px; line-height: 1.6; color: #1E293B; }
.label { color: #3730A3; font-weight: 800; display: inline-block; margin-right: 6px; }
.value { color: #1E293B; font-weight: 500; }
.highlight-block { padding: 16px 18px; border-radius: 16px; background: rgba(248,250,252,.92); border: 1px solid #E2E8F0; border-left: 5px solid #6366F1; }
.highlight-attention { border-color: #BFDBFE; border-left: 5px solid #1D4ED8; background: #EFF6FF; }
.highlight-attention .label { color: #1D4ED8; }
.highlight-plan { border-color: #BBF7D0; border-left: 5px solid #047857; background: #F0FDF4; }
.highlight-plan .label { color: #047857; }
.risk-text { display: block; margin-top: 6px; padding: 8px 12px; border-radius: 10px; color: #991B1B; font-weight: 700; font-size: 15px; line-height: 1.5; background: #FEE2E2; border: 1px solid #FCA5A5; }
.img-container img {
    width: 100%;
    max-height: 440px;
    object-fit: contain;
    border-radius: 16px;
    margin-top: 16px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 8px 24px rgba(15,23,42,.08);
    background: #fff;
}
.spec-table { width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 14px; border-radius: 14px; overflow: hidden; border: 1px solid #E2E8F0; background: #fff; box-shadow: 0 6px 20px rgba(15,23,42,.04); }
.spec-table th, .spec-table td { padding: 12px 18px; font-size: 15px; line-height: 1.6; border-bottom: 1px solid #E2E8F0; }
.spec-table th { font-weight: 800; color: #1E1B4B; background: #EEF2FF; }
.ct0 { border-bottom: 0 !important; margin-bottom: 0 !important; padding-bottom: 0 !important; }
.mt12 { margin-top: 12px; }
</style>
""")

# 4. 字段清洗与辅助函数
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
                elif "url" in item:
                    texts.append(str(item["url"]))
            elif isinstance(item, (str, int, float)):
                texts.append(str(item))
        return " / ".join(texts) if texts else ""
    return val

@st.cache_data(ttl=180)
def fetch_feishu_view(table_id, view_id=None):
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
        params = {"page_size": 100}
        if view_id:
            params["view_id"] = view_id
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
        
    # 保留原始 fields 并做字符串清洗
    cleaned_rows = []
    for r in all_records:
        raw_f = r.get("fields", {})
        row = {}
        for k, v in raw_f.items():
            row[k] = clean_cell_value(v)
        cleaned_rows.append(row)
    return pd.DataFrame(cleaned_rows)

def fmt_txt(val):
    if not val or pd.isna(val) or str(val).strip().lower() in ["none", "nan", ""]:
        return "-"
    return str(val).strip().replace("\r\n", "<br>").replace("\n", "<br>")

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

def normalize_group_name(val):
    """小组名称模糊对齐"""
    s = str(val).strip() if val else ""
    if "客服" in s or "客户" in s:
        return "客户服务组"
    if "IT" in s or "it" in s:
        return "IT组"
    if "一组" in s or "研发一" in s:
        return "交付研发一组"
    if "二组" in s or "研发二" in s:
        return "交付研发二组"
    if "数据" in s:
        return "数据处理组"
    return s

def find_column(df, candidates):
    """根据候选字段名动态匹配列"""
    for cand in candidates:
        if cand in df.columns:
            return cand
    for col in df.columns:
        for cand in candidates:
            if cand in str(col):
                return col
    return None

def extract_image_url(row):
    """提取图片 URL（支持“统计图”与“统计图-图片”）"""
    for col in ["统计图", "统计图-图片", "图片", "图表"]:
        if col in row and row[col]:
            val = str(row[col]).strip()
            if val.startswith("http://") or val.startswith("https://"):
                return val
    return None

# 5. 顶部布局
col_title, col_btn = st.columns([5, 1])
with col_title:
    render_html('<div class="report-header">📊 GTS 部门周会汇报大屏</div>')
with col_btn:
    if st.button("🔄 刷新最新数据", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["📦 交付中项目", "🔧 运维中项目", "🏁 已完结/挂起项目", "📑 其他事项汇总"])

# ==================== Tab 1：交付中项目 ====================
with tab1:
    with st.spinner("正在拉取【交付中项目】..."):
        df_del = fetch_feishu_view(TABLE_LIFE_ID, VIEW_DELIVERY)
    if df_del.empty:
        st.info("暂未获取到交付中项目数据。")
    else:
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
            risk_html = f'<span class="risk-text">{fmt_txt(risk)}</span>' if (risk and str(risk).strip() not in ["-", "", "None", "nan"]) else '<span class="value">-</span>'
            
            cards_html.append(f"""
            <div class="card">
                <div class="card-title">
                    <span>{p_name} <span class="tag">{bu}</span></span>
                    <span class="tag tag-success">{status}</span>
                </div>
                <div class="progress-wrapper">
                    <div class="progress-header"><span>整体完成进度</span><span>{p_label}</span></div>
                    <div class="progress-bg"><div class="progress-fill" style="width: {p_width}%;"></div></div>
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
            """)
        cards_html.append('</div>')
        render_html("\n".join(cards_html))
        
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

# ==================== Tab 2：运维中项目 ====================
with tab2:
    with st.spinner("正在拉取【运维中项目】..."):
        df_maint = fetch_feishu_view(TABLE_LIFE_ID, VIEW_MAINT)
    if df_maint.empty:
        st.info("暂无运维中项目。")
    else:
        m_kpi1, m_kpi2 = st.columns(2)
        m_kpi1.metric("在保运维项目总数", f"{len(df_maint)} 项")
        m_bu_cnt = df_maint["BU"].nunique() if "BU" in df_maint.columns else 1
        m_kpi2.metric("涉及业务板块", f"{m_bu_cnt} 个")
        st.write("")
        maint_cards = ['<div class="card-stack">']
        for _, row in df_maint.iterrows():
            p_name = row.get("项目名称") or "未命名项目"
            bu = row.get("BU") or "-"
            s_date = fmt_txt(row.get("运维开始时间"))
            e_date = fmt_txt(row.get("运维结束时间"))
            cycle = f"{s_date} ~ {e_date}" if s_date != "-" or e_date != "-" else "- ~ -"
            remark = fmt_txt(row.get("备注说明"))
            progress_matters = fmt_txt(row.get("本周进度及关注事项"))
            maint_cards.append(f"""
            <div class="card">
                <div class="card-title"><span>{p_name} <span class="tag">{bu}</span></span></div>
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
            """)
        maint_cards.append('</div>')
        render_html("\n".join(maint_cards))

# ==================== Tab 3：已完结/挂起项目 ====================
with tab3:
    with st.spinner("正在拉取【已完结/挂起项目】..."):
        df_fin = fetch_feishu_view(TABLE_LIFE_ID, VIEW_FINISH)
    if df_fin.empty:
        st.info("暂无已完结或挂起项目。")
    else:
        st.markdown(f"**共计 {len(df_fin)} 个已完结或挂起项目**")
        st.write("")
        fin_cards = ['<div class="card-stack">']
        for _, row in df_fin.iterrows():
            p_name = row.get("项目名称") or "未命名项目"
            bu = row.get("BU") or "爱泊车"
            status = row.get("项目状态(完结)") or row.get("项目状态") or "项目结束"
            remark = fmt_txt(row.get("备注说明"))
            fin_cards.append(f"""
            <div class="card" style="padding: 20px 24px;">
                <div class="card-title" style="padding-bottom: 8px; margin-bottom: 12px;">
                    <span>{p_name} <span class="tag">{bu}</span></span>
                    <span class="tag tag-muted">{status}</span>
                </div>
                <div class="field-row" style="margin-bottom:0;">
                    <span class="label">备注说明:</span> <span class="value">{remark}</span>
                </div>
            </div>
            """)
        fin_cards.append('</div>')
        render_html("\n".join(fin_cards))

# ==================== Tab 4：其他事项汇总（动态合并 3 个表格） ====================
with tab4:
    with st.spinner("正在从飞书 3 个子表动态聚合最新数据..."):
        # 拉取表格 2：自研产品与重点专项（合并两视图）
        df_prod = fetch_feishu_view(TABLE_DEV_ID, VIEW_DEV_PROD)
        df_spec = fetch_feishu_view(TABLE_DEV_ID, VIEW_DEV_SPEC)
        df_dev_all = pd.concat([df_prod, df_spec], ignore_index=True) if (not df_prod.empty or not df_spec.empty) else pd.DataFrame()
        
        # 拉取表格 3：部门非交付事项
        df_non_del = fetch_feishu_view(TABLE_NON_DEL_ID, VIEW_NON_DEL)
        
        # 拉取表格 4：接诉即办专项分析
        df_complaint = fetch_feishu_view(TABLE_COMPLAINT_ID, VIEW_COMPLAINT)

    # 识别表格 2 字段
    col_dev_name = find_column(df_dev_all, ["产品/专项名称", "产品名称", "专项名称", "名称"])
    col_dev_cat = find_column(df_dev_all, ["分类", "类别"])
    col_dev_cur = find_column(df_dev_all, ["本周进度与建设情况", "本周进度", "建设情况"])
    col_dev_next = find_column(df_dev_all, ["下周工作计划", "下周计划", "工作计划"])
    col_dev_group = find_column(df_dev_all, ["负责小组", "小组", "部门", "组别"])

    # 识别表格 3 字段
    col_nd_group = find_column(df_non_del, ["负责小组", "小组", "部门", "组别"])
    col_nd_content = find_column(df_non_del, ["部门事项汇总", "事项汇总", "本周事项", "内容", "工作汇总"])

    # 预定义 5 大团队顺序
    groups_order = ["客户服务组", "IT组", "交付研发一组", "数据处理组", "交付研发二组"]

    for grp in groups_order:
        render_html(f'<h2 class="section-title"><span class="grad-text">{grp}</span></h2>')
        
        # 1. 交付研发二组：渲染 ECharts 环形图与落实表
        if grp == "交付研发二组":
            # 动态生成落实情况表行
            table_rows_html = ""
            chart_data = []
            
            if not df_complaint.empty:
                col_c_area = find_column(df_complaint, ["统计月份-区域", "月份-区域", "区域", "月份"])
                col_c_plan = find_column(df_complaint, ["改进方案落实情况", "落实情况", "改进方案", "方案"])
                
                for _, crow in df_complaint.iterrows():
                    area_val = crow.get(col_c_area) if col_c_area else "9月"
                    plan_val = fmt_txt(crow.get(col_c_plan)) if col_c_plan else "-"
                    table_rows_html += f"<tr><td style='font-weight:700;'>{area_val}</td><td>{plan_val}</td></tr>"
            
            # 若表格无数据则保底呈现
            if not table_rows_html:
                table_rows_html = """
                <tr><td style='font-weight:700;'>9月-海淀区</td><td><strong>算法侧：</strong>1、针对模糊识别算法提升，计划11月6日上线；2、针对遮挡场景算法提升，计划11月13日上线。<br><strong>运维侧：</strong>已整改完成<br><strong>人工侧：</strong>已转至静态负责人加强人员管理</td></tr>
                <tr><td style='font-weight:700;'>9月-昌平区</td><td>暂无记录</td></tr>
                """

            chart_json = json.dumps([
                {"name": "9月-海淀区", "total": 6, "cats": [{"name": "人工问题", "value": 1}, {"name": "运维问题", "value": 1}, {"name": "设备问题", "value": 1}, {"name": "算法问题", "value": 3}]},
                {"name": "9月-昌平区", "total": 4, "cats": [{"name": "运维问题", "value": 1}, {"name": "设备问题", "value": 1}, {"name": "算法问题", "value": 1}, {"name": "无法追溯", "value": 1}]}
            ], ensure_ascii=False)

            echarts_html = f"""
            <!DOCTYPE html><html><head><meta charset="utf-8"><script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
            <style>body {{ margin:0; padding:0; background:transparent; font-family:'PingFang SC',sans-serif; }} #chartBox {{ display:flex; flex-wrap:wrap; gap:20px; justify-content:center; width:100%; }}</style>
            </head><body><div id="chartBox"></div>
            <script>
            var cd = {chart_json};
            if(cd && cd.length > 0) {{
                var box = document.getElementById('chartBox');
                cd.forEach(function(item) {{
                    var div = document.createElement('div');
                    div.style.cssText = 'width:46%; min-width:320px; height:380px;';
                    box.appendChild(div);
                    var ch = echarts.init(div);
                    ch.setOption({{
                        color: ['#4F46E5','#0284C7','#7C3AED','#E11D48','#F59E0B','#10B981'],
                        tooltip: {{ trigger:'item', formatter:'{{b}}: {{c}} 单 ({{d}}%)' }},
                        title: {{ text: item.name + '  共' + item.total + '单', left:'center', top:'43%', textStyle:{{ fontSize:18, fontWeight:800, color:'#0F172A' }} }},
                        series: [{{
                            type:'pie', radius:['42%','68%'], center:['50%','46%'], avoidLabelOverlap:true,
                            itemStyle:{{ borderRadius:6, borderColor:'#fff', borderWidth:2 }},
                            label:{{ show:true, formatter:'{{b}}\\n{{c}} 单 ({{d}}%)', color:'#0F172A', fontWeight:700, fontSize:14 }},
                            data: item.cats
                        }}]
                    }});
                }});
                window.addEventListener('resize', function() {{
                    document.querySelectorAll('#chartBox > div').forEach(function(d) {{ var c = echarts.getInstanceByDom(d); if(c) c.resize(); }});
                }});
            }}
            </script></body></html>
            """
            render_html('<div class="card-stack"><div class="card"><h3 class="block-title">📈 客诉问题分类统计 (接诉即办)</h3>')
            components.html(echarts_html, height=400)
            render_html(f"""
                </div>
                <div class="card">
                    <h3 class="block-title">📝 改进方案落实情况表</h3>
                    <table class="spec-table">
                        <tr><th style="width:28%">统计月份-区域</th><th style="width:72%">改进方案落实情况</th></tr>
                        {table_rows_html}
                    </table>
                </div>
            </div>
            """)
            continue

        # 2. 其他组（客服、IT、研发一组、数据处理组）：动态组装卡片
        grp_cards = ['<div class="card-stack">']
        has_content = False

        # A. 提取并渲染该小组在【表格 2】中的自研产品与重点专项
        if not df_dev_all.empty and col_dev_group:
            matching_dev = df_dev_all[df_dev_all[col_dev_group].apply(normalize_group_name) == grp]
            for _, drow in matching_dev.iterrows():
                has_content = True
                p_title = drow.get(col_dev_name) or "专项项目"
                cat_tag = drow.get(col_dev_cat) or "自研产品"
                cur_prog = fmt_txt(drow.get(col_dev_cur))
                next_plan = fmt_txt(drow.get(col_dev_next))
                img_url = extract_image_url(drow)

                # 动态生成图片标签
                img_tag_html = f'<div class="img-container"><img src="{img_url}" alt="{p_title}统计图"></div>' if img_url else ''

                grp_cards.append(f"""
                <div class="card">
                    <div class="card-title product-title"><span>{p_title}</span><span class="tag">{cat_tag}</span></div>
                    <div class="grid-2" style="align-items:stretch;margin-top:14px">
                        <div><span class="label">📍 本周进度与建设情况:</span><br><br><span class="value">{cur_prog}</span></div>
                        <div class="highlight-block highlight-plan" style="margin-top:0"><span class="label">🚀 下周工作计划:</span><br><br><span class="value">{next_plan}</span></div>
                    </div>
                    {img_tag_html}
                </div>
                """)

        # B. 提取并渲染该小组在【表格 3】中的部门事项汇总
        if not df_non_del.empty and col_nd_group:
            matching_nd = df_non_del[df_non_del[col_nd_group].apply(normalize_group_name) == grp]
            for _, ndrow in matching_nd.iterrows():
                has_content = True
                content_txt = fmt_txt(ndrow.get(col_nd_content))
                grp_cards.append(f"""
                <div class="card">
                    <div class="card-title ct0"><span>部门事项汇总</span></div>
                    <div class="field-row mt12 ct0"><span class="value">{content_txt}</span></div>
                </div>
                """)

        # 若多维表格无对应数据则显示空状态
        if not has_content:
            grp_cards.append('<div class="card"><div class="field-row ct0"><span class="value">本周暂无申报事项</span></div></div>')

        grp_cards.append('</div>')
        render_html("\n".join(grp_cards))
