import os
from datetime import datetime
import re  # 🌟 봇 차단을 무력화하고 텍스트만 낚아챌 정규식 라이브러리
import pandas as pd
import requests
from pykrx import stock

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://finance.naver.com/sise/",
}


def get_naver_regex_loader(market_code, investor_name):
    """
    HTML 태그, 파서, API 유무와 전혀 상관없이
    네이버 금융 소스 코드 텍스트에서 종목명과 순매수 금액 패턴을 정규식으로 직접 도려냅니다.
    """
    sosok = "0" if market_code == "KOSPI" else "1"
    tp = "1" if investor_name == "외국인" else "2"

    # 가장 안정적인 네이버 금융 정식 실시간 수급 페이지 URL
    url = f"https://finance.naver.com/sise/sise_deal_rank.naver?sosok={sosok}&investor_tp={tp}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        response.encoding = "euc-kr"  # 국문 깨짐 절대 방지

        if response.status_code != 200:
            return None

        html_text = response.text

        # 🌟 정규식 치트키: 네이버 소스 코드 내의 종목 링크 정보와 금액 텍스트 패턴 매칭
        # 예: <a href="/item/main.naver?code=005930" class="tltle">삼성전자</a> ... <td class="number">1,234</td>
        pattern = r'code=([0-9]{6})".*?>(.*?)</a>.*?<td.*?class="number".*?>([0-9\-\+,]+)</td>'
        matches = re.findall(pattern, html_text, re.DOTALL)

        if not matches:
            return None

        data_list = []
        rank = 1

        for match in matches:
            code = match[0]
            name = match[1].strip()
            # 네이버 금융의 '순매수대금' 위치는 종목 뒤에 나오는 숫자 패턴 중 하나입니다.
            # 정규식 노이즈 값(현재가 등)을 필터링하기 위한 장치
            if name in [
                "현재가",
                "전일대비",
                "등락률",
                "거래량",
                "거래대금",
                "매도잔량",
                "매수잔량",
            ]:
                continue

            amount_str = match[2].replace(",", "").replace("+", "")
            try:
                # 백만 단위 숫자를 억 원 단위로 환산
                amount_in_100m = round(float(amount_str) / 100, 2)
                data_list.append(
                    {
                        "순위": rank,
                        "종목코드": code,
                        "종목명": name,
                        "순매수대금(억원)": amount_in_100m,
                    }
                )
                rank += 1
                if rank > 10:  # 딱 TOP 10만 채우고 탈출
                    break
            except ValueError:
                continue

        if data_list:
            return pd.DataFrame(data_list)

    except Exception:
        pass
    return None


def get_market_net_purchases(date_str, market_code):
    """데이터 통합 게이트웨이 (기본 pykrx -> 최종병기 정규식 백업)"""
    result_dict = {}

    # 1. pykrx 작동 시도
    try:
        df = stock.get_market_net_purchases_of_equities_by_ticker(
            date_str, date_str, market_code
        )
        if (
            df is not None
            and not df.empty
            and "외국인합계" in df.columns
            and df["외국인합계"].sum() != 0
        ):
            investors = {"외국인": "외국인합계", "기관": "기관합계", "개인": "개인"}
            for investor_name, column_name in investors.items():
                top10 = df.sort_values(
                    by=column_name, ascending=False
                ).head(10)
                tickers = top10.index.tolist()
                names = [stock.get_market_ticker_name(t) for t in tickers]
                amount_in_100m = (top10[column_name] / 100000000).round(2)

                result_dict[investor_name] = pd.DataFrame(
                    {
                        "순위": range(1, 11),
                        "종목코드": tickers,
                        "종목명": names,
                        "순매수대금(억원)": amount_in_100m.values,
                    }
                )
            print(f"✅ pykrx 엔진을 통해 {market_code} 수급 수집 완료.")
            return result_dict
    except Exception:
        pass

    # 2. pykrx 실패 시 텍스트 파싱 방식의 최종병기 가동
    print(
        f"⚠️ pykrx 제한 확인. 네이버 금융 정규식 문자열 탈취 엔진 가동 ({market_code})..."
    )
    for inv_name in ["외국인", "기관"]:
        backup_df = get_naver_regex_loader(market_code, inv_name)
        if backup_df is not None and not backup_df.empty:
            result_dict[inv_name] = backup_df

    return result_dict if result_dict else None


def main():
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H시%M분")

    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 수급 데이터 수집을 시작합니다...")

    kospi_data = get_market_net_purchases(date_str, "KOSPI")
    kosdaq_data = get_market_net_purchases(date_str, "KOSDAQ")

    # 완전 빈 값 복구용 최종 크리티컬 방어선
    if not kospi_data and not kosdaq_data:
        print("❌ [최종 오류] 외부 연동 데이터 레이아웃 불일치.")
        kospi_data = {
            "알림": pd.DataFrame(
                {"상태": ["실패"], "원인": ["네이버 장마감 데이터 동기화 시간"]}
            )
        }

    file_name = f"수급_{time_str}.xlsx"

    with pd.ExcelWriter(file_name, engine="openpyxl") as writer:
        if kospi_data:
            start_row = 0
            for investor, df in kospi_data.items():
                pd.DataFrame([[]]).to_excel(
                    writer, sheet_name="KOSPI", startrow=start_row, index=False
                )
                writer.sheets["KOSPI"].cell(
                    row=start_row + 1, column=1, value=f"★ {investor} 순매수 상위 10"
                )
                df.to_excel(
                    writer,
                    sheet_name="KOSPI",
                    startrow=start_row + 1,
                    index=False,
                )
                start_row += 13

        if kosdaq_data:
            start_row = 0
            for investor, df in kosdaq_data.items():
                pd.DataFrame([[]]).to_excel(
                    writer, sheet_name="KOSDAQ", startrow=start_row, index=False
                )
                writer.sheets["KOSDAQ"].cell(
                    row=start_row + 1, column=1, value=f"★ {investor} 순매수 상위 10"
                )
                df.to_excel(
                    writer,
                    sheet_name="KOSDAQ",
                    startrow=start_row + 1,
                    index=False,
                )
                start_row += 13
        else:
            pd.DataFrame([["데이터 없음"]]).to_excel(
                writer, sheet_name="KOSDAQ", index=False
            )

    print(f"✨ MSDA-Trader 수급 스냅샷 저장 완료: {file_name}")


if __name__ == "__main__":
    main()