
import sqlite3
import pandas as pd
import datetime
import os

DB_FILE = "center_database.db"

def init_db():
    """DB 테이블이 없으면 생성"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 1. Players Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            player_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            dob TEXT,
            sport TEXT,
            position TEXT,
            team TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Daily Measurements
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT,
            date TEXT,
            
            -- Body Profile
            height REAL,
            weight REAL,
            muscle_mass REAL,
            fat_mass REAL,
            
            -- Power Metrics (1RM)
            squat_1rm REAL,
            bench_1rm REAL,
            deadlift_1rm REAL,
            
            -- Power Metrics (Machine/Etc)
            pull_up REAL,
            xim_pulldown REAL,
            xim_shoulder REAL,
            xim_deadlift REAL,
            epoc REAL,
            
            -- Sprints (Optional)
            sprint_10m REAL,
            sprint_20m REAL,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players (player_id)
        )
    ''')
    
    # 3. Rehabilitation Records
    c.execute('''
        CREATE TABLE IF NOT EXISTS rehab_records (
            rehab_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT,
            date TEXT,
            
            diagnosis TEXT,
            injury_date TEXT,
            return_date TEXT,
            stage TEXT,
            program_count INTEGER,
            injury_mechanism TEXT,
            problem_list_1 TEXT,
            problem_list_2 TEXT,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players (player_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_FILE)

# --- Player Functions ---
def add_player(name, dob, sport, position, team, phone):
    conn = get_connection()
    c = conn.cursor()
    
    # Simple ID Generation: NAME_DOB (e.g., SON_19920708)
    dob_clean = dob.replace("-", "").replace(".", "")
    player_id = f"{name}_{dob_clean}"
    
    try:
        c.execute('''
            INSERT INTO players (player_id, name, dob, sport, position, team, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (player_id, name, dob, sport, position, team, phone))
        conn.commit()
        return True, f"선수 등록 성공: {name} ({player_id})"
    except sqlite3.IntegrityError:
        return False, "이미 등록된 선수(ID 중복)입니다."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def delete_player(player_id):
    """
    Deletes a player and their associated records from the database.
    Argument player_id is TEXT.
    """
    conn = get_connection()
    c = conn.cursor()
    try:
        # Delete related records
        c.execute("DELETE FROM daily_records WHERE player_id = ?", (player_id,))
        c.execute("DELETE FROM rehab_records WHERE player_id = ?", (player_id,))
        # Delete player
        c.execute("DELETE FROM players WHERE player_id = ?", (player_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting player: {e}")
        return False
    finally:
        conn.close()

def get_all_players():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM players ORDER BY name", conn)
    conn.close()
    return df

# --- Measurement Functions ---
def add_daily_record(data_dict):
    conn = get_connection()
    keys = ', '.join(data_dict.keys())
    placeholders = ', '.join(['?'] * len(data_dict))
    values = tuple(data_dict.values())
    
    try:
        conn.execute(f"INSERT INTO daily_records ({keys}) VALUES ({placeholders})", values)
        conn.commit()
        return True, "기록 저장 성공"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_player_records(player_id):
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM daily_records WHERE player_id = '{player_id}' ORDER BY date DESC", conn)
    conn.close()
    return df

# --- Rehab Functions ---
def add_rehab_record(data_dict):
    conn = get_connection()
    keys = ', '.join(data_dict.keys())
    placeholders = ', '.join(['?'] * len(data_dict))
    values = tuple(data_dict.values())
    
    try:
        conn.execute(f"INSERT INTO rehab_records ({keys}) VALUES ({placeholders})", values)
        conn.commit()
        return True, "재활 기록 저장 성공"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_player_rehab(player_id):
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM rehab_records WHERE player_id = '{player_id}' ORDER BY date DESC", conn)
    conn.close()
    return df

if not os.path.exists(DB_FILE):
    init_db()
