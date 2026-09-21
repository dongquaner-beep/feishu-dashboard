import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import json

# 1. 页面基本配置
st.set_page_config(page_title="全球技术服务中心周报", layout="wide", page_icon="📊")

# 2. 飞书凭据与完整表格配置
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

# 安全渲染 HTML 的辅助函数（彻底去除行首空格，防止被 Markdown 误识别为代码块）
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

/* 汇报模块分组大标题 */
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
.section-title:first-child {
    margin-top: 6px;
}
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
.product-title {
    font-size: 23px;
    font-weight: 800;
    background: linear-gradient(120deg,#4338CA,#0284C7);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}
.block-title {
    margin: 0 0 18px;
    font-size: 22px;
    font-weight: 800;
    color: #0F172A;
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

/* 运维关注区块（淡蓝） */
.highlight-attention {
    border-color: #BFDBFE;
    border-left: 5px solid #1D4ED8;
    background: #EFF6FF;
}
.highlight-attention .label {
    color: #1D4ED8;
}

/* 下周工作计划区块（清新淡绿） */
.highlight-plan {
    border-color: #BBF7D0;
    border-left: 5px solid #047857;
    background: #F0FDF4;
}
.highlight-plan .label {
    color: #047857;
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

/* 进度说明与落实情况表格 */
.spec-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin-top: 14px;
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid #E2E8F0;
    background: #fff;
    box-shadow: 0 6px 20px rgba(15,23,42,.04);
}
.spec-table th, .spec-table td {
    padding: 12px 18px;
    font-size: 15px;
    line-height: 1.6;
    border-bottom: 1px solid #E2E8F0;
}
.spec-table th {
    font-weight: 800;
    color: #1E1B4B;
    background: #EEF2FF;
}
.ct0 {
    border-bottom: 0 !important;
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
}
.mt12 {
    margin-top: 12px;
}
</style>
""")

# 4. 辅助函数：清洗字段
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

# 5. 飞书数据拉取
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
        
        # 底部进度对照表
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
    with st.spinner("正在拉取【运维中项目】最新汇报数据..."):
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

# ==================== Tab 3：已完结/挂起项目 ====================
with tab3:
    with st.spinner("正在拉取【已完结/挂起项目】最新数据..."):
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

# ==================== Tab 4：其他事项汇总（分组与ECharts图表） ====================
with tab4:
    with st.spinner("正在同步【其他事项汇总】各组数据..."):
        # 拉取专项与自研
        df_prod = fetch_feishu_view(TABLE_DEV_ID, VIEW_DEV_PROD)
        df_spec = fetch_feishu_view(TABLE_DEV_ID, VIEW_DEV_SPEC)
        # 拉取非交付事项
        df_non_del = fetch_feishu_view(TABLE_NON_DEL_ID, VIEW_NON_DEL)
        # 拉取接诉即办
        df_complaint = fetch_feishu_view(TABLE_COMPLAINT_ID, VIEW_COMPLAINT)

    # 1. 客户服务组
    render_html('<h2 class="section-title"><span class="grad-text">客户服务组</span></h2>')
    render_html("""
    <div class="card-stack">
        <div class="card">
            <div class="card-title product-title"><span>认证平台</span><span class="tag">自研产品</span></div>
            <div class="grid-2" style="align-items:stretch;margin-top:14px">
                <div><span class="label">📍 本周进度与建设情况:</span><br><br><span class="value">1、魔盒平台: 脚本编写8/8、视频进度8/8; 培训文档已完成；</span></div>
                <div class="highlight-block highlight-plan" style="margin-top:0"><span class="label">🚀 下周工作计划:</span><br><br><span class="value">1、国际版AIOT：待启动；<br>2、ACG平台：下周启动；</span></div>
            </div>
        </div>
        <div class="card">
            <div class="card-title ct0"><span>部门事项汇总</span></div>
            <div class="field-row mt12 ct0"><span class="value">一、培训工作<br>1、番禺IDS移交培训：单证签字盖章（差资料表）补齐后发出培训邮件; <br>2、培训资料：维护到认证平台后给到江宁项目使用; <br>3、江宁项目：前场答疑2次;<br><br>二、北京停车售后：<br>（1）对接市交委处理各区泊位上下线，共计5次243个泊位。<br>（2）对接静态处理长时间未离场订单，共计3118条。<br>（3）处理易错车辆识别错误原因添加易错车辆库，共计10辆车。<br>（4）对接静态运维处理各区泊位上下线数据表，共计109个泊位。<br>（5）对接静态运维核查历史下线未恢复上线泊位设备上传IDS数据问题，共计25个泊位。<br>（6）核对海康ISC平台配置点位及授权采购历史资料。<br>（7）对接丰台区城管委制作泊位临时下线、删除、恢复上线数据表，共计49个泊位。<br><br>三、北京违停售后<br>1、东城违停项目：交警反馈误抓点位2个，全景看不到违法车辆点位1个，核查违停数据，确认点位详细情况，协调运维调整识别区；核查违法数据填写核查表340/514已完成。<br>2、丰台违停项目：远程指导集指平台以及云瞳点位名称修改的相关操作。<br>3、番禺违停项目：远程指导点位名称修改的相关操作。<br><br>四、其他<br>1、输出GTS停车项目交付流程规范</span></div>
        </div>
    </div>
    """)

    # 2. IT组
    render_html('<h2 class="section-title"><span class="grad-text">IT组</span></h2>')
    render_html("""
    <div class="card-stack">
        <div class="card">
            <div class="card-title product-title"><span>监控中心</span><span class="tag">自研产品</span></div>
            <div class="grid-2" style="align-items:stretch;margin-top:14px">
                <div><span class="label">📍 本周进度与建设情况:</span><br><br><span class="value">监控相关: <br>1、服务探活接口P0整改: AIOT2个项目、蓝脑2个项目; <br>2、IDS应用监控: 0个项目; <br>3、生产工单监控添加；<br>4、监控看板，其它项目微服务jvm、请求等指标看板添加完成；<br>5、工单处理：自动处理489条；人工处理2条；</span></div>
                <div class="highlight-block highlight-plan" style="margin-top:0"><span class="label">🚀 下周工作计划:</span><br><br><span class="value">1、服务探活接口: AIOT、蓝脑等 <br>2、IDS应用监控: 其他项目继续上线添加 <br>3、工单处理;</span></div>
            </div>
        </div>
        <div class="card">
            <div class="card-title product-title"><span>安全筛查专项</span><span class="tag">重点专项</span></div>
            <div class="grid-2" style="align-items:stretch;margin-top:14px">
                <div><span class="label">📍 本周进度与建设情况:</span><br><br><span class="value">前场设备：<br>一、前场设备台账: 路由器统计进展填报到表格；其他设备进度完成5%；<br>二、前场网络架构梳理: 所有项目整体进展100%；<br><br>后端环境：<br>1、上月已完成3个项目安全基线筛查; <br>2、本周亳州项目完成密码修改、安全组调整，该项目进展100%</span></div>
                <div class="highlight-block highlight-plan" style="margin-top:0"><span class="label">🚀 下周工作计划:</span><br><br><span class="value">前场设备：<br>一、前场设备台账推进</span></div>
            </div>
        </div>
        <div class="card">
            <div class="card-title product-title"><span>CPD专项</span><span class="tag">重点专项</span></div>
            <div class="grid-2" style="align-items:stretch;margin-top:14px">
                <div><span class="label">📍 本周进度与建设情况:</span><br><br><span class="value">运维侧：chaosmesh测试用例测试，稳定性、自愈类故障模拟pod生命周期测试等<br>研发侧：cpd-app、cpd-acp小程序测试，ids功能自测，前端爱增收项目验证部署等</span></div>
                <div class="highlight-block highlight-plan" style="margin-top:0"><span class="label">🚀 下周工作计划:</span><br><br><span class="value">运维侧：证书管理、备份管理、存储管理等用例测试<br>研发侧：路外车场测试、acc，算法除ids外功能自测</span></div>
            </div>
        </div>
        <div class="card">
            <div class="card-title ct0"><span>部门事项汇总</span></div>
            <div class="field-row mt12 ct0"><span class="value">项目巡检：郑州、唐山开平每2周人工巡检，郑州每周一、三、五人工复核结果;<br>项目支持：番禺、阳朔、增城、广二等；k8s生产mq问题处理、合肥团队acg流水线改造；<br>关键备份：gitcentersvnjenkinswiki运维平台等；项目部署：昌平部署支持等；<br>数据库：项目维护(腾讯云EOC、南京、花都、番禺等sql优化或问题处理)；例行巡检；<br>通行：张家口日常巡检维护、处理升级后问题、增加redis节点规模；<br>网络安全：番禺、广二漏洞修复，eoc证书更换；机房：北京、张家口机房例行巡检；<br>资源梳理优化：高州、化州、番禺、增城降配；公有云降配预计节省约1400元/月；<br>Cassandra运维：完成单副本认证故障模拟、数据迁移测试、节点故障恢复及一键部署脚本编写。</span></div>
        </div>
    </div>
    """)

    # 3. 交付研发一组
    render_html('<h2 class="section-title"><span class="grad-text">交付研发一组</span></h2>')
    render_html("""
    <div class="card-stack">
        <div class="card">
            <div class="card-title product-title"><span>运维工单平台</span><span class="tag">自研产品</span></div>
            <div class="grid-2" style="align-items:stretch;margin-top:14px">
                <div><span class="label">📍 本周进度与建设情况:</span><br><br><span class="value">工单平台二期: 2.1已上线，商用环境正式启用。<br>工单平台三期: <br>1.完成3.0需求研发评审与排期；<br>2.已启动开发，表结构设计中；<br>3.完成定时邮件发送运维周报功能原型设计。</span></div>
                <div class="highlight-block highlight-plan" style="margin-top:0"><span class="label">🚀 下周工作计划:</span><br><br><span class="value">根据评审需求完善原型；优化C端交互设计，和aiot平台研发对齐业务和技术方案；开展3.0开发，预计进度达到30%。</span></div>
            </div>
        </div>
    </div>
    """)

    # 4. 数据处理组
    render_html('<h2 class="section-title"><span class="grad-text">数据处理组</span></h2>')
    render_html("""
    <div class="card-stack">
        <div class="card">
            <div class="card-title ct0"><span>部门事项汇总</span></div>
            <div class="field-row mt12 ct0"><span class="value">一、日常数据处理类<br>1、交付数据处理：任务67384条、巡检19488条、巡检忽略47525条。<br>2、数据质检：共计质检33213条，错误115条，正确率为99.35%。<br>3、算法准确率验证：共计验证12600条，错误2条，正确率为99.99%。<br>4、昌平三期准确率验证：共计验证4200条，错误1条，正确率为99.98%。<br>5、小松鼠项目：本周标记3099条，正报3084条，误报15条，正确率为99.52%。<br>6、昌平三期新上线车场24小时验证：共计验证608个泊位。<br><br>二、项目移交类<br>1、如皋项目移交：等待官司结束启动移交。<br>2、番禺项目移交：已催客户尽快接手，陪伴期至10月31日。<br>3、海安项目移交：持续保障中，项目经理咨询移交后所需人员情况。<br>4、贵阳项目移交：持续保障中。<br>5、亳州项目移交：甲方未反馈是否找到新运营公司，安排现场沟通。</span></div>
        </div>
    </div>
    """)

    # 5. 交付研发二组（ECharts 环形图与落实表）
    render_html('<h2 class="section-title"><span class="grad-text">交付研发二组</span></h2>')
    
    # ECharts 数据源
    chart_json = json.dumps([
        {
            "name": "9月-海淀区",
            "total": 6,
            "cats": [
                {"name": "人工问题", "value": 1},
                {"name": "运维问题", "value": 1},
                {"name": "设备问题", "value": 1},
                {"name": "算法问题", "value": 3}
            ]
        },
        {
            "name": "9月-昌平区",
            "total": 4,
            "cats": [
                {"name": "运维问题", "value": 1},
                {"name": "设备问题", "value": 1},
                {"name": "算法问题", "value": 1},
                {"name": "无法追溯", "value": 1}
            ]
        }
    ], ensure_ascii=False)

    # 嵌入原生 ECharts 环形图组件
    echarts_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
        <style>
            body {{ margin: 0; padding: 0; background: transparent; font-family: 'PingFang SC', sans-serif; }}
            #chartBox {{ display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; width: 100%; }}
        </style>
    </head>
    <body>
        <div id="chartBox"></div>
        <script>
            var cd = {chart_json};
            if(cd && cd.length > 0) {{
                var box = document.getElementById('chartBox');
                cd.forEach(function(item) {{
                    var div = document.createElement('div');
                    div.style.cssText = 'width: 46%; min-width: 320px; height: 380px;';
                    box.appendChild(div);
                    var ch = echarts.init(div);
                    ch.setOption({{
                        color: ['#4F46E5','#0284C7','#7C3AED','#E11D48','#F59E0B','#10B981'],
                        tooltip: {{
                            trigger: 'item',
                            backgroundColor: 'rgba(255,255,255,.96)',
                            borderColor: '#E2E8F0',
                            borderWidth: 1,
                            textStyle: {{ color: '#0F172A', fontWeight: 700, fontSize: 15 }},
                            formatter: '{{b}}: {{c}} 单 ({{d}}%)'
                        }},
                        title: {{
                            text: item.name + '  共' + item.total + '单',
                            left: 'center',
                            top: '43%',
                            textStyle: {{ fontSize: 18, fontWeight: 800, color: '#0F172A' }}
                        }},
                        series: [{{
                            type: 'pie',
                            radius: ['42%', '68%'],
                            center: ['50%', '46%'],
                            avoidLabelOverlap: true,
                            itemStyle: {{ borderRadius: 6, borderColor: '#fff', borderWidth: 2 }},
                            label: {{
                                show: true,
                                formatter: '{{b}}\\n{{c}} 单 ({{d}}%)',
                                color: '#0F172A',
                                fontWeight: 700,
                                fontSize: 14,
                                lineHeight: 20
                            }},
                            labelLine: {{ length: 10, length2: 8 }},
                            data: item.cats
                        }}]
                    }});
                }});
                window.addEventListener('resize', function() {{
                    var charts = document.querySelectorAll('#chartBox > div');
                    charts.forEach(function(d) {{
                        var c = echarts.getInstanceByDom(d);
                        if(c) c.resize();
                    }});
                }});
            }}
        </script>
    </body>
    </html>
    """

    render_html("""
    <div class="card-stack">
        <div class="card">
            <h3 class="block-title">📈 客诉问题分类统计 (接诉即办)</h3>
    """)
    # 渲染 ECharts 交互组件
    components.html(echarts_html, height=400)
    render_html("""
        </div>
        <div class="card">
            <h3 class="block-title">📝 改进方案落实情况表</h3>
            <table class="spec-table">
                <tr><th style="width:28%">统计月份-区域</th><th style="width:72%">改进方案落实情况</th></tr>
                <tr>
                    <td style="font-weight:700;">9月-海淀区</td>
                    <td>
                        <strong>算法侧：</strong><br>
                        1、针对模糊识别算法提升，计划11月6日上线<br>
                        2、针对遮挡场景算法提升，计划11月13日上线<br>
                        3、事件检测算法提升，计划10月30日上线<br>
                        4、针对离线场景的巡检优化，已经上线<br>
                        5、模糊车牌算法提升，已经上线<br>
                        6、针对相似字符识别效果提升，已经上线<br><br>
                        <strong>设备侧：</strong> -<br>
                        <strong>平台侧：</strong> 暂无<br>
                        <strong>运维侧：</strong> 已整改完成<br>
                        <strong>人工侧：</strong> 已转至静态负责人，并要求其加强人员管理
                    </td>
                </tr>
                <tr>
                    <td style="font-weight:700;">9月-昌平区</td>
                    <td>暂无记录</td>
                </tr>
            </table>
        </div>
    </div>
    """)
