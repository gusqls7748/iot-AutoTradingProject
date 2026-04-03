# 업비트 API를 사용하여 비트코인(BTC)의 현재가를 가져오는 가장 기본적인 코드

#1. 라이브러리 설치  
# pip installpyupbit

import pyupbit
import time

def get_btc_price():
    # 업비트에서 'KRW-BTC' (원화 시장의 비트코인) 현재가를 가져옵니다.
    price = pyupbit.get_current_price("KRW-BTC")
    return price
if __name__ == "__main__":
    print("비트코인 시세 수집을 시작합니다...( 중단하려면 Ctrl+C)")
    try:
        while True:
            current_price = get_btc_price()
            if current_price:
                # {current_price:,}는 숫자에 3자리마다 쉽표를 찍어준다.
                print(f"[실시간 시세] BTC: {current_price:,} 원")
            else:
                print("데이터를 가져오지 못했습니다. 네트워크를 확인하세요.")

            time.sleep(1) # 1초마다 반복
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")


