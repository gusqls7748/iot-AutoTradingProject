import pandas as pd
import numpy as np
import yfinance as yf  # 데이터 테스트용

def calculate_indicators(df):
    """
    주가 데이터프레임(df)을 받아 이동평균선과 RSI를 계산합니다.
    """
    # [보안관 코드] yfinance 멀티인덱스 컬럼 구조를 단일 레이어로 평탄화
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # 1. 이동평균선(Moving Average) 계산
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()
    
    # 2. RSI (상대강도지수) 계산 공식 구현
    delta = df['Close'].diff()
    
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    
    ma_up = up.ewm(com=13, adjust=False).mean()
    ma_down = down.ewm(com=13, adjust=False).mean()
    
    rs = ma_up / ma_down
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df

def check_entry_signal(df):
    """
    계산된 지표를 바탕으로 고수들의 기계적 진입 타점을 판정합니다.
    """
    if len(df) < 60:
        return "WAIT", "데이터 부족으로 판정 불가"
        
    # 가장 최신(오늘 혹은 현재 분봉)의 데이터 추출
    latest_row = df.iloc[-1]
    
    # .item()을 붙여서 판다스 시리즈 객체가 아닌 순수한 '파이썬 단일 숫자'로 추출합니다. (에러 방지)
    close = float(latest_row['Close'].item()) if hasattr(latest_row['Close'], 'item') else float(latest_row['Close'])
    ma5 = float(latest_row['MA5'].item()) if hasattr(latest_row['MA5'], 'item') else float(latest_row['MA5'])
    ma20 = float(latest_row['MA20'].item()) if hasattr(latest_row['MA20'], 'item') else float(latest_row['MA20'])
    ma60 = float(latest_row['MA60'].item()) if hasattr(latest_row['MA60'], 'item') else float(latest_row['MA60'])
    rsi = float(latest_row['RSI'].item()) if hasattr(latest_row['RSI'], 'item') else float(latest_row['RSI'])
    
    # 🚨 고수의 진입 판정 알고리즘
    # 조건 1: 정배열인가?
    is_up_trend = ma5 > ma20 > ma60
    
    # 조건 2: 세일(눌림목) 구간인가?
    is_sale_price = rsi <= 40.0
    
    # 조건 3: 과열 구간인가?
    is_overheated = rsi >= 70.0
    
    print(f"\n🔍 [타점 분석 결과]")
    print(f"   - 현재가: {close:,.0f}원")
    print(f"   - 이평선 상태: 5일선({ma5:,.0f}) | 20일선({ma20:,.0f}) | 60일선({ma60:,.0f}) ➔ {'정배열' if is_up_trend else '역배열/혼조'}")
    print(f"   - RSI 지수: {rsi:.2f}")
    print("-" * 40)
    
    if is_overheated:
        return "PASS", "❌ 탐욕 구간(RSI 70이상)! 지금 사면 꼭대기에 물리니까 쳐다보지도 마세요."
        
    # ➔ 💡 [광기 장세용 튜닝] 완전 역배열(흘러내리는 중)만 아니거나, RSI가 35 이하면 공격적 진입
    is_not_falling_dead = ma5 > ma60  # 완전 찐 하락세는 아님
    if (is_up_trend and is_sale_price) or (is_not_falling_dead and rsi <= 35.0):
        return "BUY", "🔥 공격적 타점 포착! 단기 과매도 구간입니다. 분할 매수 진입!"
        
    if is_up_trend and not is_sale_price:
        return "HOLD", "👀 정배열 우상향 중이나, 아직 확실한 세일 자리(눌림목)가 아닙니다. 대기."
        
    return "WAIT", "💤 추세가 무너진 역배열 상태입니다. 돈이 안 되는 자리이므로 관망합니다."

# 🧪 오늘 아침 핫한 'SK하이닉스' 데이터로 엔진 검증하기
if __name__ == "__main__":
    print("[LAYER 3] 기술적 타점 계산기 테스트 가동...")
    
    try:
        ticker = "000660.KS"
        raw_df = yf.download(ticker, period="5d", interval="15m", progress=False)
        
        # 지표 계산
        processed_df = calculate_indicators(raw_df)
        
        # 진입 신호 확인
        signal, guide = check_entry_signal(processed_df)
        
        print(f"📢 [최종 결론] : {signal}")
        print(f"📢 [가 이 드] : {guide}\n")
        
    except Exception as e:
        print(f"❌ 테스트 중 에러 발생: {e}")