# K League Dashboard Maintenance Manual 📘

## Project Overview
This project is a Streamlit data dashboard for analyzing K League player performance, specifically physical metrics and scouting data.

**Key Features:**
- **Protocol Analysis**: Team comparison and metric trends.
- **Player Profiling**: Radar charts (10-point scale), growth history, and detailed metrics.
- **Tech Stack**: Python, Streamlit, Plotly, Google BigQuery (connected to Google Sheets).

## File Structure
- `app.py`: Main entry point. Handles layout framework (Sidebar).
- `templates/template_association.py`: **Core Logic**. Contains all code for charts (Radar, Bar, Line) and tabs (Player, Protocol).
- `utils/data_loader.py`: Handles connection to BigQuery and data preprocessing (column types, dates).
- `safe_schema.sql`: **Critical**. Defines the manual schema for the BigQuery External Table. Use this to update DB structure if columns change in Google Sheets.
- `requirements.txt`: List of required Python libraries.

## How to Modify Later
When you come back to this project, tell the AI assistant:
> "This is the K League Dashboard project. Please read `KLEAGUE_MANUAL.md` to understand the context."

### Common Tasks
1.  **Adding New Columns from Google Sheets:**
    - If you add columns to the Google Sheet (e.g., new test results), they won't appear automatically.
    - You must update the BigQuery Schema.
    - **Action**: Edit `safe_schema.sql` to include the new column at the **correct position** matching the Sheet.
    - Run the SQL query in BigQuery Console.

2.  **Updating Charts / Visuals:**
    - Go to `templates/template_association.py`.
    - `render_metric_card`: Controls the small charts in Protocol tab.
    - `Player Tab` section (Line ~650+): Controls the Player Search and Radar Chart.

3.  **Deployment:**
    - Push changes to GitHub: `git push`
    - Streamlit Cloud updates automatically.
    - URL: https://kleague-jqj4kmdjvfmhdhtmh6cok9.streamlit.app/

## Troubleshooting
- **Data is NULL?**: Check `safe_schema.sql` vs Google Sheet column order. (Remember the "AQ ~ BL" column range issue we solved).
- **Service Account Error?**: Check Streamlit Secrets in the dashboard settings.

---
*Last Updated: 2025-12-29 (Fixed Strength_Sum_Point mapping & Filters)*
