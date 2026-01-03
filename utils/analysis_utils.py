import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# 1. Eccentric Utilization Ratio (EUR)
# ==============================================================================
def calculate_eur(df, col_cmj, col_sj):
    """
    Returns aggregated DataFrame with 'EUR' column.
    Formula: EUR = CMJ / Squat Jump
    """
    if col_cmj not in df.columns or col_sj not in df.columns:
        return pd.DataFrame()
        
    df = df.dropna(subset=[col_cmj, col_sj])
    if df.empty: return pd.DataFrame()
    
    eur_df = df.groupby('Name')[[col_cmj, col_sj]].mean().reset_index()
    eur_df['EUR'] = eur_df[col_cmj] / eur_df[col_sj]
    
    # Classification
    def get_status(x):
        if x > 1.15: return 'High Elasticity (> 1.15)'
        elif x >= 1.0: return 'Normal (1.0 - 1.15)'
        else: return 'Low Elasticity (< 1.0)'
        
    eur_df['Status'] = eur_df['EUR'].apply(get_status)
    return eur_df

def plot_eur(eur_df, col_cmj, col_sj):
    """
    Generates EUR Scatter Plot with new thresholds.
    """
    if eur_df.empty: return None
    
    color_map = {
        'High Elasticity (> 1.15)': '#00CC96', # Green
        'Normal (1.0 - 1.15)': '#636EFA',      # Blue/Purple
        'Low Elasticity (< 1.0)': '#EF553B'    # Red
    }
    
    fig = px.scatter(eur_df, x=col_sj, y=col_cmj, text='Name', 
                     color='Status', color_discrete_map=color_map,
                     hover_data=['EUR'],
                     size_max=10, 
                     labels={col_sj: "Squat Jump (cm)", col_cmj: "CMJ (cm)"},
                     title="Elasticity Profiling (CMJ vs SquatJump)")
    
    # Reference Lines
    max_val = max(eur_df[col_cmj].max(), eur_df[col_sj].max()) * 1.1
    
    # 1.0 Line
    fig.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, line=dict(color="Gray", dash="dash"))
    fig.add_annotation(x=max_val, y=max_val, text="EUR 1.0", showarrow=False)

    # 1.15 Line
    fig.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val*1.15, line=dict(color="Green", dash="dot"))
    fig.add_annotation(x=max_val, y=max_val*1.15, text="EUR 1.15", showarrow=False)
    
    fig.update_traces(textposition='top center', marker=dict(size=10, line=dict(width=1, color='DarkSlateGrey')))
    return fig

# ==============================================================================
# 2. Limb Asymmetry (SLJ)
# ==============================================================================
def calculate_asymmetry(df, col_l, col_r):
    """
    Returns aggregated DataFrame with 'Asymmetry' column.
    Formula: (R - L) / Max(R, L) * 100
    """
    if col_l not in df.columns or col_r not in df.columns:
        return pd.DataFrame()

    valid_df = df.dropna(subset=[col_l, col_r])
    if valid_df.empty: return pd.DataFrame()
    
    asy_df = valid_df.groupby('Name')[[col_l, col_r]].mean().reset_index()
    asy_df['Max_Val'] = asy_df[[col_l, col_r]].max(axis=1)
    # Use standard formula implies Direction. (R-L)/Max. 
    # But usually for 'Imbalance' magnitude we use Abs in reporting, but R-L is good for direction.
    asy_df['Asymmetry'] = ((asy_df[col_r] - asy_df[col_l]) / asy_df['Max_Val']) * 100
    
    # Default Classification (Threshold=15 as base, but can be overridden)
    # We will just return the value. Classification creates 'Status' column if needed.
    return asy_df

def plot_asymmetry_lollipop(asy_df, title="Limb Asymmetry Watchlist", threshold=10):
    """
    Generates Lollipop Chart for Asymmetry.
    """
    if asy_df.empty: return None
    
    # Sort for lollipop
    asy_df = asy_df.sort_values('Asymmetry')
    
    # Color logic
    asy_df['Color'] = asy_df['Asymmetry'].apply(lambda x: '#FF4B4B' if abs(x) > threshold else '#006442')
    
    # Determine tick colors based on risk and format as HTML
    tick_text_colored = [
        f"<span style='color:{color}'><b>{name}</b></span>" 
        for name, color in zip(asy_df['Name'], asy_df['Color'])
    ]

    # Create Stems using Scatter with None to break lines
    # This is more robust for categorical axes than shapes
    x_lines = []
    y_lines = []
    for index, row in asy_df.iterrows():
        x_lines.extend([0, row['Asymmetry'], None])
        y_lines.extend([row['Name'], row['Name'], None])

    fig = go.Figure()
    
    # 1. Stems (Grey Lines)
    fig.add_trace(go.Scatter(
        x=x_lines,
        y=y_lines,
        mode='lines',
        line=dict(color='grey', width=1),
        hoverinfo='skip',
        showlegend=False
    ))
        
    # 2. Markers
    fig.add_trace(go.Scatter(
        x=asy_df['Asymmetry'],
        y=asy_df['Name'],
        mode='markers',
        marker=dict(color=asy_df['Color'], size=10, line=dict(width=1, color='white')),
        text=asy_df['Asymmetry'].apply(lambda x: f"{x:.1f}%"),
        hovertemplate='<b>%{y}</b><br>Asymmetry: %{text}<extra></extra>'
    ))
    
    # Threshold Lines
    fig.add_vline(x=threshold, line_dash="dash", line_color="red", opacity=0.5)
    fig.add_vline(x=-threshold, line_dash="dash", line_color="red", opacity=0.5)
    
    # Dynamic Range padding
    max_val = max(50, asy_df['Asymmetry'].abs().max() * 1.2)
    
    fig.update_layout(
        title=title,
        yaxis=dict(
            title=None, 
            type='category',
            tickmode='array',
            tickvals=asy_df['Name'].tolist(),
            ticktext=tick_text_colored
        ),
        xaxis=dict(title="Asymmetry (%)", range=[-max_val, max_val]),
        showlegend=False,
        height=max(400, len(asy_df) * 30),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def plot_asymmetry_scatter(df, col_l, col_r, metric_name="Strength", threshold=15):
    """
    Generates Scatter Plot (Quad Analysis): Strength (Sum) vs Asymmetry.
    """
    if col_l not in df.columns or col_r not in df.columns: return None
    
    clean_df = df.dropna(subset=[col_l, col_r]).copy()
    if clean_df.empty: return None
    
    # Aggregation
    agg_df = clean_df.groupby('Name')[[col_l, col_r]].mean().reset_index()
    agg_df['Sum'] = agg_df[col_l] + agg_df[col_r]
    agg_df['Max'] = agg_df[[col_l, col_r]].max(axis=1)
    agg_df['Asymmetry_Abs'] = abs(((agg_df[col_r] - agg_df[col_l]) / agg_df['Max']) * 100) # Use Absolute for Y-axis
    
    avg_strength = agg_df['Sum'].mean()
    
    # Quadrant Classification
    def classify(row):
        if row['Asymmetry_Abs'] > threshold:
            return 'High Risk (Weak)' if row['Sum'] < avg_strength else 'Imbalanced (Strong)'
        else:
            return 'Balanced (Weak)' if row['Sum'] < avg_strength else 'Well Developed'
            
    agg_df['Status'] = agg_df.apply(classify, axis=1)
    color_map = {
        'High Risk (Weak)': '#d62728', 
        'Imbalanced (Strong)': '#ff7f0e',
        'Balanced (Weak)': '#1f77b4',
        'Well Developed': '#2ca02c'
    }
    
    fig = px.scatter(
        agg_df, x='Sum', y='Asymmetry_Abs', 
        color='Status', color_discrete_map=color_map,
        text='Name',
        title=f"Scatter Analysis: {metric_name} vs Imbalance",
        labels={'Sum': f"{metric_name} Sum (N)", 'Asymmetry_Abs': "Asymmetry (%)"}
    )
    
    fig.add_hline(y=threshold, line_dash="dot", line_color="red", annotation_text=f"Limit {threshold}%")
    fig.add_vline(x=avg_strength, line_dash="dot", line_color="grey", annotation_text="Avg Strength")
    
    fig.update_traces(textposition='top center', marker=dict(size=10))
    return fig

def plot_asymmetry_heatmap(df, metrics_map):
    """
    Generates Heatmap for Multiple Asymmetry Metrics.
    metrics_map: {'Label': (col_l, col_r)}
    """
    if df.empty: return None
    
    res_list = []
    
    for label, (col_l, col_r) in metrics_map.items():
        if col_l in df.columns and col_r in df.columns:
            temp_df = calculate_asymmetry(df, col_l, col_r)
            if not temp_df.empty:
                temp_df = temp_df.set_index('Name')['Asymmetry'].abs() # Use absolute imbalance for heatmap intensity
                temp_df.name = label
                res_list.append(temp_df)
                
    if not res_list: return None
    
    heat_df = pd.concat(res_list, axis=1).fillna(0)
    
    fig = px.imshow(
        heat_df, 
        labels=dict(x="Metric", y="Player", color="Imbalance (%)"),
        x=heat_df.columns,
        y=heat_df.index,
        color_continuous_scale='Reds', # White to Red
        origin='lower',
        title="Multi-Metric Imbalance Heatmap (Absolute %)"
    )
    fig.update_xaxes(side="top")
    return fig

def plot_asymmetry(asy_df, title="Limb Asymmetry (%) : Right(+) vs Left(-)", threshold=10):
    """
    Generates Asymmetry Bar Chart (Diverging).
    threshold: % value for risk line (default 10)
    """
    if asy_df.empty: return None
    
    # Color logic
    asy_df['Color'] = asy_df['Asymmetry'].apply(lambda x: 'red' if abs(x) > threshold else 'green')
    
    fig = px.bar(asy_df.sort_values('Asymmetry'), x='Asymmetry', y='Name', orientation='h',
                 color='Color', color_discrete_map={'red': '#FF4B4B', 'green': '#006442'},
                 text_auto='.1f', title=title)
    
    fig.add_vline(x=threshold, line_dash="dash", line_color="red")
    fig.add_vline(x=-threshold, line_dash="dash", line_color="red")
    fig.update_layout(
        height=height,
        xaxis_title="Abductor Strength (N)",
        yaxis_title="Adductor Strength (N)",
        showlegend=False
    )
    fig.update_traces(textposition='top center')
    return fig

# ==============================================================================
# 3. Groin Risk (Hip Adductor/Abductor Ratio)
# ==============================================================================
def calculate_groin_risk(df, col_add_l, col_add_r, col_abd_l, col_abd_r):
    """
    Returns aggregated DataFrame with 'Ratio' column.
    Formula: Avg(Add) / Avg(Abd)
    """
    required = [col_add_l, col_add_r, col_abd_l, col_abd_r]
    if not all(c in df.columns for c in required):
        return pd.DataFrame()
        
    groin_df = df.groupby('Name')[required].mean().reset_index()
    groin_df['Add_Avg'] = (groin_df[col_add_l] + groin_df[col_add_r]) / 2
    groin_df['Abd_Avg'] = (groin_df[col_abd_l] + groin_df[col_abd_r]) / 2
    groin_df['Ratio'] = groin_df['Add_Avg'] / groin_df['Abd_Avg']
    return groin_df

def plot_groin_risk(groin_df, height=600):
    """
    Generates Groin Risk Scatter Plot.
    """
    if groin_df.empty: return None
    
    fig = px.scatter(groin_df, x='Abd_Avg', y='Add_Avg', color='Ratio',
                     text='Name', color_continuous_scale='RdYlGn', range_color=[0.5, 1.2],
                     title="Adductor vs Abductor Strength")
    
    max_abd = groin_df['Abd_Avg'].max()
    fig.add_shape(type="line", x0=0, y0=0, x1=max_abd, y1=max_abd*0.8, line=dict(color="Red", dash="dash"), name="Risk (0.8)")
    fig.update_traces(textposition='top center')
    return fig

# ==============================================================================
# 4. Hamstring Robustness (Eccentric vs Asymmetry)
# ==============================================================================
def calculate_hamstring_robustness(df, col_ecc_l, col_ecc_r):
    """
    Returns aggregated DataFrame with 'Ecc_Avg' and 'Asy_Abs'.
    """
    if col_ecc_l not in df.columns or col_ecc_r not in df.columns:
        return pd.DataFrame()
        
    ham_df = df.groupby('Name')[[col_ecc_l, col_ecc_r]].mean().reset_index()
    ham_df['Ecc_Avg'] = (ham_df[col_ecc_l] + ham_df[col_ecc_r]) / 2
    
    ham_df['Max_Ecc'] = ham_df[[col_ecc_l, col_ecc_r]].max(axis=1)
    # Use absolute asymmetry for this chart (Risk Factor)
    ham_df['Asy_Abs'] = (abs(ham_df[col_ecc_l] - ham_df[col_ecc_r]) / ham_df['Max_Ecc']) * 100
    
    # Check for NaNs
    ham_df = ham_df.dropna(subset=['Ecc_Avg', 'Asy_Abs'])
    return ham_df

def plot_hamstring_robustness(ham_df):
    """
    Generates Hamstring Bubble Chart.
    """
    if ham_df.empty: return None
    
    fig = px.scatter(ham_df, x='Ecc_Avg', y='Asy_Abs', text='Name', size='Ecc_Avg',
                     color='Asy_Abs', color_continuous_scale='RdYlGn_r', # Red is high asy
                     labels={'Ecc_Avg': "Avg Strengh (N)", 'Asy_Abs': "Asymmetry (%)"},
                     title="Hamstring: Strength vs Imbalance")
    
    fig.add_hline(y=15, line_dash="dash", line_color="red", annotation_text="High Risk (>15%)")
    fig.add_vline(x=300, line_dash="dash", line_color="orange", annotation_text="Target Str")
    fig.update_traces(textposition='top center')
    return fig

# ==============================================================================
# 5. Neuromuscular Fatigue (Z-Score)
# ==============================================================================
def calculate_z_scores(df_history, df_recent, col_metric):
    """
    Calculates Z-Score for the latest test vs historical mean/std.
    df_history: All available data (for stats)
    df_recent: Recent data (for current status)
    """
    if col_metric not in df_history.columns:
        return pd.DataFrame()

    # 1. Player Stats (Mean/Std) from ALL data
    stats = df_history.groupby('Name')[col_metric].agg(['mean', 'std']).reset_index()
    
    # 2. Get LATEST record per player from recent data
    latest_recs = df_recent.sort_values('Test_Date').groupby('Name').tail(1)[['Name', 'Test_Date', col_metric]]
    
    # 3. Merge
    merged = pd.merge(latest_recs, stats, on='Name')
    merged['Z_Score'] = (merged[col_metric] - merged['mean']) / merged['std']
    
    return merged.dropna(subset=['Z_Score'])

def plot_z_scores(z_df, title="Neuromuscular Fatigue Status"):
    """
    Generates Z-Score Bar Chart.
    """
    if z_df.empty: return None
    
    fig = px.bar(z_df, x='Name', y='Z_Score', color='Z_Score', 
                 color_continuous_scale='RdYlGn', range_color=[-2, 2],
                 title=title)
    
    fig.add_hline(y=-1.5, line_width=2, line_dash="dash", line_color="red")
    fig.add_hline(y=0, line_width=1, line_color="gray")
    return fig

# ==============================================================================
# 6. Physical Tiering System (Periodic Status)
# ==============================================================================
def calculate_physical_tier(df, metrics_dict):
    """
    Calculates composite score based on available metrics and assigns S/A/B/C Tier.
    metrics_dict: {'Power': ['col1', 'col2'], 'Speed': 'col3', ...}
    Supports list of columns for each category.
    """
    if df.empty: return pd.DataFrame()
    
    score_df = df.copy()
    valid_metrics = []
    
    # Calculate Z-score/Rank for each category
    for category, cols in metrics_dict.items():
        # Ensure cols is a list
        if isinstance(cols, str):
            cols = [cols]
            
        category_ranks = []
        
        for col in cols:
            if col in score_df.columns:
                clean_col = score_df[col].fillna(score_df[col].median())
                
                # Check directionality (assuming 'time' or 'asymmetry' is lower-is-better)
                ascending = True
                if 'time' in col.lower() or 'asi' in col.lower() or 'asymmetry' in col.lower():
                     ascending = False
                
                # Percentile Rank (0-100)
                rank = clean_col.rank(ascending=ascending, pct=True) * 100
                category_ranks.append(rank)
        
        if category_ranks:
            # Average rank across all metrics in this category
            # e.g. Power Score = Avg(CMJ Rank, SquatJ Rank)
            avg_rank = pd.concat(category_ranks, axis=1).mean(axis=1)
            score_df[f'{category}_Score'] = avg_rank
            valid_metrics.append(f'{category}_Score')

    if not valid_metrics:
        return pd.DataFrame()

    # Composite Score (Average of Category Scores)
    score_df['Physical_Score'] = score_df[valid_metrics].mean(axis=1)
    
    # Assign Tier
    def assign_tier(score):
        if score >= 80: return 'S'
        elif score >= 60: return 'A'
        elif score >= 40: return 'B'
        else: return 'C'
        
    score_df['Tier'] = score_df['Physical_Score'].apply(assign_tier)
    # Return Name, Tier, Score, and individual category scores
    return score_df[['Name', 'Physical_Score', 'Tier'] + valid_metrics]

def plot_tier_distribution(tier_df):
    if tier_df.empty: return None
    
    counts = tier_df['Tier'].value_counts().reset_index()
    counts.columns = ['Tier', 'Count']
    
    # Fixed order S, A, B, C
    tier_order = ['S', 'A', 'B', 'C']
    counts['Tier'] = pd.Categorical(counts['Tier'], categories=tier_order, ordered=True)
    counts = counts.sort_values('Tier')
    
    fig = px.pie(counts, values='Count', names='Tier', 
                 color='Tier', 
                 color_discrete_map={'S': '#FFD700', 'A': '#C0C0C0', 'B': '#CD7F32', 'C': '#808080'},
                 hole=0.4, title="Physical Tier Distribution")
    fig.update_traces(textinfo='label+percent+value')
    return fig

# ==============================================================================
# 7. Pre-Post Delta Analysis (Development Tracker)
# ==============================================================================
def calculate_pre_post_delta(df_pre, df_post, metrics_dict, join_col='Name'):
    """
    Compares two DataFrames (Pre vs Post) by merging on join_col.
    Calculates % Change (Delta) for each metric.
    """
    if df_pre.empty or df_post.empty:
        return pd.DataFrame()
        
    # Merge
    merged = pd.merge(df_pre, df_post, on=join_col, suffixes=('_Pre', '_Post'))
    
    valid_df = merged[[join_col]].copy()
    
    for category, col in metrics_dict.items():
        c_pre = f"{col}_Pre"
        c_post = f"{col}_Post"
        
        if c_pre in merged.columns and c_post in merged.columns:
            # Calculate Delta %: (Post - Pre) / Pre * 100
            # Handle divide by zero
            # If Time, (Pre - Post) / Pre * 100 ? (Reduction is positive improvement)
            # Standard: (Post - Pre) / Pre
            # We will handle "Improvement is Negative" in visualization or textual interpretation.
            # But for simple delta, we stick to math: (Post - Pre)/Pre
            
            delta_col = f"{category}_Delta"
            
            # Use small epsilon to avoid div/0
            pre_vals = merged[c_pre].replace(0, 0.001)
            
            if 'time' in col.lower() and 'flight' not in col.lower(): # Sprint time etc.
                 # Improvement if Time DECREASES. 
                 # Let's keep raw delta. If -5%, that's speed up.
                 valid_df[delta_col] = (merged[c_post] - pre_vals) / pre_vals * 100
            else:
                 valid_df[delta_col] = (merged[c_post] - pre_vals) / pre_vals * 100
                 
    return valid_df

def plot_delta_chart(delta_df, metric_category):
    """
    Charts the top movers for a specific metric category (e.g., 'Power_Delta')
    """
    col = f"{metric_category}_Delta"
    if col not in delta_df.columns: return None
    
    # Sort by absolute change to show most significant changes
    delta_df['Abs_Delta'] = delta_df[col].abs()
    top_movers = delta_df.sort_values('Abs_Delta', ascending=False).head(10)
    
    fig = px.bar(top_movers, x=col, y='Name', orientation='h',
                 color=col, color_continuous_scale='RdBu',
                 title=f"Top Movers: {metric_category} Change (%)",
                 text_auto='.1f')
    
    # Interpretation Guide
    fig.add_vline(x=0, line_width=1, line_color='black')
    return fig

# ==============================================================================
# 8. Hamstring Functional Ratio (Eccentric / Isometric)
# ==============================================================================
def plot_hamstring_functional_ratio(df, iso_col, ecc_col, title="Hamstring Functional Ratio (Ecc vs Iso)"):
    """
    Plots a Scatter Chart for Hamstring Functional Ratio.
    Ratio = Eccentric Force / Isometric Force.
    Target Range: 1.1 ~ 1.15.
    """
    if df.empty or iso_col not in df.columns or ecc_col not in df.columns:
        return None

    plot_df = df.copy()
    plot_df['ISO_Avg'] = plot_df[iso_col]
    plot_df['ECC_Avg'] = plot_df[ecc_col]
    
    # Calculate Ratio for Color Coding
    # Avoid division by zero
    plot_df['Ratio'] = plot_df['ECC_Avg'] / plot_df['ISO_Avg'].replace(0, 0.001)
    
    def get_status(r):
        if r < 1.1: return 'Eccentric Deficit (< 1.1)'
        elif r > 1.15: return 'Isometric Deficit (> 1.15)'
        else: return 'Optimal Zone (1.1-1.15)'
        
    plot_df['Status'] = plot_df['Ratio'].apply(get_status)
    
    # Define Colors
    color_map = {
        'Eccentric Deficit (< 1.1)': '#EF553B', # Red
        'Optimal Zone (1.1-1.15)': '#00CC96',   # Green
        'Isometric Deficit (> 1.15)': '#FFA15A' # Orange
    }
    
    fig = px.scatter(
        plot_df, 
        x='ISO_Avg', 
        y='ECC_Avg', 
        color='Status',
        color_discrete_map=color_map,
        hover_data=['Name', 'Ratio'],
        text='Name',
        title=title
    )
    
    fig.update_traces(textposition='top center', marker=dict(size=10, line=dict(width=1, color='DarkSlateGrey')))
    
    # Dynamic Range for Reference Lines
    if plot_df['ISO_Avg'].max() > 0:
        max_iso = plot_df['ISO_Avg'].max() * 1.2
        max_ecc = plot_df['ECC_Avg'].max() * 1.2
    else:
        max_iso = 1000
        max_ecc = 1200
        
    # Reference Lines (Diagonal)
    # y = 1.1x (Lower Bound of Optimal)
    fig.add_shape(type="line", x0=0, y0=0, x1=max_iso, y1=max_iso * 1.1,
                  line=dict(color="Green", width=1, dash="dash"))
    fig.add_annotation(x=max_iso, y=max_iso*1.1, text="Ratio 1.1", showarrow=False, yshift=10)

    # y = 1.15x (Upper Bound of Optimal)
    fig.add_shape(type="line", x0=0, y0=0, x1=max_iso, y1=max_iso * 1.15,
                  line=dict(color="Green", width=1, dash="dash"))
    fig.add_annotation(x=max_iso, y=max_iso*1.15, text="Ratio 1.15", showarrow=False, yshift=10)
    
    fig.update_layout(
        xaxis_title="Isometric Peak Force (N)",
        yaxis_title="Eccentric Peak Force (N)",
        yaxis=dict(range=[0, max_ecc]),
        xaxis=dict(range=[0, max_iso]),
        legend_title="Start Training Focus",
        height=600
    )
    
    return fig
