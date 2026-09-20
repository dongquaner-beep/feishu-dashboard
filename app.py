import streamlit as st
import requests
import pandas as pd

# 1. 页面基本设置（宽屏展示、设置标题与图标）
st.set_page_config(page_title="全球技术服务中心周报", layout="wide", page_icon="📊")

# 2. 凭据与多表多视图层级配置
APP_ID = "cli_aa2529e038f81be3"
APP_SECRET = "gKBRXaqMIYKGGqc9RkyH0b11V4Dk4PSY"
APP_TOKEN = "JqHKw49V3izuZKkm9s8ccGwNnmb"

TABLES_CONFIG = [
    {
        "table_name": "项目全生命周期总表",
        "table_id": "tblfMcfAnXH3luI7",
        "views": [
            {"view_name": "交付中项目", "view_id": "vewSu37vul"},
            {"view_name": "运维中项目", "view_id": "vew4u7e0fo"},
            {"view_name": "已完结项目", "view_id": "vewwcbPapg"},
        ]
    },
    {
        "table_name": "GTS自研产品与重点专项",
        "table_id": "tblYtSIkGK07Na1M",
        "views": [
            {"view_name": "自研产品", "view_id": "vewV4IWr91"},
            {"view_name": "重点专项", "view_id": "vew1aFFPXR"},
        ]
    },
    {
        "table_name": "部门非交付事项",
        "table_id": "tbl9DVGuvIB6dOas",
        "views": [
            {"view_name": "非交付事项", "view_id": "vewCXHSZWx"},
        ]
    },
    {
        "table_name": "接诉即办专项分析",
        "table_id": "tblGj9QwAXsYOOrn",
        "views": [
            {"view_name": "接诉即办", "view_id": "vewiedoaqM"},
        ]
    },
]

# 3. 辅助函数：清洗特殊对象
def clean_cell_value(val):
    """清洗飞书特殊字段（关联对象、人员、富文本）为干净字符串"""
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

# 4. 数据拉取函数（带 3 分钟自动缓存）
@st.cache_data(ttl=180)
def fetch_view_data(table_id, view_id):
    """通过飞书 API 拉取指定视图数据并清洗为 DataFrame"""
    # 步骤 A：获取访问 Token
    token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    token_resp = requests.post(
        token_url,
        json={"app_id": APP_ID, "app_secret": APP_SECRET},
        timeout=10
    ).json()
    
    if token_resp.get("code") != 0:
        st.error(f"飞书鉴权失败: {token_resp.get('msg')}")
        return pd.DataFrame()
        
    token = token_resp["tenant_access_token"]
    
    # 步骤 B：分页拉取指定视图记录
    records_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/records"
    headers = {"Authorization": f"Bearer {token}"}
    
    all_records = []
    page_token = ""
    
    while True:
        params = {"page_size": 100, "view_id": view_id}
        if page_token:
            params["page_token"] = page_token
            
        resp = requests.get(records_url, headers=headers, params=params, timeout=15).json()
        if resp.get("code") != 0:
            st.error(f"拉取视图异常: {resp.get('msg')}")
            break
            
        items = resp.get("data", {}).get("items", [])
        all_records.extend(items)
        
        if not resp.get("data", {}).get("has_more", False):
            break
        page_token = resp.get("data", {}).get("page_token")
        
    if not all_records:
        return pd.DataFrame()
        
    # 步骤 C：清洗并转换为 DataFrame
    fields_list = [r.get("fields", {}) for r in all_records]
    df = pd.DataFrame(fields_list)
    df = df.applymap(clean_cell_value)
    return df

# 5. 网页前端布局渲染
st.title("📊 全球技术服务中心周报大屏")

# 顶部操作栏（带一键刷新按钮）
col_left, col_btn = st.columns([5, 1])
with col_btn:
    if st.button("🔄 刷新最新数据", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 第一层：大分类 Tab（4 个多维子表）
table_names = [t["table_name"] for t in TABLES_CONFIG]
table_tabs = st.tabs(table_names)

for idx, t_cfg in enumerate(TABLES_CONFIG):
    with table_tabs[idx]:
        t_id = t_cfg["table_id"]
        views = t_cfg["views"]
        
        # 第二层：子视图选择（单选按钮或小标签）
        view_names = [v["view_name"] for v in views]
        selected_view_name = st.radio(
            "选择视图",
            options=view_names,
            horizontal=True,
            key=f"view_choice_{t_id}",
            label_visibility="collapsed"
        )
        
        # 找到选中的 view_id
        selected_view_id = next(v["view_id"] for v in views if v["view_name"] == selected_view_name)
        
        # 拉取并展示当前视图数据
        with st.spinner(f"正在同步【{selected_view_name}】最新数据..."):
            df = fetch_view_data(t_id, selected_view_id)
            
        if df.empty:
            st.info("当前视图暂无数据。")
        else:
            # 顶部统计指标卡片
            m1, m2, m3 = st.columns(3)
            m1.metric("事项总数", f"{len(df)} 项")
            
            if "完成进度" in df.columns:
                valid_progress = pd.to_numeric(df["完成进度"], errors="coerce").dropna()
                avg_p = round(float(valid_progress.mean()) * 100, 1) if not valid_progress.empty else 0
                m2.metric("平均进度", f"{avg_p}%")
            elif "项目状态" in df.columns:
                m2.metric("状态类型数", f"{df['项目状态'].nunique()} 种")
                
            if "业务大类" in df.columns:
                m3.metric("涉及业务大类", f"{df['业务大类'].nunique()} 个")
            elif "负责人" in df.columns:
                m3.metric("涉及人员", f"{df['负责人'].nunique()} 人")
                
            st.markdown("---")
            
            # 美化表格展示（支持搜索、排序、全屏放大）
            st.dataframe(df, use_container_width=True, hide_index=True)
