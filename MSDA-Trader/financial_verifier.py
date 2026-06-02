import yfinance as yf

def verify_company_health(ticker_symbol):
    """
    기업의 재무제표(info)를 조회하여 좀비 기업, 부실 기업을 걸러내는 최종 방어벽입니다.
    """
    print(f"\n🛡️ [LAYER 4] '{ticker_symbol}' 기업 재무 체력 최종 심사 시작...")
    
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        # 1. 재무 데이터에서 핵심 지표 3가지 쏙 쏙 골라내기
        # 데이터가 없을 경우를 대비해 기본값(None 또는 0)을 세팅합니다.
        company_name = info.get('longName', ticker_symbol)
        
        # 영업이익률 또는 순이익 (적자 여부 확인용)
        profit_margins = info.get('profitMargins', 0)  # 소수점 형태 (예: 0.15 = 15%)
        
        # 부채비율 (Debt to Equity)
        debt_to_equity = info.get('debtToEquity', 0)   # 퍼센트 형태 (예: 80 = 80%)
        
        # ROE (자기자본이익률)
        roe = info.get('returnOnEquity', 0)            # 소수점 형태 (예: 0.12 = 12%)
        
        # 2. 화면에 심사 지표 깔끔하게 출력
        print(f"========================================")
        print(f"🏢 기업명: {company_name}")
        print(f"----------------------------------------")
        print(f"📊 1. 순이익률 (Profit Margin) : {profit_margins * 100:.2f}%")
        print(f"💵 2. 부채비율 (Debt/Equity)   : {debt_to_equity:.2f}%")
        print(f"📈 3. ROE (자기자본이익률)     : {roe * 100:.2f}%")
        print(f"========================================")
        
        # 🚨 고수들의 부실기업 필터링 알고리즘 (컷오프 기준선)
        # 조건 1: 이익률이 0보다 작으면 (적자 기업) ➔ 탈락
        if profit_margins < 0:
            return "FAIL", f"❌ 심사 탈락: 현재 적자 구조인 좀비 기업입니다. 매수 금지!"
            
        # 조건 2: 부채비율이 250%를 넘어가면 (위험 수준) ➔ 탈락
        if debt_to_equity > 250.0:
            return "FAIL", f"❌ 심사 탈락: 부채비율({debt_to_equity:.2f}%)이 너무 높아 부도 위험이 있습니다."
            
        # 조건 3: ROE가 너무 낮으면 (돈을 못 굴림, 마이너스거나 2% 미만) ➔ 탈락
        if roe < 0.02:
            return "FAIL", f"❌ 심사 탈락: ROE({roe * 100:.2f}%)가 너무 낮아 자본 효율성이 떨어집니다."
            
        # 모든 관문을 통과하면 완벽한 우량주!
        return "PASS", "✅ 최종 승인: 재무 체력이 탄탄한 안전 우량주입니다. 매수 가능!"
        
    except Exception as e:
        # 해외 라이브러리 특성상 한국 중소형주는 info 데이터가 비어있을 수 있어서 예외처리가 필수입니다.
        return "ERROR", f"⚠️ 재무 데이터 조회 실패 (데이터 누락 가능성): {e}"

# 🧪 대장주 'SK하이닉스'와 부실 테마주 가상 시뮬레이션 테스트
if __name__ == "__main__":
    # 1. 안전한 대장주 테스트
    ticker_ok = "000660.KS"  
    status, message = verify_company_health(ticker_ok)
    print(f"📢 [심사 결과] : {status}")
    print(f"📢 [가 이 드] : {message}\n")