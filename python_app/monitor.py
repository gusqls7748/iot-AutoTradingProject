import mysql.connector
import json # 1. json 라이브러리 추가 필요
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

# [중요] 현재 실행되는 monitor.py와 '같은 폴더'에 있는 config.json을 찾습니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "config.json")

# 1. 설정 파일 로드
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f"✅ 설정 로드 완료: {config_path}")
except Exception as e:
    print(f"❌ 설정 파일 읽기 실패: {e}")
    exit()

def get_total_asset():
    try:
        conn = mysql.connector.connect(
            host=config['database']['host'],
            user=config['database']['user'],
            password=config['database']['pw'],
            database=config['database']['db']
        )
        cursor = conn.cursor()

        # 현재가 가져오기
        cursor.execute("SELECT price FROM market_data ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if not row: return None
        current_price = row[0]

        # 잔고 가져오기
        cursor.execute("SELECT asset_type, balance FROM assets")
        balances = dict(cursor.fetchall())

        cash = balances.get('CASH', 0)
        btc = balances.get('BTC', 0)

        # 총자산 = 현금 + (보유 BTC * 현재가)
        total_value = cash + (btc * current_price)

        conn.close()
        return total_value
    except Exception as e:
        print(f"에러 발생: {e}")
        return None
    
# 데이터 저장용 리스트
times = []
assets = []

fig, ax = plt.subplots()

def update(frame):
    current_asset = get_total_asset()
    if current_asset is not None:
        times.append(time.strftime('%H:%M:%S'))
        assets.append(current_asset)

        # 최근 50개의 데이터만 유지
        if len(times) > 50:
            times.pop(0)
            assets.pop(0)

        ax.clear()
        ax.plot(times, assets, marker='o', color='g', linestyle='-')
        plt.xticks(rotation=45, ha='right')
        plt.title(f"Real-time Asset Monitoring: {current_asset:,.0f} KRW")
        ax.set_ylabel("Total Value (KRW)")
        plt.tight_layout()

# 3. 중요: FuncAnimation은 함수 밖(메인 흐름)에 있어야 합니다.
ani = FuncAnimation(fig, update, interval=5000, cache_frame_data=False)
plt.show()