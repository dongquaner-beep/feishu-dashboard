import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import json
import base64

# 1. 页面基本配置
st.set_page_config(
    page_title="全球技术服务中心周报",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# 2. 飞书凭据配置（安全读取 Streamlit Secrets 保险箱）
APP_ID = st.secrets.get("APP_ID", "cli_aa2529e038f81be3")
APP_SECRET = st.secrets.get("APP_SECRET", "gKBRXaqMIYKGGqc9RkyH0b11V4Dk4PSY")
APP_TOKEN = st.secrets.get("APP_TOKEN", "JqHKw49V3izuZKkm9s8ccGwNnmb")

TABLE_LIFE_ID = "tblfMcfAnXH3luI7"
VIEW_DELIVERY = "vewSu37vul"    # 交付中项目
VIEW_MAINT = "vew4u7e0fo"       # 运维中项目
VIEW_FINISH = "vewwcbPapg"      # 已完结/挂起项目

TABLE_DEV_ID = "tblYtSIkGK07Na1M"
VIEW_DEV_PROD = "vewV4IWr91"    # 自研产品
VIEW_DEV_SPEC = "vew1aFFPXR"    # 重点专项

TABLE_NON_DEL_ID = "tbl9DVGuvIB6dOas"
VIEW_NON_DEL = "vewCXHSZWx"

TABLE_COMPLAINT_ID = "tblGj9QwAXsYOOrn"
VIEW_COMPLAINT = "vewiedoaqM"

# 导航菜单配置
NAV_TABS = [
    {"id": "delivery", "label": "📦 交付中项目", "icon": "📦"},
    {"id": "maint", "label": "🔧 运维中项目", "icon": "🔧"},
    {"id": "finish", "label": "🏁 已完结/挂起项目", "icon": "🏁"},
    {"id": "other", "label": "📑 其他事项汇总", "icon": "📑"},
]

# 状态初始化
if "sidebar_collapsed" not in st.session_state:
    st.session_state.sidebar_collapsed = False
if "active_tab_idx" not in st.session_state:
    st.session_state.active_tab_idx = 0

# 安全渲染 HTML
def render_html(html_str):
    cleaned = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)

# 动态计算侧边栏宽度：展开 240px，收起为 68px Mini-Rail
sb_width = 68 if st.session_state.sidebar_collapsed else 240

# GTS 专属科技矢量徽标
GTS_LOGO_SVG = """
<span class="gts-logo-badge">
    <svg width="34" height="34" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="34" height="34" rx="9" fill="url(#gts_gradient)"/>
        <circle cx="17" cy="17" r="9" stroke="#FFFFFF" stroke-width="1.6" stroke-opacity="0.95"/>
        <ellipse cx="17" cy="17" rx="3.8" ry="9" stroke="#FFFFFF" stroke-width="1.2" stroke-opacity="0.8"/>
        <line x1="8" y1="17" x2="26" y2="17" stroke="#FFFFFF" stroke-width="1.2" stroke-opacity="0.8"/>
        <path d="M10 12.8C12 14.2 14.5 14.8 17 14.8C19.5 14.8 22 14.2 24 12.8" stroke="#FFFFFF" stroke-width="1.1" stroke-opacity="0.6"/>
        <path d="M10 21.2C12 19.8 14.5 19.2 17 19.2C19.5 19.2 22 19.8 24 21.2" stroke="#FFFFFF" stroke-width="1.1" stroke-opacity="0.6"/>
        <path d="M7 26C11 28.5 23 28.5 27 21" stroke="#38BDF8" stroke-width="1.4" stroke-dasharray="2 2" stroke-linecap="round"/>
        <circle cx="26.5" cy="12.5" r="2.2" fill="#38BDF8"/>
        <circle cx="7.5" cy="21.5" r="1.5" fill="#A5B4FC"/>
        <defs>
            <linearGradient id="gts_gradient" x1="0" y1="0" x2="34" y2="34" gradientUnits="userSpaceOnUse">
                <stop stop-color="#4F46E5"/>
                <stop offset="0.5" stop-color="#2563EB"/>
                <stop offset="1" stop-color="#0284C7"/>
            </linearGradient>
        </defs>
    </svg>
</span>
"""

# 3. 注入全局样式
render_html(f"""
<style>
/* 全局微光渐变背景 */
.stApp {{
    background: radial-gradient(60% 52% at 12% 8%,rgba(99,102,241,.14),transparent 70%),
                radial-gradient(55% 46% at 90% 6%,rgba(56,189,248,.13),transparent 70%),
                radial-gradient(58% 50% at 92% 92%,rgba(168,85,247,.13),transparent 70%),
                radial-gradient(55% 46% at 6% 94%,rgba(59,130,246,.13),transparent 70%),
                linear-gradient(135deg,#EEF2FF,#F5F8FF 46%,#FAF5FF) !important;
    font-family: 'PingFang SC','SF Pro Display',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    color: #334155;
}}

/* 顶栏背景透明，隐藏系统杂项 */
header[data-testid="stHeader"] {{
    background: transparent !important;
    pointer-events: none !important;
}}
[data-testid="stToolbar"], [data-testid="stDecoration"] {{
    display: none !important;
}}
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {{
    display: none !important;
}}

/* 隐藏应用内多余元素 */
[data-testid="manage-app-button"],
footer {{
    display: none !important;
    visibility: hidden !important;
}}

/* ================= 侧边栏结构：锁定 {sb_width}px ================= */
section[data-testid="stSidebar"] {{
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    bottom: 0 !important;
    width: {sb_width}px !important;
    min-width: {sb_width}px !important;
    max-width: {sb_width}px !important;
    transform: none !important;
    margin-left: 0 !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 9999 !important;
    background: rgba(255, 255, 255, 0.92) !important;
    border-right: 1px solid rgba(226, 232, 240, 0.9) !important;
    backdrop-filter: blur(22px) saturate(180%) !important;
    box-shadow: 4px 0 24px rgba(15, 23, 42, 0.05) !important;
    overflow-x: hidden !important;
}}

/* 主内容区域跟随侧边栏平滑避让 */
[data-testid="stMain"], .main {{
    margin-left: {sb_width}px !important;
    width: calc(100% - {sb_width}px) !important;
    max-width: calc(100% - {sb_width}px) !important;
}}

/* 侧边栏内边距 */
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
    padding: {"14px 8px" if st.session_state.sidebar_collapsed else "20px 14px"} !important;
}}

/* 侧边栏标题 */
.sidebar-title {{
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.5px;
    background: linear-gradient(120deg,#4338CA,#0284C7 50%,#7C3AED);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    display: block;
    white-space: nowrap;
    line-height: 32px;
}}

/* 收起/展开按钮绝对对齐 */
div[class*="st-key-toggle_sidebar_btn"] {{
    display: flex !important;
    align-items: center !important;
    justify-content: {"center" if st.session_state.sidebar_collapsed else "flex-end"} !important;
    width: 100% !important;
}}
div[class*="st-key-toggle_sidebar_btn"] button {{
    width: 32px !important;
    height: 32px !important;
    min-width: 32px !important;
    max-width: 32px !important;
    min-height: 32px !important;
    max-height: 32px !important;
    padding: 0 !important;
    margin: 0 !important;
    border-radius: 8px !important;
    background: #F1F5F9 !important;
    border: 1px solid #CBD5E1 !important;
    color: #475569 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05) !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}}
div[class*="st-key-toggle_sidebar_btn"] button:hover {{
    background: #EEF2FF !important;
    border-color: #818CF8 !important;
    color: #4F46E5 !important;
    transform: scale(1.05) !important;
}}
div[class*="st-key-toggle_sidebar_btn"] button div[data-testid="stMarkdownContainer"] {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    height: 100% !important;
    line-height: 1 !important;
}}
div[class*="st-key-toggle_sidebar_btn"] button p {{
    font-size: 14px !important;
    font-weight: 700 !important;
    line-height: 1 !important;
    margin: 0 !important;
    padding: 0 !important;
    text-align: center !important;
}}

/* 展开状态导航胶囊 */
div[class*="st-key-nav_exp_"] button {{
    border-radius: 12px !important;
    padding: 10px 14px !important;
    height: 42px !important;
    min-height: 42px !important;
    font-size: 14.5px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    margin-bottom: 6px !important;
    transition: all 0.2s ease !important;
    border: 1px solid transparent !important;
}}
div[class*="st-key-nav_exp_"] button[kind="secondary"] {{
    background: transparent !important;
    color: #475569 !important;
}}
div[class*="st-key-nav_exp_"] button[kind="secondary"]:hover {{
    background: #F1F5F9 !important;
    color: #1E1B4B !important;
}}
div[class*="st-key-nav_exp_"] button[kind="secondary"] p {{
    color: #475569 !important;
    font-weight: 500 !important;
    font-size: 14.5px !important;
}}
div[class*="st-key-nav_exp_"] button[kind="primary"] {{
    background: linear-gradient(135deg, #4F46E5, #2563EB) !important;
    box-shadow: 0 6px 16px rgba(67, 56, 202, 0.28) !important;
    border-color: transparent !important;
}}
div[class*="st-key-nav_exp_"] button[kind="primary"] p {{
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 14.5px !important;
}}

/* 收起状态纯单图标方块（100% 居中，零截断） */
div[class*="st-key-nav_col_"] button {{
    border-radius: 12px !important;
    padding: 0 !important;
    width: 46px !important;
    height: 46px !important;
    min-width: 46px !important;
    max-width: 46px !important;
    min-height: 46px !important;
    max-height: 46px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 auto 10px auto !important;
    transition: all 0.2s ease !important;
    border: 1px solid transparent !important;
}}
div[class*="st-key-nav_col_"] button[kind="secondary"] {{
    background: transparent !important;
}}
div[class*="st-key-nav_col_"] button[kind="secondary"]:hover {{
    background: #EEF2FF !important;
    border-color: #C7D2FE !important;
    transform: translateY(-1px) !important;
}}
div[class*="st-key-nav_col_"] button[kind="secondary"] p {{
    font-size: 20px !important;
    margin: 0 !important;
    line-height: 1 !important;
}}
div[class*="st-key-nav_col_"] button[kind="primary"] {{
    background: linear-gradient(135deg, #4F46E5, #2563EB) !important;
    box-shadow: 0 6px 18px rgba(79, 70, 229, 0.35) !important;
    transform: scale(1.05) !important;
}}
div[class*="st-key-nav_col_"] button[kind="primary"] p {{
    font-size: 20px !important;
    margin: 0 !important;
    line-height: 1 !important;
    color: #ffffff !important;
}}

/* 页面顶部 GTS 标题 */
.block-container {{
    padding-top: 2rem !important;
}}
.report-header {{
    font-size: 26px;
    font-weight: 700;
    margin-bottom: 6px;
    display: inline-flex;
    align-items: center;
}}
.report-header-text {{
    background: linear-gradient(120deg,#4338CA,#0284C7 50%,#7C3AED);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    display: inline-block;
}}
.gts-logo-badge {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    vertical-align: middle;
    margin-right: 12px;
    filter: drop-shadow(0 4px 10px rgba(79, 70, 229, 0.28));
}}
.tab-summary-badge {{
    font-size: 14px;
    font-weight: 400;
    color: #64748B;
    margin-bottom: 20px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}}
.tab-summary-badge strong {{
    font-weight: 600;
    color: #1E293B;
}}

/* 右下角专属悬浮刷新胶囊（FAB） */
div.st-key-floating_refresh_btn button {{
    position: fixed !important;
    bottom: 56px !important;
    right: 28px !important;
    z-index: 999999 !important;
    border-radius: 999px !important;
    padding: 8px 18px !important;
    height: 38px !important;
    min-height: 38px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    background: linear-gradient(135deg, #4F46E5, #2563EB) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.6) !important;
    box-shadow: 0 4px 16px rgba(79, 70, 229, 0.35) !important;
    backdrop-filter: blur(10px) !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    width: auto !important;
}}
div.st-key-floating_refresh_btn button:hover {{
    transform: translateY(-2px) scale(1.03) !important;
    box-shadow: 0 8px 22px rgba(79, 70, 229, 0.48) !important;
    background: linear-gradient(135deg, #4338CA, #1D4ED8) !important;
}}
div.st-key-floating_refresh_btn button p {{
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    margin: 0 !important;
    line-height: 1 !important;
}}

/* 🎯 重点汇报行：温和蓝紫聚焦 */
.target-highlight {{
    color: #3730A3 !important;
    font-weight: 500 !important;
    background: #EEF2FF !important;
    border: 1px solid #C7D2FE !important;
    border-left: 4px solid #6366F1 !important;
    padding: 3px 10px !important;
    margin: 4px 0 !important;
    border-radius: 6px !important;
    display: inline-block !important;
    line-height: 1.65 !important;
}}
.risk-text .target-highlight {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}}

/* 卡片排版 */
.section-title {{
    font-size: 22px;
    font-weight: 700;
    padding-bottom: 8px;
    margin: 30px 0 16px;
    position: relative;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.section-title:first-child {{ margin-top: 4px; }}
.section-title::after {{
    content: '';
    position: absolute;
    left: 0;
    bottom: 0;
    width: 64px;
    height: 3px;
    border-radius: 3px;
    background: linear-gradient(90deg,#4F46E5,#0284C7);
}}
.grad-text {{
    background: linear-gradient(120deg,#4338CA,#0284C7 50%,#7C3AED);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}}
.card-stack {{ display: flex; flex-direction: column; gap: 20px; }}
.card {{
    position: relative;
    padding: 22px 26px;
    border-radius: 18px;
    background: rgba(255,255,255,.9);
    border: 1px solid rgba(255,255,255,.95);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    box-shadow: 0 8px 26px rgba(15, 23, 42, .05);
    transition: transform .2s ease, box-shadow .2s ease;
}}
.card:hover {{ transform: translateY(-2px); box-shadow: 0 14px 34px rgba(15, 23, 42, .08); }}

.card-title {{
    font-size: 20px;
    font-weight: 700;
    color: #0F172A;
    margin: 0 0 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid #E2E8F0;
}}
.product-title {{
    font-size: 21px;
    font-weight: 700;
    background: linear-gradient(120deg,#4338CA,#0284C7);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}}
.block-title {{ margin: 0 0 16px; font-size: 20px; font-weight: 700; color: #0F172A; }}

.tag {{
    display: inline-block;
    padding: 2px 10px;
    font-size: 13px;
    font-weight: 500;
    border-radius: 99px;
    color: #3730A3;
    background: #EEF2FF;
    border: 1px solid #C7D2FE;
}}
.tag-success {{ color: #065F46; background: #ECFDF5; border-color: #A7F3D0; }}
.tag-muted {{ color: #475569; background: #F1F5F9; border-color: #CBD5E1; }}

.progress-wrapper {{ margin: 14px 0 10px; }}
.progress-header {{ display: flex; justify-content: space-between; font-size: 14px; font-weight: 500; color: #64748B; margin-bottom: 6px; }}
.progress-header span:last-child {{ font-weight: 600; color: #1E293B; }}
.progress-bg {{ width: 100%; height: 10px; border-radius: 99px; background: #E2E8F0; box-shadow: inset 0 2px 4px rgba(15, 23, 42, .08); overflow: hidden; }}
.progress-fill {{
    height: 100%;
    border-radius: 99px;
    position: relative;
    overflow: hidden;
    background: linear-gradient(90deg,#4F46E5,#2563EB,#0284C7,#7C3AED,#4F46E5);
    background-size: 300% 100%;
    animation: flow 4s linear infinite;
}}
@keyframes flow {{ to {{ background-position: 300% 0; }} }}

.grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: stretch; }}
@media (max-width: 900px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}

.field-row {{
    margin-bottom: 12px;
    font-size: 14.5px;
    line-height: 1.7;
    color: #334155;
    font-weight: 400;
}}
.label {{
    color: #4338CA;
    font-weight: 600;
    display: inline-block;
    margin-right: 6px;
    font-size: 14.5px;
}}
.value {{
    color: #334155;
    font-weight: 400;
    font-size: 14.5px;
}}

.highlight-block {{ padding: 14px 16px; border-radius: 14px; background: rgba(248,250,252,.92); border: 1px solid #E2E8F0; border-left: 4px solid #6366F1; }}
.highlight-attention {{ border-color: #BFDBFE; border-left: 4px solid #2563EB; background: #F8FAFC; }}
.highlight-attention .label {{ color: #1D4ED8; }}
.highlight-plan {{ border-color: #BBF7D0; border-left: 4px solid #059669; background: #F8FCF9; }}
.highlight-plan .label {{ color: #047857; }}

.risk-text {{
    display: block;
    margin-top: 6px;
    padding: 8px 12px;
    border-radius: 8px;
    color: #991B1B;
    font-weight: 500;
    font-size: 14.5px;
    line-height: 1.6;
    background: #FEE2E2;
    border: 1px solid #FCA5A5;
}}

.img-container img {{
    width: 100%;
    max-height: 460px;
    object-fit: contain;
    border-radius: 14px;
    margin-top: 14px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 6px 20px rgba(15, 23, 42, .06);
    background: #fff;
}}
.spec-table {{ width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 14px; border-radius: 12px; overflow: hidden; border: 1px solid #E2E8F0; background: #fff; box-shadow: 0 4px 16px rgba(15, 23, 42, .03); }}
.spec-table th, .spec-table td {{ padding: 11px 16px; font-size: 14px; line-height: 1.6; border-bottom: 1px solid #E2E8F0; font-weight: 400; color: #334155; }}
.spec-table th {{ font-weight: 600; color: #1E1B4B; background: #EEF2FF; }}
.ct0 {{ border-bottom: 0 !important; margin-bottom: 0 !important; padding-bottom: 0 !important; }}
.mt12 {{ margin-top: 10px; }}
</style>
""")

# 4. 原生零报错防 nan 函数
def is_null_or_nan(val):
    if val is None:
        return True
    if isinstance(val, (list, dict, tuple, set)):
        return False
    if isinstance(val, float) and val != val:
        return True
    s = str(val).strip().lower()
    if s in ["nan", "none", "null", "<na>", "undefined", ""]:
        return True
    return False

def safe_val(val, default="-"):
    if is_null_or_nan(val):
        return default
    return str(val).strip()

def fmt_txt(val, default="-"):
    s = safe_val(val, default)
    if s == default:
        return default
    lines = [line.strip() for line in s.replace("\r\n", "\n").split("\n")]
    formatted = []
    for line in lines:
        if not line:
            continue
        if line == "🎯":
            formatted.append('<span class="target-highlight">🎯 (重点汇报)</span>')
        elif "🎯" in line:
            formatted.append(f'<span class="target-highlight">{line}</span>')
        else:
            formatted.append(line)
    if not formatted:
        return default
    return "<br>".join(formatted)

def clean_cell_value(val):
    if is_null_or_nan(val):
        return ""
    if isinstance(val, list):
        texts = []
        for item in val:
            if isinstance(item, dict):
                t = item.get("link") or item.get("url") or item.get("text") or item.get("name") or ""
                if not t and "text_arr" in item and isinstance(item["text_arr"], list):
                    t = " / ".join([str(x) for x in item["text_arr"] if x])
                if t:
                    texts.append(str(t))
            elif isinstance(item, (str, int, float)):
                if not is_null_or_nan(item):
                    texts.append(str(item))
        return " / ".join(texts) if texts else ""
    if isinstance(val, dict):
        return str(val.get("link") or val.get("url") or val.get("text") or val.get("name") or "")
    return str(val).strip()

def fmt_progress(val):
    s = safe_val(val, "")
    if not s:
        return 0.0, "0%"
    try:
        num = float(s.replace("%", "").strip())
        pct = round(num * 100, 1) if num <= 1.0 else round(num, 1)
        pct_int = int(pct) if pct.is_integer() else pct
        return min(max(pct, 0.0), 100.0), f"{pct_int}%"
    except Exception:
        return 0.0, "0%"

def normalize_group_name(val):
    s = safe_val(val, "")
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
    for cand in candidates:
        if cand in df.columns:
            return cand
    for col in df.columns:
        for cand in candidates:
            if cand in str(col):
                return col
    return None

@st.cache_data(ttl=3600)
def to_base64_image(img_url):
    if not img_url or not str(img_url).startswith("http"):
        return img_url
    try:
        res = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if res.status_code == 200 and len(res.content) > 200:
            b64 = base64.b64encode(res.content).decode("utf-8")
            ctype = res.headers.get("Content-Type", "image/png")
            return f"data:{ctype};base64,{b64}"
    except Exception:
        pass
    return img_url

def extract_image_url(row, p_title=""):
    default_workorder_img = "https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/preview/Qt6pbnTeNo3Y9DxuERlcPPAZnIh?extra=%7B%22bitablePerm%22%3A%7B%22tableId%22%3A%22tblYtSIkGK07Na1M%22%2C%22rev%22%3A146%2C%22attachments%22%3A%7B%22fldt82h6VW%22%3A%7B%22recvuTXB4GVwCg%22%3A%5B%22Qt6pbnTeNo3Y9DxuERlcPPAZnIh%22%5D%7D%7D%7D%7D&mount_point=bitable&preview_type=16&version=7685209289593572280"
    for col in ["统计图", "统计图-图片", "图片", "图表"]:
        if col in row and row[col]:
            val = str(row[col]).strip()
            if val.startswith("http://") or val.startswith("https://"):
                return to_base64_image(val)
    if "工单" in p_title:
        return to_base64_image(default_workorder_img)
    return None

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
        
    cleaned_rows = []
    for r in all_records:
        raw_f = r.get("fields", {})
        row = {}
        for k, v in raw_f.items():
            row[k] = clean_cell_value(v)
        cleaned_rows.append(row)
    return pd.DataFrame(cleaned_rows)

# ----------------- 5. 全局预加载（静音自带的 Running 提示） -----------------
@st.cache_data(ttl=300, show_spinner=False)
def load_all_dashboard_data():
    df_del = fetch_feishu_view(TABLE_LIFE_ID, VIEW_DELIVERY)
    df_maint = fetch_feishu_view(TABLE_LIFE_ID, VIEW_MAINT)
    df_fin = fetch_feishu_view(TABLE_LIFE_ID, VIEW_FINISH)
    
    df_p = fetch_feishu_view(TABLE_DEV_ID, VIEW_DEV_PROD)
    df_s = fetch_feishu_view(TABLE_DEV_ID, VIEW_DEV_SPEC)
    df_dev_all = pd.concat([df_p, df_s], ignore_index=True) if (not df_p.empty or not df_s.empty) else pd.DataFrame()
    
    df_non_del = fetch_feishu_view(TABLE_NON_DEL_ID, VIEW_NON_DEL)
    df_complaint = fetch_feishu_view(TABLE_COMPLAINT_ID, VIEW_COMPLAINT)
    
    return {
        "delivery": df_del,
        "maint": df_maint,
        "finish": df_fin,
        "dev_all": df_dev_all,
        "non_del": df_non_del,
        "complaint": df_complaint
    }

# ================= 核心：数据常驻 session_state，普通交互 0 秒切无转圈 =================
if "data_hub" not in st.session_state:
    with st.spinner("正在同步飞书全量数据..."):
        st.session_state.data_hub = load_all_dashboard_data()

DATA_HUB = st.session_state.data_hub

# 解析表格 3（部门非交付事项）
def parse_non_delivery_data(df):
    if df.empty:
        return {}
    col_grp = find_column(df, ["负责小组", "小组", "部门", "负责部门", "团队", "组别"])
    col_cnt = find_column(df, ["进度及关注事项", "本周进度及关注事项", "关注事项", "事项内容", "工作内容", "部门事项汇总", "非交付事项"])
    res = {}
    for _, r in df.iterrows():
        g_raw = r.get(col_grp) if col_grp else ""
        g = normalize_group_name(g_raw)
        c_raw = r.get(col_cnt) if col_cnt else ""
        if not c_raw and "进度及关注事项" in r:
            c_raw = r.get("进度及关注事项")
        c_clean = fmt_txt(c_raw)
        if g and c_clean != "-":
            if g in res:
                res[g] += "<br><br>" + c_clean
            else:
                res[g] = c_clean
    return res

# 解析表格 4（接诉即办专项分析）
def parse_complaint_data(df):
    if df.empty:
        return [], []
    col_month = find_column(df, ["统计月份", "月份", "统计月份-区域"])
    col_area = find_column(df, ["区域", "地区"])
    col_total = find_column(df, ["客诉总单数", "总单数", "总数"])
    col_plan = find_column(df, ["改进方案落实情况", "落实情况", "改进方案", "方案", "整改方案"])
    
    cat_cols = []
    for col in df.columns:
        if col in [col_month, col_area, col_total, col_plan]:
            continue
        if "问题" in col or "归类" in col:
            cat_cols.append(col)
            
    chart_list = []
    plans = []
    for _, r in df.iterrows():
        name = safe_val(r.get(col_month) or r.get(col_area), "客诉分析")
        area_name = safe_val(r.get(col_area) or r.get(col_month), "")
        try:
            total = int(float(str(r.get(col_total, 0) or 0).strip()))
        except Exception:
            total = 0
            
        cats = []
        for c in cat_cols:
            clean_cname = c.replace("归类-", "").replace("归类", "").strip()
            try:
                v = int(float(str(r.get(c, 0) or 0).strip()))
            except Exception:
                v = 0
            if v > 0:
                cats.append({"name": clean_cname, "value": v})
                
        if total == 0 and cats:
            total = sum(x["value"] for x in cats)
            
        if cats or total > 0:
            chart_list.append({"name": name, "total": total, "cats": cats})
            
        if col_plan:
            p_txt = str(r.get(col_plan, "")).strip()
            display_area = name if name else area_name
            plans.append({"area": display_area, "plan": fmt_txt(p_txt) if p_txt else "暂无记录"})
            
    return chart_list, plans

# ----------------- 6. 侧边栏：状态化 240px 展开 / 68px 纯图标坞 -----------------
with st.sidebar:
    if not st.session_state.sidebar_collapsed:
        # A. 展开模式：标题 + 精致对齐的收起按钮 «
        c_title, c_toggle = st.columns([3.8, 1.2])
        with c_title:
            render_html('<span class="sidebar-title">GTS 周会汇报</span>')
        with c_toggle:
            if st.button("«", key="toggle_sidebar_btn", help="收起导航为图标模式"):
                st.session_state.sidebar_collapsed = True
                st.rerun()
        
        render_html("<div style='height:12px;'></div>")
        for i, tab in enumerate(NAV_TABS):
            is_active = (st.session_state.active_tab_idx == i)
            if st.button(tab["label"], key=f"nav_exp_{i}", type="primary" if is_active else "secondary", use_container_width=True):
                st.session_state.active_tab_idx = i
                st.rerun()
    else:
        # B. 收起模式：居中对齐展开按钮 » + 纯单图标（100% 居中，零截断）
        if st.button("»", key="toggle_sidebar_btn", help="展开完整导航"):
            st.session_state.sidebar_collapsed = False
            st.rerun()
            
        render_html("<div style='height:16px;'></div>")
        for i, tab in enumerate(NAV_TABS):
            is_active = (st.session_state.active_tab_idx == i)
            if st.button(tab["icon"], key=f"nav_col_{i}", type="primary" if is_active else "secondary", use_container_width=True):
                st.session_state.active_tab_idx = i
                st.rerun()

# 当前激活板块 ID
current_tab_id = NAV_TABS[st.session_state.active_tab_idx]["id"]

# ----------------- 7. 页面顶部纯净大标题（内嵌 GTS 科技矢量徽标） -----------------
render_html(f'''
<div class="report-header">
    {GTS_LOGO_SVG}
    <span class="report-header-text">GTS 部门周会汇报大屏</span>
</div>
''')

# ----------------- 8. 右下角专属悬浮刷新胶囊（点击时才触发真正同步） -----------------
if st.button("🔄 刷新数据", key="floating_refresh_btn"):
    st.cache_data.clear()
    if "data_hub" in st.session_state:
        del st.session_state["data_hub"]
    st.rerun()

# ==================== Tab 1：交付中项目 ====================
if current_tab_id == "delivery":
    df_del = DATA_HUB["delivery"]
    if df_del.empty:
        st.info("暂未获取到交付中项目数据。")
    else:
        render_html(f'<div class="tab-summary-badge">共计 <strong>{len(df_del)}</strong> 个交付中项目</div>')
        
        col_c_desc = find_column(df_del, ["交付内容", "交付范围", "建设内容", "内容"])
        col_c_done = find_column(df_del, ["已完成事项", "已完成工作", "已完成", "完成事项"])
        
        cards_html = ['<div class="card-stack">']
        for _, row in df_del.iterrows():
            p_name = safe_val(row.get("项目名称"), "未命名项目")
            bu = safe_val(row.get("BU"), "-")
            status = safe_val(row.get("项目状态"), "交付中")
            p_width, p_label = fmt_progress(row.get("完成进度"))
            c_sign = fmt_txt(row.get("合同签订时间"))
            c_acc = fmt_txt(row.get("计划验收时间"))
            
            raw_desc = row.get(col_c_desc) if col_c_desc else row.get("交付内容")
            raw_done = row.get(col_c_done) if col_c_done else row.get("已完成事项")
            
            c_desc = fmt_txt(raw_desc)
            c_done = fmt_txt(raw_done)
            
            s_prog = fmt_txt(row.get("项目进度-软件侧"))
            h_prog = fmt_txt(row.get("项目进度-硬件侧"))
            d_supp = fmt_txt(row.get("项目进度-交付支持") or row.get("交付支持"))
            risk = safe_val(row.get("风险点和协调项"), "-")
            risk_html = f'<span class="risk-text">{fmt_txt(risk)}</span>' if risk != "-" else '<span class="value">-</span>'
            
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
elif current_tab_id == "maint":
    df_maint = DATA_HUB["maint"]
    if df_maint.empty:
        st.info("暂无运维中项目。")
    else:
        render_html(f'<div class="tab-summary-badge">共计 <strong>{len(df_maint)}</strong> 个在保运维项目</div>')
        
        maint_cards = ['<div class="card-stack">']
        for _, row in df_maint.iterrows():
            p_name = safe_val(row.get("项目名称"), "未命名项目")
            bu = safe_val(row.get("BU"), "-")
            s_date = safe_val(row.get("运维开始时间"), "-")
            e_date = safe_val(row.get("运维结束时间"), "-")
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
elif current_tab_id == "finish":
    df_fin = DATA_HUB["finish"]
    if df_fin.empty:
        st.info("暂无已完结或挂起项目。")
    else:
        render_html(f'<div class="tab-summary-badge">共计 <strong>{len(df_fin)}</strong> 个已完结或挂起项目</div>')
        
        fin_cards = ['<div class="card-stack">']
        for _, row in df_fin.iterrows():
            p_name = safe_val(row.get("项目名称"), "未命名项目")
            bu = safe_val(row.get("BU"), "爱泊车")
            status = safe_val(row.get("项目状态(完结)") or row.get("项目状态"), "项目结束")
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

# ==================== Tab 4：其他事项汇总 ====================
elif current_tab_id == "other":
    df_dev_all = DATA_HUB["dev_all"]
    df_non_del = DATA_HUB["non_del"]
    df_complaint = DATA_HUB["complaint"]

    non_del_summary_map = parse_non_delivery_data(df_non_del)

    col_dev_name = find_column(df_dev_all, ["产品/专项名称", "产品名称", "专项名称", "名称"])
    col_dev_cat = find_column(df_dev_all, ["分类", "类别"])
    col_dev_cur = find_column(df_dev_all, ["本周进度与建设情况", "本周进度", "建设情况"])
    col_dev_next = find_column(df_dev_all, ["下周工作计划", "下周计划", "工作计划"])
    col_dev_group = find_column(df_dev_all, ["负责小组", "小组", "部门", "组别", "团队"])

    groups_order = ["客户服务组", "IT组", "交付研发一组", "数据处理组", "交付研发二组"]

    for grp in groups_order:
        render_html(f'<h2 class="section-title"><span class="grad-text">{grp}</span></h2>')
        
        if grp == "交付研发二组":
            chart_list, plan_list = parse_complaint_data(df_complaint)
            if not chart_list:
                chart_list = [
                    {"name": "9月-海淀区", "total": 10, "cats": [{"name": "运维问题", "value": 1}, {"name": "设备问题", "value": 1}, {"name": "算法问题", "value": 8}]},
                    {"name": "9月-昌平区", "total": 10, "cats": [{"name": "运维问题", "value": 1}, {"name": "设备问题", "value": 1}, {"name": "算法问题", "value": 8}]}
                ]
            if not plan_list:
                plan_list = [
                    {"area": "9月-海淀区", "plan": "算法侧：1、针对模糊识别算法提升，计划11月6日上线；2、针对遮挡场景算法提升，计划11月13日上线。<br>运维侧：已整改完成<br>人工侧：已转至静态负责人加强人员管理"},
                    {"area": "9月-昌平区", "plan": "暂无记录"}
                ]

            chart_json = json.dumps(chart_list, ensure_ascii=False)
            table_rows_html = "".join([f"<tr><td style='font-weight:600;'>{safe_val(x['area'])}</td><td>{x['plan']}</td></tr>" for x in plan_list])

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
                        color: ['#4F46E5','#0284C7','#7C3AED','#E11D48','#F59E0B','#10B981','#64748B'],
                        tooltip: {{ trigger:'item', formatter:'{{b}}: {{c}} 单 ({{d}}%)' }},
                        title: {{ text: item.name + '  共' + item.total + '单', left:'center', top:'43%', textStyle:{{ fontSize:17, fontWeight:600, color:'#0F172A' }} }},
                        series: [{{
                            type:'pie', radius:['42%','68%'], center:['50%','46%'], avoidLabelOverlap:true,
                            itemStyle:{{ borderRadius:6, borderColor:'#fff', borderWidth:2 }},
                            label:{{ show:true, formatter:'{{b}}\\n{{c}} 单 ({{d}}%)', color:'#0F172A', fontWeight:500, fontSize:13.5 }},
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

        grp_cards = ['<div class="card-stack">']
        has_content = False

        if not df_dev_all.empty and col_dev_group:
            matching_dev = df_dev_all[df_dev_all[col_dev_group].apply(normalize_group_name) == grp]
            for _, drow in matching_dev.iterrows():
                has_content = True
                p_title = safe_val(drow.get(col_dev_name), "专项产品")
                cat_tag = safe_val(drow.get(col_dev_cat), "自研产品")
                cur_prog = fmt_txt(drow.get(col_dev_cur))
                next_plan = fmt_txt(drow.get(col_dev_next))
                img_url = extract_image_url(drow, p_title)

                img_tag_html = f'<div class="img-container"><img src="{img_url}" referrerpolicy="no-referrer" alt="{p_title}统计图"></div>' if img_url else ''

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

        if grp in non_del_summary_map:
            has_content = True
            content_txt = non_del_summary_map[grp]
            grp_cards.append(f"""
            <div class="card">
                <div class="card-title ct0"><span>部门事项汇总</span></div>
                <div class="field-row mt12 ct0"><span class="value">{content_txt}</span></div>
            </div>
            """)

        if not has_content:
            grp_cards.append('<div class="card"><div class="field-row ct0"><span class="value">本周暂无申报事项</span></div></div>')

        grp_cards.append('</div>')
        render_html("\n".join(grp_cards))
