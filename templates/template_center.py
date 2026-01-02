import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import analysis_utils
import numpy as np
from utils import analysis_utils
from functools import reduce
import datetime
import base64
import time
from utils import center_db
import importlib
from utils.ui_utils import get_base64_of_bin_file

# Force reload DB module to pick up new schema/functions
importlib.reload(center_db)

# Init DB on load
center_db.init_db()

# --- One-time Cache Clear for Auth Fix ---
if 'auth_fix_cleared' not in st.session_state:
    st.cache_data.clear()
    st.session_state['auth_fix_cleared'] = True
    st.rerun()

# --- One-time Cache Clear V2 (For Scope Fix) ---
if 'scope_fix_cleared' not in st.session_state:
    st.cache_data.clear()
    st.session_state['scope_fix_cleared'] = True
    st.image("https://media.giphy.com/media/l0HlHJGHe3yAMhdQY/giphy.gif", caption="배관 뚫는 중...", width=100)
    st.rerun()

def show_dashboard(df_raw=None): # df_raw is optional now as we use DB
    # --- CSS Styling (Same Premium Style) ---
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;900&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .stApp { background-color: #f8f9fa; }
        [data-testid="stVerticalBlockBorderWrapper"] {
            border: none !important; border-radius: 16px !important;
            background-color: #ffffff; box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            margin-bottom: 24px; padding: 25px;
        }
        .section-title {
            font-family: 'Inter', sans-serif; font-weight: 900; font-size: 18px;
            color: #1B263B; margin-bottom: 10px; text-transform: uppercase;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # --- Init Session State for View ---
    if 'center_view' not in st.session_state:
        st.session_state['center_view'] = 'dashboard' # Default

    # --- Header Layout (Logo | Dashboard | Settings + Account) ---
    logo_path = "assets/logo_center_user.png"
    logo_base64 = get_base64_of_bin_file(logo_path)
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" width="80" style="vertical-align: middle;">' if logo_base64 else "⚽"

    # Layout: [Left: Logo+Title (4)] [Center: Dash (2)] [Right: Set+User (2)]
    # We use empty container for spacing if needed
    h_col1, h_col2, h_col3 = st.columns([5, 1, 2], gap="small")
    
    # Col 1: Logo + Title
    with h_col1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; height: 80px;"> 
            <div style="margin-right: 20px;">{logo_html}</div>
            <div style="display: flex; flex-direction: column; justify-content: center;">
                <div style="font-family: 'Inter'; font-size: 24px; font-weight: 900; color: #1B263B; line-height: 1.1; margin-bottom: 4px;">윤청구 퍼포먼스 트레이닝 센터</div>
                <div style="font-family: 'Inter'; font-size: 15px; font-weight: 500; color: #415A77; letter-spacing: -0.01em;">Player Performance Management System</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Col 2: Dashboard Button (Center)
    with h_col2:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True) # Vertical Align Spacer
        # Use a button that looks like a tab? Or just a primary button if active.
        # Simple Button approach
        type_dash = "primary" if st.session_state['center_view'] == 'dashboard' else "secondary"
        if st.button("📊 대시보드", key="nav_dash", type=type_dash, use_container_width=True):
            st.session_state['center_view'] = 'dashboard'
            st.rerun()

    # Col 3: Settings + User (Right)
    with h_col3:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True) # Vertical Align Spacer
        c_set, c_user = st.columns([1, 1])
        with c_set:
            type_set = "primary" if st.session_state['center_view'] == 'settings' else "secondary"
            if st.button("⚙️ 설정", key="nav_set", type=type_set, use_container_width=True):
                st.session_state['center_view'] = 'settings'
                st.rerun()
        with c_user:
             # User Profile (Static for now)
             st.markdown("""
             <div style="display: flex; align-items: center; justify-content: center; height: 38px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #fff;">
                <span style="font-size: 20px; margin-right: 5px;">👤</span>
                <span style="font-size: 14px; font-weight: 600; color: #1B263B;">Admin</span>
             </div>
             """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 0px 0px 30px 0px; border-top: 1px solid #e0e0e0;'>", unsafe_allow_html=True)

    # --- Main Content Router ---
    current_view = st.session_state['center_view']
    
    # CASE 1: Settings
    if current_view == 'settings':
        st.markdown('<div class="section-title">🛠️ 시스템 관리 (Settings)</div>', unsafe_allow_html=True)
        
        tab_list, tab_reg, tab_entry = st.tabs(["1. 선수 명단 (Player List)", "2. 선수 등록 (Register)", "3. 데이터 입력 (Data Entry)"])
        
        # --- 1-0. 선수 명단 ---
        with tab_list:
            players_df = center_db.get_all_players()
            if players_df.empty:
                st.info("등록된 선수가 없습니다.")
            else:
                with st.container(border=True):
                    st.markdown(f"**총 등록 선수: {len(players_df)}명**")
                    
                    # Player List (View Only)
                    st.dataframe(
                        players_df,
                        column_config={
                            "player_id": "ID", "name": "이름", "dob": "생년월일",
                            "sport": "종목", "position": "포지션", "team": "소속팀",
                            "phone": "연락처", "created_at": "등록일시"
                        },
                        hide_index=True, use_container_width=True
                    )
                    
                    st.markdown("---")
                    # Delete Section
                    with st.expander("🗑️ 선수 삭제 (Delete Player)", expanded=False):
                        st.warning("경고: 선수를 삭제하면 해당 선수의 **모든 측정 및 재활 데이터가 영구적으로 삭제**됩니다.")
                        del_id = st.selectbox("삭제할 선수 선택", 
                                              options=players_df['player_id'].tolist(),
                                              format_func=lambda x: f"{players_df[players_df['player_id']==x]['name'].values[0]} ({x})")
                        
                        if st.button("선수 삭제 (Delete)", type="primary"):
                            if center_db.delete_player(del_id):
                                st.success("삭제되었습니다.")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("삭제 실패")
        
        # --- 1-1. 선수 등록 ---
        with tab_reg:
            with st.container(border=True):
                st.subheader("신규 선수 등록")
                with st.form("reg_form"):
                    col1, col2 = st.columns(2)
                    name = col1.text_input("선수명 (Name)")
                    dob = col2.date_input("생년월일 (DOB)", min_value=datetime.date(1980,1,1))
                    col3, col4 = st.columns(2)
                    team = col3.text_input("소속팀 (Team)")
                    sport = col4.text_input("종목 (Sport)", value="Soccer")
                    col5, col6 = st.columns(2)
                    position = col5.text_input("포지션 (Position)")
                    phone = col6.text_input("휴대폰 번호 (Phone)")
                    
                    if st.form_submit_button("선수 등록"):
                        if name:
                            success, msg = center_db.add_player(name, dob.strftime("%Y-%m-%d"), sport, position, team, phone)
                            if success: st.success(msg)
                            else: st.error(msg)
                        else: st.warning("이름 필수")
                            
        # --- 1-2. 데이터 입력 ---
        with tab_entry:
            players_df = center_db.get_all_players()
            if players_df.empty:
                st.warning("선수를 먼저 등록해주세요.")
            else:
                p_opts = {f"{row['name']} ({row['player_id']})": row['player_id'] for _, row in players_df.iterrows()}
                with st.container(border=True):
                    sel_p_label = st.selectbox("선수 선택", list(p_opts.keys()))
                    sel_p_id = p_opts[sel_p_label]
                    entry_date = st.date_input("측정 날짜", value=datetime.date.today())
                    
                    e_type = st.radio("입력 유형", ["Physical & Power", "Rehabilitation (재활)"], horizontal=True)
                    
                    if e_type == "Physical & Power":
                        with st.form("phy_form"):
                            st.markdown("**1. Body / 2. Power / 3. Machine**")
                            # Shortened for brevity in templating, assuming same fields as before
                            c1, c2, c3, c4 = st.columns(4)
                            h = c1.number_input("신장 (cm)", step=0.1)
                            w = c2.number_input("체중 (kg)", step=0.1)
                            m = c3.number_input("근육량 (kg)", step=0.1)
                            f = c4.number_input("체지방량 (kg)", step=0.1)
                            
                            p1, p2, p3 = st.columns(3)
                            sq = p1.number_input("Squat 1RM", step=1.0)
                            bp = p2.number_input("Bench 1RM", step=1.0)
                            dl = p3.number_input("Deadlift 1RM", step=1.0)
                            
                            m1, m2 = st.columns(2)
                            pu = m1.number_input("Pull Up", step=1.0)
                            epoc = m2.number_input("EPOC", step=1.0)

                            if st.form_submit_button("저장"):
                                d = {"player_id": sel_p_id, "date": entry_date.strftime("%Y-%m-%d"), "height":h, "weight":w, "muscle_mass":m, "fat_mass":f, "squat_1rm":sq, "bench_1rm":bp, "deadlift_1rm":dl, "pull_up":pu, "epoc":epoc}
                                s, msg = center_db.add_daily_record(d)
                                if s: st.success(msg)
                                else: st.error(msg)
                    else:
                        with st.form("rehab_form"):
                            st.markdown("**Rehab Record**")
                            diag = st.text_input("진단명")
                            stage = st.selectbox("단계", ["수술 직후", "초기", "중기", "복귀", "팀 훈련"])
                            ret_date = st.date_input("복귀 예정일")
                            if st.form_submit_button("저장"):
                                d = {"player_id": sel_p_id, "date": entry_date.strftime("%Y-%m-%d"), "diagnosis":diag, "stage":stage, "return_date":ret_date.strftime("%Y-%m-%d")}
                                s, msg = center_db.add_rehab_record(d)
                                if s: st.success(msg)
                                else: st.error(msg)

    # CASE 2: Dashboard (Default)
    elif current_view == 'dashboard':
        players_df = center_db.get_all_players()
        if players_df.empty:
             # Just show VALD players if DB is empty
             players_df = pd.DataFrame(columns=['player_id', 'name']) # Empty schema

        p_opts = {f"{row['name']} ({row['player_id']})": row['player_id'] for _, row in players_df.iterrows()}
        
        # --- Merge VALD Players ---
        from utils import vald_data_loader
        import importlib
        importlib.reload(vald_data_loader) # Force reload to pick up new function
        vald_names = vald_data_loader.get_vald_player_list()
        
        # Add VALD names that aren't already matched (simple string match)
        # Note: 'row.name' is local name. 'vald_name' is from Sheet.
        local_names = set(players_df['name'].values)
        
        for v_name in vald_names:
            if v_name not in local_names:
                # Add as a special entry
                p_opts[f"{v_name} (VALD Only)"] = v_name # ID is the string Name itself

        # Sort options for better UX
        # p_opts = dict(sorted(p_opts.items())) # Optional

        # --- Dashboard Layout (Ultra Compact) ---
        # Filter Bar: Right aligned, Minimal height
        # Title is redundant since we are in "Dashboard". Just show the filter.
        f_col1, f_col2 = st.columns([4, 1])
        with f_col2:
            # Right-aligned filter
            sel_label = st.selectbox("선수 선택", list(p_opts.keys()), label_visibility="collapsed")
            # sel_label = "서민우 (1)" or "Minwoo (VALD Only)"
            sel_id_or_name = p_opts[sel_label]
            
            # --- Name Resolution Logic (Refactored) ---
            # Goal: Always get the clean 'Name' for VALD querying, regardless of the 'ID' format.
            
            # 1. Ensure ID is string for consistent lookup
            query_id_str = str(sel_id_or_name)
            
            # 2. Try to find player in local DB
            # We convert the DF column to string on the fly to match query_id_str
            players_df['id_str'] = players_df['player_id'].astype(str)
            matched_row = players_df[players_df['id_str'] == query_id_str]
            
            if not matched_row.empty:
                # Case A: Found in DB
                # Use the stored Name (e.g., "(18)안 선우")
                player_name_query = matched_row.iloc[0]['name']
                sel_pid_dash = sel_id_or_name # Keep original ID for DB queries
            else:
                # Case B: Not in DB (likely "VALD Only" or purely manual)
                # Parse search name from the label (e.g. "Name (VALD Only)")
                # sel_label might be "Name (VALD Only)" -> extract "Name"
                if "(VALD Only)" in sel_label:
                    player_name_query = sel_label.replace("(VALD Only)", "").strip()
                elif "(" in sel_label and ")" in sel_label:
                     # Fallback for "Name (ID)" format if lookup failed
                     player_name_query = sel_label.split("(")[0].strip()
                else:
                    player_name_query = str(sel_label)
                    
                sel_pid_dash = None

            # 3. Final Safety Cleaning (Double Check)
            # If the name somehow still looks like an ID (contains "_"), take the first part
            if "_" in player_name_query and any(char.isdigit() for char in player_name_query):
                 parts = player_name_query.split("_")
                 if len(parts) > 1:
                     player_name_query = parts[0]
            
            # [REMOVED] User requested to search EXACTLY as is.
            # Do NOT strip (18) or similar prefixes, because they ARE part of the name in VALD.
            # import re
            # player_name_query = re.sub(r'^\(\d+\)\s*', '', player_name_query).strip()
            
            # ------------------------------------------
        
        df_rec = center_db.get_player_records(sel_pid_dash) if sel_pid_dash else pd.DataFrame()
        df_rehab = center_db.get_player_rehab(sel_pid_dash) if sel_pid_dash else pd.DataFrame()
        
        # Tabs
        # Tabs
        d_tab1, d_tab2, d_tab3, d_tab_insight, d_tab4, d_tab_a400 = st.tabs(["누적 데이터", "재활 현황", "VALD", "Insight Analysis", "KEISER", "A400 Tool"])
        
        with d_tab1:
            if not df_rec.empty:
                st.markdown("##### 📈 1RM Trend")
                fig = px.line(df_rec, x='date', y=['squat_1rm', 'bench_1rm', 'deadlift_1rm'], markers=True)
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("데이터 없음")

            # --- VALD Data Section ---
            st.markdown("---")
            st.markdown("### 📊 VALD Performance Trend")
            
            # VALD Section moved to Tab 3
            pass

        with d_tab2:
            if not df_rehab.empty:
                st.dataframe(df_rehab)
            else: st.info("재활 기록 없음")
            
        with d_tab3: # VALD Tab
            st.markdown("### 📊 VALD Performance Analysis")
            
            # DEBUG: Show final query name to User
            st.info(f"🔍 Searching Name: '{player_name_query}'")
            
            # Load Data (if not loaded yet)
            from utils import vald_data_loader
            vald_data = vald_data_loader.load_vald_data(player_name_query)
            
            # --- DEBUG INFO ---
            with st.expander("🛠️ 데이터 로딩 디버그 (클릭해서 확인)", expanded=True):
                st.write(f"1. 검색하는 이름: '{player_name_query}'")
                st.write(f"2. 로드된 데이터 결과:")
                for k, v in vald_data.items():
                    st.write(f"- 테이블 '{k}': {len(v)} 행 (Rows)")
            # ------------------
            
            has_vald_data = False
            for test_name, v_df in vald_data.items():
                if not v_df.empty:
                    has_vald_data = True
                    st.markdown(f"#### {test_name}")
                    
                    # DEBUG: Show columns to fix mapping
                    with st.expander(f"🔍 {test_name} Raw Data & Columns (Debug)", expanded=True):
                        st.write("Columns:", v_df.columns.tolist())
                        st.markdown("##### Raw Data Table")
                        st.dataframe(v_df, use_container_width=True)

                    # Define metrics to plot for each test type (Refining based on likely schema)
                    # We will use flexible matching or generic plotting first
                    metrics_map = {
                        "vald_cmj": ["Jump_Height", "Peak_Power_BM", "RSI_Modified", "Jump Height", "Peak Power / BM", "RSI-modified"], 
                        "vald_nordbord": ["Max_Force_Left", "Max_Force_Right", "Imbalance_Max_Force", "Max Force Left (N)", "Max Force Right (N)"],
                        "vald_forceframe": ["Max_Force_Left", "Max_Force_Right", "Max Force Left (N)", "Max Force Right (N)"],
                        "vald_sj": ["Jump_Height", "Peak_Power_BM", "Jump Height", "Peak Power / BM"],
                        "vald_hj": ["Jump_Height", "RSI", "Jump Height"]
                    }
                    # Note: keys in vald_data are "Make"(=CMJ), "Nordbord" etc defined in loader.
                    # Dictionary keys in vald_data_loader are: "Make" (should be CMJ), "Nordbord", "ForceFrame", "SJ", "HJ"
                    
                    # Mapping loader keys to metric keys
                    key_map = {
                        "Make": "vald_cmj", "Nordbord": "vald_nordbord", "ForceFrame": "vald_forceframe",
                         "SJ": "vald_sj", "HJ": "vald_hj"
                    }
                    metric_key = key_map.get(test_name, test_name)
                    
                    # --- Flexible Keyword-Based Column Matching ---
                    # Instead of exact names, we look for columns containing specific keywords.
                    # This handles BigQuery's auto-renaming (e.g. "Jump Height (cm)" -> "Jump_Height__cm_")
                    
                    target_cols = []
                    all_cols = v_df.columns.tolist()
                    
                    # Keywords definition for each test
                    # Format: TestKey: [List of keywords to search for]
                    keyword_map = {
                        "vald_cmj": ["Jump Height", "Peak Power", "RSI", "Imp-Mom", "Flight Time"],
                        "vald_nordbord": ["Max Force", "Force", "Imbalance", "Torque"],
                        "vald_forceframe": ["Max Force", "Strength", "Peak Force"],
                        "vald_sj": ["Jump Height", "Peak Power"],
                        "vald_hj": ["Jump Height", "RSI", "Rebound"]
                    }
                    
                    metric_key = key_map.get(test_name, test_name)
                    keywords = keyword_map.get(metric_key, [])
                    
                    # Find columns that match keywords (Case Insensitive)
                    # We accept a column if it contains ANY of the keywords AND is numeric
                    # Exclude some metadata like 'Date', 'ID', 'Year'
                    excludes = ['Date', 'ID', 'Year', 'Month', 'Day', 'Time', 'Trial']
                    
                    numeric_cols = v_df.select_dtypes(include=['number']).columns.tolist()
                    
                    for col in numeric_cols:
                        # Skip if likely metadata
                        if any(ex.lower() in col.lower() for ex in excludes):
                             continue
                        
                        # Check against keywords
                        # If keyword list is empty (unknown test), maybe just add all? 
                        # But for known tests, strictly match keywords.
                        if keywords:
                            for kw in keywords:
                                # Clean string for comparison (ignore underscores vs spaces)
                                c_clean = col.replace('_', ' ').lower()
                                k_clean = kw.lower()
                                if k_clean in c_clean:
                                    target_cols.append(col)
                                    break
                        else:
                             # Fallback: Add all non-excluded numeric cols
                             target_cols.append(col)
                    
                    # Sort or prioritize? (Optional)
                    target_cols = sorted(list(set(target_cols))) 

                    if target_cols:
                        # Time Series Line Chart
                        # Find Date Column
                        date_candidates = [c for c in v_df.columns if 'date' in c.lower() or 'time' in c.lower()]
                        date_col = 'Test_Date' # Default
                        if 'Test_Date' in v_df.columns: date_col = 'Test_Date'
                        elif date_candidates: date_col = date_candidates[0]
                        else: date_col = v_df.columns[0] # Ultimate fallback

                        fig_v = px.line(v_df, x=date_col, y=target_cols, markers=True, 
                                        title=f"{test_name} Trend ({len(target_cols)} metrics found)")
                        st.plotly_chart(fig_v, use_container_width=True)
                    else:
                        st.warning(f"'{test_name}': 그래프를 그릴 수치 컬럼을 찾지 못했습니다.")
                        st.caption(f"검색 키워드: {keywords}")

            if not has_vald_data:
                 st.info(f"데이터가 없습니다. (ID: {player_name_query})")
                 st.caption("팁: DB의 이름과 VALD 시트의 이름이 정확히 일치해야 합니다.")
            
        with d_tab_insight:
            st.markdown('<div class="section-title">심층 분석 (Insight Analysis)</div>', unsafe_allow_html=True)
            
            # Helper to find columns with synonyms
            def find_col(df, candidates):
                cols_lower = {c.lower(): c for c in df.columns}
                for cand in candidates:
                    # 1. Exact or Underscore match (case insensitive)
                    c_clean = cand.lower().replace(" ", "_")
                    for cl, original in cols_lower.items():
                        if c_clean in cl.replace(" ", "_"):
                             return original
                return None

            # --- 1. EUR (CMJ + SJ) ---
            st.markdown("### 1. Eccentric Utilization Ratio (EUR)")
            # Try to get data from VALD tabs
            # vald_data keys: "Make" (CMJ), "SJ", "Nordbord", "ForceFrame"
            df_cmj = vald_data.get('Make', vald_data.get('CMJ', pd.DataFrame()))
            df_sj = vald_data.get('SJ', pd.DataFrame())
            
            col_cmj = find_col(df_cmj, ['Jump Height', 'Height', 'Flight Time']) if not df_cmj.empty else None
            col_sj = find_col(df_sj, ['Jump Height', 'Height']) if not df_sj.empty else None
            
            if col_cmj and col_sj:
                 # Merge on Date (rounding to day)
                 df_cmj['Date_Day'] = pd.to_datetime(df_cmj['Test_Date']).dt.date
                 df_sj['Date_Day'] = pd.to_datetime(df_sj['Test_Date']).dt.date
                 # Merge
                 merged_eur = pd.merge(df_cmj, df_sj, on='Date_Day', suffixes=('_CMJ', '_SJ'))
                 merged_eur['Name'] = player_name_query
                 
                 eur_df = analysis_utils.calculate_eur(merged_eur, f"{col_cmj}_CMJ", f"{col_sj}_SJ")
                 if not eur_df.empty:
                      fig_eur = analysis_utils.plot_eur(eur_df, f"{col_cmj}_CMJ", f"{col_sj}_SJ")
                      st.plotly_chart(fig_eur, use_container_width=True)
                 else:
                      st.info("EUR 계산 불가 (날짜 매칭 실패 또는 데이터 부족)")
            else:
                 st.info("EUR 데이터 부족 (CMJ 또는 SJ 높이 데이터 누락)")

            st.divider()

            # --- 2. Asymmetry (SLJ) ---
            st.markdown("### 2. Limb Asymmetry Watchlist")
            # If SLJ table exists?
            df_slj = vald_data.get('SJ', pd.DataFrame()) # Assuming SLJ might be mixed or missing
            # Check for Asymmetry columns in CMJ or Nordbord if SLJ specific not found
            # For now, placeholder
            st.info("SLJ (Single Leg Jump) 데이터 연동 필요")

            st.divider()

            # --- 3. Groin Risk (ForceFrame) ---
            st.markdown("### 3. Groin Risk (Add/Abd Ratio)")
            df_ff = vald_data.get('ForceFrame', pd.DataFrame())
            if not df_ff.empty:
                 # Adductor
                 c_add_l = find_col(df_ff, ['Adductor Max Force [L]', 'Add Max Force L', 'Left Adductor', 'Max Force Left'])
                 c_add_r = find_col(df_ff, ['Adductor Max Force [R]', 'Add Max Force R', 'Right Adductor', 'Max Force Right'])
                 # Abductor (often in separate test type rows in raw export, but if pivoted in DB...)
                 # Assume wide format for now
                 c_abd_l = find_col(df_ff, ['Abductor Max Force [L]', 'Abd Max Force L', 'Left Abductor'])
                 c_abd_r = find_col(df_ff, ['Abductor Max Force [R]', 'Abd Max Force R', 'Right Abductor'])
                 
                 # If Abductor missing, maybe we can't calculate ratio.
                 if c_add_l and c_add_r:
                      df_ff['Name'] = player_name_query
                      if c_abd_l and c_abd_r:
                           groin_df = analysis_utils.calculate_groin_risk(df_ff, c_add_l, c_add_r, c_abd_l, c_abd_r)
                           if not groin_df.empty:
                                fig_groin = analysis_utils.plot_groin_risk(groin_df)
                                st.plotly_chart(fig_groin, use_container_width=True)
                           else:
                                st.info("Groin Risk 계산 실패")
                      else:
                           st.warning("Abductor (외전근) 데이터 미식별. Ratio 계산 불가.")
                 else:
                      st.info("ForceFrame 필수 컬럼 식별 실패")
            else:
                 st.info("ForceFrame 데이터 없음")

            st.divider()

            # --- 4. Hamstring (NordBord) ---
            st.markdown("### 4. Hamstring Robustness")
            df_nb = vald_data.get('Nordbord', pd.DataFrame())
            if not df_nb.empty:
                 c_nb_l = find_col(df_nb, ['Max Force [L]', 'Max Force Left', 'Left Max Force'])
                 c_nb_r = find_col(df_nb, ['Max Force [R]', 'Max Force Right', 'Right Max Force'])
                 
                 if c_nb_l and c_nb_r:
                      df_nb['Name'] = player_name_query
                      ham_df = analysis_utils.calculate_hamstring_robustness(df_nb, c_nb_l, c_nb_r)
                      if not ham_df.empty:
                           fig_ham = analysis_utils.plot_hamstring_robustness(ham_df)
                           st.plotly_chart(fig_ham, use_container_width=True)
                 else:
                      st.info("NordBord 컬럼 식별 실패")
            else:
                 st.info("NordBord 데이터 없음")
            
        with d_tab4:
             st.info("KEISER Analysis (준비 중)")

        with d_tab_a400:
             st.components.v1.iframe("https://a400.onrender.com/", height=800, scrolling=True)
