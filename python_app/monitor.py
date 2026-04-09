import mysql.connector
import json # 1. json 라이브러리 추가 필요
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime
import time

# [중요] 현재 실행되는 monitor.py와 '같은 폴더'에 있는 config.json을 찾습니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "config.json")

# 로그 저장 경로 설정
LOG_DIR = os.path.join(current_dir, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 중복 저장 방지를 위한 마지막 매매 ID 저장용 변수 (함수 밖 전역 변수)
last_processed_trade_id = None

# 1. 설정 파일 로드
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f"O 설정 로드 완료: {config_path}")
except Exception as e:
    print(f"X 설정 파일 읽기 실패: {e}")
    exit()

def get_total_asset():
    max_retries = 3 # 최대 3번 재시도
    retry_delay = 2 # 실패 시 2초 대기

    for attempt in range(max_retries):
        conn = None # 초기화
        try:
            # 데이터베이스 연결 시도 (Timeout 설정 추가 권장)
            conn = mysql.connector.connect(
                host=config['database']['host'],
                user=config['database']['user'],
                password=config['database']['pw'],
                database=config['database']['db'],
                connect_timeout=3 # 3초 이내 응답 없으면 타임 아웃
            )
            cursor = conn.cursor()

            # 현재가 가져오기
            cursor.execute("SELECT price FROM market_data ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            # if not row: return None
            current_price = row[0] if row else 0
            print(f"DEBUG > 현재가: {current_price}") #터미널 확인용

            # 잔고 가져오기
            cursor.execute("SELECT asset_type, balance FROM assets")
            balances = {row[0].upper(): row[1] for row in cursor.fetchall()} #대소문자 방어
            print(f"DEBUG > 가져온 잔고: {balances}") # 터미널 확인용

            cash = balances.get('CASH', 0)
            btc = balances.get('BTC', 0)

            # 총자산 = 현금 + (보유 BTC * 현재가)
            total_value = float(cash) + (float(btc) * float(current_price))

            # conn.close()
            return total_value
        except Exception as e: 
            print(f"DEBUG > 데이터 조회 오류: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                conn.close()

def get_trade_logs():
    conn = None
    try:
        conn = mysql.connector.connect(
            host=config['database']['host'],
            user=config['database']['user'],
            password=config['database']['pw'],
            database=config['database']['db'],
            connect_timeout=3
        )
        cursor = conn.cursor()

        # 최근 30개의 매매 기록 가져오기
        # [수정 포인트] 컬럼명을 DB 구조에 맞게 변경: side, traded_at
        # 테이블 이름도 보여주신 데이터가 들어있는 실제 테이블명으로 바꿔주세요.
        # 여기서는 일단 보여주신 구조대로 쿼리를 짭니다.
        query = """
            SELECT 
                DATE_FORMAT(traded_at, '%Y-%m-%d %H:%i:%s') as t_time, 
                side, 
                price 
            FROM trade_logs 
            ORDER BY id DESC 
            LIMIT 30
        """
        cursor.execute(query)
        logs = cursor.fetchall()
        return logs 
    except Exception as e:
        print(f"DEBUG > 로그 호출 중 에러 발생: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close() # 연결을 확실히 닫아줘야 DB 부하가 줄어듭니다.
    
# 초기 자산 (수익률 계산용 - config에 넣거나 첫 로드값 사용)
INITAL_ASSET = 1000000
# 데이터 저장용 리스트
times = []
assets = []
yields = [] # 수익률 저장

fig, ax = plt.subplots(figsize=(10,6))

def update(frame):
    global last_processed_trade_id
    current_asset = get_total_asset()
    
    # [중요] 매매 로그를 가져오는 시점을 자산 업데이트와 분리해서 확실히 체크
    trades = get_trade_logs()
    
    # 터미널에 매매 데이터가 오고 있는지 강제 출력 (이게 떠야 합니다!)
    if not trades:
        print("DEBUG > [알림] 현재 DB에 매매 기록(trade_logs)이 하나도 없습니다.")
    else:
        print(f"DEBUG > [확인] DB에서 {len(trades)}개의 로그를 가져왔습니다.")

    if current_asset is not None:
        current_time = time.strftime('%H:%M:%S')
        times.append(current_time)
        assets.append(current_asset)
        
        current_yield = ((current_asset - INITAL_ASSET) / INITAL_ASSET) * 100
        yields.append(current_yield)

        if len(times) > 50:
            times.pop(0)
            assets.pop(0)
            yields.pop(0)

        ax.clear()

        # --- 저장 로직 시작 ---
        if trades:
            # 0번이 가장 최신
            trade_time_str, trade_side, trade_price = trades[0] 
            current_trade_id = f"{trade_time_str}_{trade_side}_{trade_price}"

            # 비교를 수행합니다.
            if last_processed_trade_id != current_trade_id:
                print(f"🚀 [매매 감지] {current_trade_id} -> 저장을 시도합니다!")
                
                try:
                    # 파일명 생성
                    safe_time = trade_time_str.replace(":", "").replace("-", "").replace(" ", "_")
                    file_name = f"trade_{safe_time}_{trade_side}.png"
                    file_path = os.path.join(LOG_DIR, file_name)

                    # 1. 그래프 그리기 (저장용)
                    ax.plot(times, assets, marker='o', color='g', alpha=0.4)
                    
                    # 2. 파일 저장
                    plt.savefig(file_path)
                    print(f"✅ [성공] 스냅샷 저장 완료: {file_path}")

                    # 3. CSV 저장
                    log_data = {"timestamp": [trade_time_str], "type": [trade_side], "price": [trade_price], "total_asset": [current_asset]}
                    df = pd.DataFrame(log_data)
                    csv_path = os.path.join(LOG_DIR, "trade_history.csv")
                    if not os.path.exists(csv_path):
                        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                    else:
                        df.to_csv(csv_path, mode='a', header=False, index=False, encoding='utf-8-sig')
                    
                    print(f"✅ [성공] CSV 로그 기록 완료")
                    
                    # 저장 완료 후 ID 업데이트
                    last_processed_trade_id = current_trade_id
                
                except Exception as e:
                    print(f"❌ [에러] 저장 중 오류 발생: {e}")
        # --- 저장 로직 끝 ---

        # 메인 화면 그래프 다시 그리기
        ax.plot(times, assets, marker='o', color='g', linestyle='-', alpha=0.4)
        
        # [수정된 타점 마킹 로직]
        for t_time_str, t_type, t_price in trades:
            # t_time_str 예: '2026-04-09 15:45:30'
            # 1. DB 시간을 시:분:초 형식으로 변환
            try:
                trade_t = t_time_str.split(" ")[1] 
            except:
                continue

            # 2. 현재 화면에 표시되고 있는 데이터(times) 중 가장 가까운 인덱스 찾기
            # (시간이 정확히 일치하지 않아도 가장 근접한 위치에 찍기 위함)
            if times:
                # 완벽하게 일치하는 시각이 있으면 거기 찍고, 
                # 없으면 현재 표시 중인 데이터 중 가장 마지막(최신) 근처에 마킹 시도
                if trade_t in times:
                    idx = times.index(trade_t)
                    color = 'red' if t_type == 'BUY' else 'blue'
                    marker = '^' if t_type == 'BUY' else 'v'
                    ax.scatter(times[idx], assets[idx], color=color, marker=marker, s=200, zorder=10, edgecolors='black')
                else:
                    # [팁] 실시간 데이터 특성상 정확한 매칭이 어려우면, 
                    # 로그의 시간이 times의 범위 안에 있을 때 가장 가까운 곳에 찍어주는 로직이 필요합니다.
                    # 일단은 '최신 매매' 하나라도 확실히 보여주기 위해 아래 로직 추가
                    if t_time_str == trades[0][0]: # 가장 최근 매매라면
                         ax.annotate(f"{t_type}", xy=(times[-1], assets[-1]), 
                                     xytext=(0, 20 if t_type=='BUY' else -20),
                                     textcoords='offset points', ha='center',
                                     arrowprops=dict(arrowstyle='->', color='red' if t_type=='BUY' else 'blue'))

# 3. 중요: FuncAnimation은 함수 밖(메인 흐름)에 있어야 합니다.
# 애니메이션 실행
ani = FuncAnimation(fig, update, interval=5000, cache_frame_data=False)
plt.show()