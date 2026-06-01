import os
from datetime import datetime
import yfinance as yf

def get_theme_leader_board():
    print("[Macro Engine] 미 증시 주도 테마 및 핵심 주종목 추적 시작...")
    
    # 🇺🇸 국장에 다이렉트로 영향을 주는 미국 4대 테마 및 핵심 주종목 매핑
    theme_map = {
        "📊 기술주/빅테크": {
            "Apple (애플)": "AAPL",
            "Microsoft (마이크로소프트)": "MSFT"
        },
        "🔥 반도체/AI": {
            "NVIDIA (엔비디아)": "NVDA",
            "TSMC": "TSM"
        },
        "🧬 제약/바이오": {
            "Eli Lilly (일라이릴리)": "LLY",
            "Novo Nordisk (노보노디스크)": "NVO"
        },
        "⚡ 전력/인프라/우주": {
            "GE Vernova (GE버니어)": "GEV",
            "NextEra Energy (넥스트에라)": "NEE"
        },
        "🚗 이차전지/자율주행": {
        "Tesla (테슬라)": "TSLA",
        "Albemarle (앨버말 - 리튬1등)": "ALB"
        },
        "🚀 방산/우주인프라": {
            "Lockheed Martin (록히드마틴)": "LMT",
            "Raytheon (레이티온)": "RTX"
        }
        
    }
    
    # 모든 티커를 한 번에 긁어오기 위한 리스트 생성
    all_tickers = []
    for stocks in theme_map.values():
        all_tickers.extend(stocks.values())
        
    try:
        # yfinance로 한 번에 다운로드해서 속도 최적화
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
                    
                    # 등락률 계산
                    chg_percent = ((current_close - prev_close) / prev_close) * 100
                    
                    # 🔴 상승/🔵 하락 직관적인 기호 표시
                    if chg_percent > 0:
                        direction = f"🔺 +{chg_percent:.2f}%"
                    elif chg_percent < 0:
                        direction = f"🔻 {chg_percent:.2f}%"
                    else:
                        direction = " Medal  0.00%"
                        
                    print(f" 🌟 {stock_name:<22} ({ticker:<4}) ➔ {direction}")
                    
        print("=" * 55)
        
    except Exception as e:
        print(f"❌ 주종목 테마 데이터 연동 실패: {e}")

if __name__ == "__main__":
    get_theme_leader_board()