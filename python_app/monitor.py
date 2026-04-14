import mysql.connector
import json
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import font_manager, rc
import time

# 1. 설정 및 폰트 로드
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "config.json")

font_path = "C:/Windows/Fonts/malgun.ttf"
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)

try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
except Exception as e:
    print(f"X 설정 파일 읽기 실패: {e}")
    exit()

# 2. 데이터베이스 함수들
def get_db_connection():
    return mysql.connector.connect(
        host=config['database']['host'],
        user=config['database']['user'],
        password=config['database']['pw'],
        database=config['database']['db'],
        connect_timeout=3
    )

def get_current_price_from_db():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT price FROM market_data ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        return float(row[0]) if row else 0
    except: return 0
    finally:
        if conn and conn.is_connected(): conn.close()

def get_trade_logs():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT DATE_FORMAT(traded_at, '%H:%i:%s'), side, price 
            FROM trade_logs ORDER BY id DESC LIMIT 30
        """
        cursor.execute(query)
        return cursor.fetchall()
    except: return []
    finally:
        if conn and conn.is_connected(): conn.close()

# 3. 초기화 (시스템 시작 시 딱 한 번)
BASE_PRINCIPAL = 100000000.0 # 기본 1억 JPY
sim_cash = BASE_PRINCIPAL
sim_btc_amount = 0.0
is_holding = False
last_processed_trade_id = None

times, yields, assets = [], [], []
fig, ax = plt.subplots(figsize=(10, 6))

# 4. 애니메이션 업데이트 함수
def update(frame):
    global last_processed_trade_id, sim_cash, sim_btc_amount, is_holding
    
    current_price = get_current_price_from_db()
    trades = get_trade_logs()

    if current_price > 0:
        current_time = time.strftime('%H:%M:%S')
        
        # 매매 로직 (최신 로그 감시)
        if trades:
            latest_t, latest_side, latest_p = trades[0]
            trade_id = f"{latest_t}_{latest_side}"
            
            if last_processed_trade_id != trade_id:
                if latest_side == 'BUY' and not is_holding:
                    fee = sim_cash * 0.0005
                    sim_btc_amount = (sim_cash - fee) / current_price
                    sim_cash = 0
                    is_holding = True
                    print(f"🚀 [BUY] {current_price:,.0f}원에 매수")
                elif latest_side == 'SELL' and is_holding:
                    sell_val = sim_btc_amount * current_price
                    fee = sell_val * 0.0005
                    sim_cash = sell_val - fee
                    sim_btc_amount = 0
                    is_holding = False
                    print(f"💰 [SELL] {current_price:,.0f}원에 매도")
                last_processed_trade_id = trade_id

        # 실시간 가치 계산
        current_val = (sim_btc_amount * current_price) if is_holding else sim_cash
        curr_yield = ((current_val - BASE_PRINCIPAL) / BASE_PRINCIPAL) * 100

        # 데이터 업데이트
        times.append(current_time)
        yields.append(curr_yield)
        assets.append(current_val)
        if len(times) > 50:
            times.pop(0); yields.pop(0); assets.pop(0)

        # 차트 그리기
        ax.clear()
        ax.plot(times, yields, marker='o', color='#2ecc71', linewidth=2, label='수익률')
        ax.axhline(0, color='black', linewidth=1, alpha=0.2)
        
        # 타점 표시
        for t_time, t_side, t_price in trades:
            if t_time in times:
                idx = times.index(t_time)
                color = 'red' if t_side == 'BUY' else 'blue'
                ax.scatter(times[idx], yields[idx], color=color, marker='^' if t_side=='BUY' else 'v', s=150, zorder=5)
        
        plt.xticks(rotation=45, ha='right')
        ax.set_ylabel('수익률 (%)')
        status = "BTC 보유" if is_holding else "현금 보유"
        plt.title(f"시뮬레이션 [{status}] | 자산: {current_val:,.0f} JPY ({curr_yield:+.4f}%)")
        plt.tight_layout()

# 5. 실행
ani = FuncAnimation(fig, update, interval=5000, cache_frame_data=False)
plt.show()