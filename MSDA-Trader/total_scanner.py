import time
import yfinance as yf
import msda  # 실시간 수급 추적 모듈 import

# 우리가 만든 LAYER 1, LAYER 3, LAYER 4 모듈 합체
import macro_selector as layer1
import technical_calculator as layer3
import financial_verifier as layer4

def run_total_scanner(ticker_list):
    print("\n" + "=" * 65)
    print("🚀 [MSDA-Trader] 장중 주도주 핵심 종목 종합 스캔 가동")
    print("=" * 65)
    
    results = []
    
    for ticker in ticker_list:
        print(f"\n🔍 종목 코드 [{ticker}] 분석 중...", end="", flush=True)
        
        try:
            # 1. 데이터 수집 (최근 5일치 15분봉)
            raw_df = yf.download(ticker, period="5d", interval="15m", progress=False)
            if raw_df.empty:
                print(" ➔ 데이터 누락 패스")
                continue
                
            # 2. LAYER 3: 기술적 타점 계산
            processed_df = layer3.calculate_indicators(raw_df)
            chart_signal, chart_guide = layer3.check_entry_signal(processed_df)
            
            # 가장 최신 데이터의 상세 값 추출을 위해 평탄화 후 바인딩
            latest_row = processed_df.iloc[-1]
            close_val = latest_row['Close'].item() if hasattr(latest_row['Close'], 'item') else latest_row['Close']
            rsi_val = processed_df['RSI'].iloc[-1]
            
            # 3. LAYER 4: 기업 재무 체력 검증
            t_obj = yf.Ticker(ticker)
            info = t_obj.info
            profit_margins = info.get('profitMargins', 0)
            debt_to_equity = info.get('debtToEquity', 0)
            
            # 재무 심사 컷오프
            if profit_margins is None or profit_margins < 0 or (debt_to_equity and debt_to_equity > 250.0):
                fund_status = "FAIL"
            else:
                fund_status = "PASS"
                
            # 결과 저장
            results.append({
                "ticker": ticker,
                "name": info.get('shortName', ticker),
                "price": f"{close_val:,.0f}원",
                "rsi": f"{rsi_val:.1f}",
                "chart": chart_signal,
                "fund": fund_status
            })
            print(" 완료!")
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f" ➔ ❌ 에러 발생: {e}")
            
    # 4. 📊 최종 종합 전광판 출력
    print("\n" + "=" * 65)
    print("📋 [MSDA-Trader] 주도 종목 실시간 종합 판정 전광판")
    print("=" * 65)
    print(f"{'종목명':<12} | {'현재가':<10} | {'RSI':<5} | {'차트타점':<5} | {'재무안전'}")
    print("-" * 65)
    
    for r in results:
        c_icon = "🔥 BUY" if r['chart'] == "BUY" else "👀 HOLD" if r['chart'] == "HOLD" else "❌ PASS" if r['chart'] == "PASS" else "💤 WAIT"
        f_icon = "✅ 안전" if r['fund'] == "PASS" else "🚨 부실"
        
        print(f"{r['name']:<12} | {r['price']:<10} | {r['rsi']:<5} | {r['chart']:<5} | {f_icon}")
        
    print("=" * 65)
    print("💡 가이드: 차트타점이 'BUY'이면서 재무안전이 '안전'인 종목만 최종 타겟입니다.\n")

# ⚡ [통합 자동화 메인 흐름 제어]
if __name__ == "__main__":
    print("=====================================================")
    print("🤖 MSDA-Trader 통합 자동매매 파이프라인 가동 엔진 🤖")
    print("=====================================================")
    
    # 1단계: LAYER 1 매크로 시장 날씨 심사 (VKOSPI, 시장 등락폭)
    weather, message = layer1.get_market_weather()
    
    if weather == "STORM":
        print(f"\n📢 [시스템 비상 브레이크 작동] {message}")
        print("❌ 정치적 불확실성 및 외인 대량 매도로 판이 깨졌습니다. 안전을 위해 전 종목 매수를 동결하고 관망합니다.")
    else:
        # 2단계: 시장 날씨가 SUNNY 또는 CLOUDY로 통과했을 때만 실시간 수급 종목 추출
        print(f"\n🌤️ 시장 날씨 패스 완료 ({weather}) ➔ 실시간 수급 주도주 수집 중...")
        target_stocks = msda.get_live_top_tickers() 
        
        if target_stocks:
            # 3단계: 수집된 실시간 종목으로 분봉 타점 + 재무 스캔 가동
            run_total_scanner(target_stocks)
        else:
            print("❌ LAYER 2 실시간 종목 수집 실패로 스캔을 중단합니다.")