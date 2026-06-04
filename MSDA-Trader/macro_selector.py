import os
from datetime import datetime
import yfinance as yf
import math  # 👈 math.isnan을 쓰기 위해 상단에 import 필수!

def get_theme_leader_board():
    print("[Macro Engine] 미 증시 주도 테마 및 핵심 주종목 추적 시작...")
    
    theme_map = {
        "📊 기술주/빅테크": {"Apple (애플)": "AAPL", "Microsoft (마이크로소프트)": "MSFT"},
        "🔥 반도체/AI": {"NVIDIA (엔비디아)": "NVDA", "TSMC": "TSM"},
        "🧬 제약/바이오": {"Eli Lilly (일라이릴리)": "LLY", "Novo Nordisk (노보노디스크)": "NVO"},
        "⚡ 전력/인프라/우주": {"GE Vernova (GE버니어)": "GEV", "NextEra Energy (넥스트에라)": "NEE"},
        "🚗 이차전지/자율주행": {"Tesla (테슬라)": "TSLA", "Albemarle (앨버말 - 리튬1등)": "ALB"},
        "🚀 방산/우주인프라": {"Lockheed Martin (록히드마틴)": "LMT", "Raytheon (레이티온)": "RTX"}
    }
    
    all_tickers = []
    for stocks in theme_map.values():
        all_tickers.extend(stocks.values())
        
    try:
        data = yf.download(all_tickers, period="5d", progress=False)
        close_data = data['Close']
        
        print("\n" + "=" * 55)
        print(f"📡 [MSDA-Trader] 미 증시 주도 테마 현황판 ({datetime.now().strftime('%m-%d %H:%M')})")
        print("=" * 55)
        
        for theme_name, stocks in theme_map.items():
            print(f"\n[{theme_name}]")
            print("-" * 55)
            
            for stock_name, ticker in stocks.items():
                if ticker in close_data.columns:
                    current_close = close_data[ticker].iloc[-1]
                    prev_close = close_data[ticker].iloc[-2]
                    chg_percent = ((current_close - prev_close) / prev_close) * 100
                    
                    if chg_percent > 0:
                        direction = f"🔺 +{chg_percent:.2f}%"
                    elif chg_percent < 0:
                        direction = f"🔻 {chg_percent:.2f}%"
                    else:
                        direction = " ➖  0.00%"
                        
                    print(f" 🌟 {stock_name:<22} ({ticker:<4}) ➔ {direction}")
                    
        print("=" * 55)
        
    except Exception as e:
        print(f"❌ 주종목 테마 데이터 연동 실패: {e}")

def get_market_weather():
    """
    미국 증시 + 국장 수급 변동성 지수를 종합하여 오늘 안전하게 매매할 수 있는 '시장 날씨'를 반환합니다.
    """
    print("\n🏛️ [LAYER 1] 글로벌 및 국장 매크로 환경 실시간 점검...")
    
    try:
        # 야후 파이낸스에서 한국 코스피 지수(^KS11)와 미국 VIX(^VIX) 실시간 수집
        macro_data = yf.download(["^KS11", "^VIX"], period="2d", progress=False)

        # -----------------------------------------------------------------
        # [1] VIX 수치 파싱 및 nan 방어 코드 적용 구간
        # -----------------------------------------------------------------
        if '^VIX' in macro_data['Close'].columns:
            raw_vix = macro_data['Close']['^VIX'].iloc[-1]
            # yfinance 특성상 데이터가 비어있으면 nan이 들어올 수 있음
            if raw_vix is None or math.isnan(raw_vix):
                vkospi = 18.5  # nan일 경우 안전한 기본값으로 세팅
            else:
                vkospi = float(raw_vix)
        else:
            vkospi = 18.5
            
        # -----------------------------------------------------------------
        # [2] 코스피 지수 파싱 및 nan 방어 코드 적용 구간
        # -----------------------------------------------------------------
        if '^KS11' in macro_data['Close'].columns:
            kospi_today = macro_data['Close']['^KS11'].iloc[-1]
            kospi_prev = macro_data['Close']['^KS11'].iloc[-2]
            
            # 둘 중 하나라도 nan이거나 분모가 0이 되는 상황 방어
            if (kospi_today is None or math.isnan(kospi_today) or 
                kospi_prev is None or math.isnan(kospi_prev) or kospi_prev == 0):
                kospi_chg = 0.0
                kospi_print_str = "조회 실패(확인 필요)"  # 터미널 출력용 문자열
            else:
                kospi_chg = ((kospi_today - kospi_prev) / kospi_prev) * 100
                kospi_print_str = f"{kospi_chg:+.2f}%"
        else:
            kospi_chg = 0.0
            kospi_print_str = "0.00%"

        # -----------------------------------------------------------------
        # [3] 미 증시 빅테크 엔비디아 파싱 및 nan 방어 코드 적용 구간
        # -----------------------------------------------------------------
        us_data = yf.download(["AAPL", "NVDA"], period="2d", progress=False)
        nvda_today = us_data['Close']['NVDA'].iloc[-1]
        nvda_prev = us_data['Close']['NVDA'].iloc[-2]
        
        if (nvda_today is None or math.isnan(nvda_today) or 
            nvda_prev is None or math.isnan(nvda_prev) or nvda_prev == 0):
            nvda_chg = 0.0
            nvda_print_str = "조회 실패(미장 휴장 등)"
        else:
            nvda_chg = ((nvda_today - nvda_prev) / nvda_prev) * 100
            nvda_print_str = f"{nvda_chg:+.2f}%"
            
        us_market_good = True if nvda_chg > -1.0 else False

        # 변수 값이 nan이 아님이 보장되었으므로 깔끔하게 포맷팅하여 출력
        print(f" - [국장 변동성] VKOSPI 공포 지수 : {vkospi:.2f}")
        print(f" - [국장 지수방향] KOSPI 당일 등락  : {kospi_print_str}")
        print(f" - [미장 반도체] 엔비디아 단기 동향  : {nvda_print_str}")
        print("-" * 55)

        # 🚨 [매크로 폭풍우 조건 필터링]
        if vkospi > 22.0 or kospi_chg < -1.5:
            return "STORM", "⚠️ 매크로 폭풍우 발생: 국장 내 변동성 폭등 및 외인 이탈 감지. 자금 보호를 위해 매수 전면 동결."
            
        if us_market_good and kospi_chg >= -0.2:
            return "SUNNY", "☀️ 맑음: 글로벌 매크로 및 국장 수급 안정세. 매매 진행 가능."
            
        return "CLOUDY", "☁️ 흐림: 시장이 다소 불안정합니다. 철저히 눌림목 보수적 타점만 노리세요."

    except Exception as e:
        return "CLOUDY", f"⚠️ 매크로 일부 데이터 누락으로 흐림 판정: {e}"
    
    # ⚠️ 이 블록이 맨 밑에 반드시 있어야 코드가 실행됩니다!
    
    # ⚠️ 이 블록이 맨 밑에 반드시 있어야 코드가 실행됩니다!
if __name__ == "__main__":
    get_theme_leader_board()
    weather, msg = get_market_weather()
    print(f"결과: {weather} ➔ {msg}")

