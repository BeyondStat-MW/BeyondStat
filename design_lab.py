import streamlit as st

st.set_page_config(layout="wide")

# Mock CSS Injection
st.markdown("""
<style>
    /* Premium Card Container */
    .premium-card {
        background-color: white; 
        border-radius: 12px; 
        padding: 20px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); 
        border: 1px solid #f0f0f0; 
        width: 100%;
        max-width: 320px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .card-title {
        font-size: 15px; 
        font-weight: 800; 
        color: #111; 
        border-bottom: 2px solid #006442; 
        padding-bottom: 8px; 
        margin-bottom: 15px;
        letter-spacing: -0.3px;
    }
    .metric-row {
        display: flex; 
        justify-content: space-between; 
        align-items: center;
        margin-bottom: 12px; 
        font-size: 13px;
    }
    .metric-label {
        color: #666; 
        font-weight: 500;
    }
    .metric-value {
        font-weight: 700; 
        color: #333;
        display: flex;
        align-items: center;
        gap: 6px; /* Gap for units/icons */
    }
    small {
        font-size: 11px;
        color: #888;
        font-weight: 400;
    }
</style>
""", unsafe_allow_html=True)

# Helper for rendering
def render_card(title, option_type):
    # Base Data
    val_cmj = 31.2
    del_cmj = 5.2
    
    val_sj = 31.1
    del_sj = -2.1
    
    val_eur = 1.00
    del_eur = 0.0
    
    # Logic for rendering based on type
    def format_delta(val, delta, unit="cm"):
        color = "#006442" if delta > 0 else "#d62728" if delta < 0 else "gray"
        arrow = "▲" if delta > 0 else "▼" if delta < 0 else "-"
        # bg_color is for badge
        bg_color = "rgba(0, 100, 66, 0.1)" if delta > 0 else "rgba(214, 39, 40, 0.1)" if delta < 0 else "rgba(128,128,128,0.1)"
        
        val_str = f"{val:.1f} <small>{unit}</small>"
        
        if option_type == "A": # Classic Arrow
            return f"{val_str} <span style='color:{color}; font-size:11px; margin-left:4px;'>{arrow} {abs(delta):.1f}%</span>"
            
        elif option_type == "B": # Badge
            return f"""
            <div style='display:flex; align-items:center;'>
                <span>{val_str}</span>
                <span style='
                    background-color:{bg_color}; 
                    color:{color}; 
                    border-radius:12px; 
                    padding:2px 6px; 
                    font-size:10px; 
                    font-weight:700; 
                    margin-left:6px;'>
                    {"+" if delta>0 else ""}{delta:.1f}%
                </span>
            </div>
            """
            
        elif option_type == "C": # Stacked (Mini Text Below)
            return f"""
            <div style='display:flex; flex-direction:column; align-items:flex-end; line-height:1.1;'>
                <span>{val_str}</span>
                <span style='color:{color}; font-size:10px;'>{arrow} {abs(delta):.1f}% vs last</span>
            </div>
            """
            
    # Generate HTML
    html = f"""
    <div class="premium-card">
        <div class="card-title">{title}</div>
        
        <div class="metric-row">
            <span class="metric-label">CMJ Height</span>
            <span class="metric-value">{format_delta(val_cmj, del_cmj)}</span>
        </div>
        
        <div class="metric-row">
            <span class="metric-label">Squat Jump</span>
            <span class="metric-value">{format_delta(val_sj, del_sj)}</span>
        </div>
        
         <div class="metric-row">
            <span class="metric-label">EUR</span>
            <span class="metric-value">{format_delta(val_eur, del_eur, "")}</span>
        </div>
        
        <div style="text-align: right; margin-top: 15px; border-top: 1px solid #eee; padding-top: 10px;">
             <span style="display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; color: white; background-color: #1f77b4;">Normal</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

st.header("🎨 Option Comparison")

c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("Option A: Classic Arrow")
    render_card("⚡ Jump & Elasticity", "A")

with c2:
    st.subheader("Option B: Modern Badge")
    render_card("⚡ Jump & Elasticity", "B")

with c3:
    st.subheader("Option C: Stacked Info")
    render_card("⚡ Jump & Elasticity", "C")
