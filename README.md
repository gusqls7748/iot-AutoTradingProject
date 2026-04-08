## iot-AutoTradingProject
2026년 Iot개발 miniProject 1

### 알고리즘 기반 '주식/가상화폐 자동 매매 시뮬레이션

1. 시스템 구조 (Architecture)
  - Language: C++ (Main Engine), Python (Data Collector)
  - Database: MySQL 
  - Library: libmysql, WinSock2 (Network), Windows.h (System)
  -Pattern: OOP (Object-Oriented Programming) 기반 모듈화

2. 주요 기능 (Key Features)
실시간 데이터 연동: Python으로 수집된 업비트 시세를 MySQL을 통해 실시간으로 읽어옴.

- 이동평균선(MA5) 전략: 최근 5회차 가격 평균을 계산하여 현재가와 비교하는 추세 추종 매매.

- 자동 자산 관리: 매수/매도 시 assets 테이블의 원화(CASH)와 비트코인(BTC) 잔고를 실시간 업데이트.

- 매매 일지 자동 기록: 모든 거래 내역(가격, 시간, 종류)을 trade_logs 테이블에 자동 저장.

- 리스크 관리 로직:
  - 익절(Take-Profit): 설정 수익률(예: +0.01%) 도달 시 자동 매도.

  - 손절(Stop-Loss): 설정 수익률(예: -0.01%) 도달 시 자동 매도.

  - 중복 매수 방지: 코인 보유 중일 경우 추가 매수 금지 로직 포함.

3. 모듈화 현황 (Refactoring)
- DatabaseManager 클래스 구현:

  - 기존 main.cpp에 밀집되어 있던 SQL 쿼리와 DB 접속 로직을 분리.
  - DatabaseManager.h / .cpp 파일을 통해 DB 접근을 객체화하여 유지보수성 향상.
- Main Logic 간소화: main.cpp는 매매 전략과 루프 제어에만 집중하도록 설계.
2. 시스템 아키텍처 (전체 구조)
시스템은 크게 세 부분으로 나누어 설계하면 효율적입니다.

- 수집기 (Python): yfinance나 pyupbit 같은 라이브러리를 사용해 실시간 시세를 가져와 DB에 쌓거나 C++로 넘겨줍니다.

- 엔진 (C++): Python이 받은 데이터를 넘겨받아 이동평균선(MA), RSI 등 지표를 계산하고 "살지 팔지" 결정합니다.

- 저장소 (DB - MySQL/PostgreSQL): 자산 현황, 매수 기록, 일별 수익률을 정규화하여 관리합니다.

3. 단계별 구현 가이드

- 1단계: 데이터베이스(DB) 설계
가장 먼저 데이터가 들어갈 그릇을 만들어야 합니다. SQL 실력을 발휘할 시점입니다.

- Table 1: market_data (날짜, 종목코드, 현재가, 거래량)

   - Table 2: trade_logs (매매 시간, 종목, 수량, 가격, 수수료)

    - Table 3: assets (보유 현금, 총 자산 가치, 수익률)

- 2단계: C++ 연산 로직 (알고리즘)
C++에서는 속도가 중요한 기술적 지표 계산을 담당합니다.

    - 자료구조 활용: 시세 데이터를 담을 std::vector나 실시간 윈도우 계산을 위한 std::deque를 활용해 보세요.

    - 알고리즘: 이동평균선(Moving Average) 계산 로직을 작성합니다.

    - 예: 최근 5일 평균 가격이 20일 평균 가격을 돌파할 때(골든크로스) 매수 신호 발생.

- 3단계: Python과 C++ 연동 (핵심)
가장 난이도가 높으면서도 실력이 급상승하는 구간입니다.
    - 방법: C++ 코드를 .dll(Windows) 또는 .so(Linux) 파일로 빌드한 뒤, Python의 ctypes 라이브러리를 사용하여 호출합니다.

    - 흐름: Python에서 API로 가격을 가져옴 → C++ 함수 호출(가격 전달) → C++이 계산 후 "Buy/Sell/Hold" 결과 반환 → Python이 결과에 따라 DB 업데이트.


### 2026-04-03 1일차

- 1단계: 파이썬 DB 연결 라이브러리 설치 (가장 먼저!)

```bash
pip install pymysql python-dotenv
```

## 2026-04-06 2일차 

### 시스템 인프라 구축 및 이종 언어 연동 성공

- 오늘 데이터의 흐름(Data Pipeline)을 완성하는 데 집중했습니다. 파이썬이 데이터를 공급하고, C++이 이를 분석하는 구조를 실제 작동 확인했습니다.

#### 1. 데이터베이스(MySQL) 상세 설정
- **Database**: `AutoTrading` 생성 (Charset: `utf8mb4`)
- **Table**: `market_data` 테이블 구축 완료 
    - 실시간 시세 저장을 위한 ID, Ticker, Price, Timestamp 구조 설계

#### 2. python 시세 수집기 (collector) 구현
- `pyupbit` 라이브러리를 활용한 비트코인(KRW-BTC) 실시간 시세 추출.
- `.env` 파일을 통한 DB 보안 설정 및 `pymysql`을 이용한 데이터 저장 로직 구현.
- **성과** 5초 주기 업비트 시세를 MySQL DB에 자동 적재 성공.

#### 3. C++ 매매 판단 엔진 (Trading Engine) 구축
- **환경 설정**: Visual Studio 2026 (x64) 환경에서 `libmysql` 라이브러리 연동 성공.
- **핵심 로직**: 
    - MySQL C API를 이용해 DB에 접속하여 최신 가격 데이터 2개를 조회.
    - 현재가와 이전 가격을 비교하여 **상승/하락/보합** 상태를 판단하는 알고리즘 초안 작성,
- **Troubleshooting**: `libmysql.dll` 누락 문제를 실행 폴더 복사를 통해 해결.

#### 4. 시스템 연동 확인 (Integration Test)
- **Flow**: [Python] 시세 수집 → [MySQL] 데이터 저장 → [C++] 데이터 조회 및 전략 판단
- **결과**: 두 프로그램이 동시에 돌아가며 실시간으로 매매 신호(`🚀 상승!`, `📉 하락`)를 출력하는 것을 확인.

## 3일차

- [ ] **실제 매매 로그 기록**: C++에서 상승 신호 발생 시 `trade_logs` 테이블에 INSERT 실행. 
- [ ] **자산 관리 로직**: 초기 자본 설정 및 매수 시 `assets` 테이블 업데이트 기능 추가.
- [ ] **전략 고도화**: 단순 가격 비교를 넘어 '이동평균선(MA)' 계산 로직 구현 시작.

### ✅ 오늘의 성과
- **실시간 자산 업데이트 로직 완성**:
  - 매수 신호 발생 시 `assets` 테이블에서 `CASH` 잔액을 차감하고 `BTC` 보유 수량을 즉각 반영하는 트랜잭션 구현.
  - SQL `ON DUPLICATE KEY UPDATE` 구문을 활용하여 코인 보유량 합산 로직 최적화.
- **실시간 수익률(ROI) 산출 엔진 구현**:
  - `trade_logs` 테이블의 과거 매수 기록을 분석하여 **매수 평균 단가(Avg Price)** 산출.
  - 현재 시세와 평단가를 비교하여 실시간 수익률을 콘솔 및 DB에 출력하는 기능 추가.
- **DB 정합성 해결**:
  - `autocommit` 설정 및 `COMMIT` 명령을 통한 데이터 영구 저장 이슈 해결.
  - `asset_type`의 PK(Primary Key) 특성을 활용한 데이터 중복 방지.

### 📊 현재 구동 화면
> `📊 현재: 103,491,000 | 이전: 103,491,000 -> ➡️ 보합 | 평단가: 103,408,785원 | 수익률: 0.08%`
> (실시간으로 자산 가치를 평가하며 안정적으로 구동 중)

### 🔍 Troubleshooting & Lessons Learned
1. **함수 호출 누락 및 로직 흐름 개선**:
   - 문제: 자산 업데이트 함수를 정의했으나 매수 조건문 내 호출 누락으로 DB 미반영.
   - 해결: `checkMarketAndDecide` 내 조건부 호출 로직을 점검하여 매매 시점과 자산 업데이트 시점 동기화.
2. **DB 대소문자 구분 및 데이터 무결성 확보**:
   - 문제: 'CASH'와 'cash'의 혼용으로 인한 `UPDATE` 쿼리 실패.
   - 해결: DB 데이터와 소스코드 내 문자열을 대문자로 표준화하여 쿼리 정확도 향상.
3. **트랜잭션 영속성 확보**:
   - 문제: 프로그램 종료 시 데이터 휘발 현상 발생.
   - 해결: `mysql_autocommit` 활성화 및 명시적 `COMMIT` 명령을 통해 데이터 영속성(Persistence) 확보.

## 4일차

### 오늘의 최종 성과 요약
  - C++: 함수 분리(Refactoring)로 코드의 안정성 확보
  - JSON: 공용 설정 파일로 시스템 관리 편의성 증대
  - Python: 실시간 자산 모니터링 시각화 성공

- 잔고 확인 로직 (Balance Check)
  - 기능: 매수 주문 실행 전, DB의 assets 테이블을 조회하여 실제 매수 가능한 CASH 잔액이 있는지 검증합니다.
  - 효과: 잔액 부족으로 인한 SQL 오류를 방지하고, 무분별한 매수 시도를 차단합니다.

- 중복 매수 방지 (Anti-Double-Buy)
  - 기능: 현재 BTC를 보유 중인지 체크하여, 이미 코인이 있다면 추가 매수 신호가 와도 진입을 제한합니다
  - 효과: 한 번의 상승장에 자산이 몰빵되는 것을 방지하고, 정해진 비중(0.001 BTC 등)으로만 매매하도록 관리합니다.

- 자동 청산 및 자산 반영 (Auto-Exit & Sync)
  - 기능: 매수 후 실시간 수익률(ROI)을 계산하여 익절(+2.0%) 또는 손절(-1.0%) 기준 도달 시 자동으로 매도(SELL)를 실행합니다.
  - 효과: 매매 즉시 assets 테이블의 현금과 코인 잔고를 실시간 업데이트하여 데이터 정밀도를 유지합니다.

  ### 결과
  ![alt text](image.png)
  ```
  | ID | Ticker | Side | Price | Volume | Timestamp |
  | :--- | :--- | :--- | :--- | :--- | :--- |
  | 1 | KRW-BTC | BUY | 106,517,000 | 0.001 | 2026-04-08 01:15 |
  | 2 | KRW-BTC | SELL | 106,295,000 | 0.001 | 2026-04-08 01:27 |
  | 3 | KRW-BTC | BUY | 106,254,000 | 0.001 | 2026-04-08 01:27 |
  | 4 | KRW-BTC | SELL | 106,201,000 | 0.001 | 2026-04-08 01:28 |
  ```
2. 주요 기능 (Key Features)
실시간 데이터 연동: Python으로 수집된 업비트 시세를 MySQL을 통해 실시간으로 읽어옴.

- 이동평균선(MA5) 전략: 최근 5회차 가격 평균을 계산하여 현재가와 비교하는 추세 추종 매매.

- 자동 자산 관리: 매수/매도 시 assets 테이블의 원화(CASH)와 비트코인(BTC) 잔고를 실시간 업데이트.

- 매매 일지 자동 기록: 모든 거래 내역(가격, 시간, 종류)을 trade_logs 테이블에 자동 저장.

- 리스크 관리 로직:
  - 익절(Take-Profit): 설정 수익률(예: +0.01%) 도달 시 자동 매도.

  - 손절(Stop-Loss): 설정 수익률(예: -0.01%) 도달 시 자동 매도.

  - 중복 매수 방지: 코인 보유 중일 경우 추가 매수 금지 로직 포함.

3. 모듈화 현황 (Refactoring)
- DatabaseManager 클래스 구현:

  - 기존 main.cpp에 밀집되어 있던 SQL 쿼리와 DB 접속 로직을 분리.
  - DatabaseManager.h / .cpp 파일을 통해 DB 접근을 객체화하여 유지보수성 향상.
- Main Logic 간소화: main.cpp는 매매 전략과 루프 제어에만 집중하도록 설계.

[안정성 강화(예외 처리)]
```
1. C++ 코드 리팩토링 (기초 공사)
작업 내용: main.cpp에 몰려있던 코드를 get_total_asset, update_balance 등 기능별 함수로 분리.

분류: 2️⃣ 시스템 안정성 및 최적화 (Stability)

효과: * 가독성 향상: 코드가 깔끔해져서 어디가 틀렸는지 찾기 쉬워짐.

재사용성: 나중에 다른 기능을 추가할 때 만들어둔 함수를 그대로 쓸 수 있음.

안정성: 한 부분의 수정이 전체 시스템을 망가뜨릴 위험을 줄임.

2. 환경 설정의 외부화 (공용 설계도)
작업 내용: DB 접속 정보 등을 코드에 직접 쓰지 않고 config.json 파일로 분리.

분류: 3️⃣ 시각화 및 관리 (Visualization & Config)

효과: * 보안: 소스 코드를 공유해도 내 비번은 공개되지 않음.

협업: C++ 엔진과 Python 모니터가 똑같은 정보를 공유해서 사용하게 함.

3. 실시간 모니터링 시스템 구축 (결과물)
작업 내용: Python의 matplotlib을 이용해 자산 변화 그래프 구현.

분류: 3️⃣ 시각화 및 관리 (Visualization & Config)

효과: * 시각화: 숫자로만 보던 자산을 한눈에 들어오는 그래프로 확인 가능.

실시간 감시: 엔진이 잘 돌아가는지 매번 DB를 뒤져보지 않아도 됨.

````

  


1️⃣ 전략 고도화 (Intelligence)
[v] 기술적 지표 도입: 이동평균선(MA5, MA20) 추세 추종 구현 완료.

[v] 자동 손절/익절: 수익률 기반 자동 매도 로직 구현 완료.

[v] 변동성 돌파 전략: 래리 윌리엄스 전략 이식 완료.

2️⃣ 시스템 안정성 및 최적화 (Stability)
[v] 코드 리팩토링: main.cpp 함수 분리 및 구조화 완료. (유지보수성 향상)

[ ] 예외 처리: API/DB 재접속 로직 강화 (다음 목표)

3️⃣ 시각화 및 관리 (Visualization & Config)
[v] 실시간 대시보드: Python 기반 실시간 자산 그래프 구현 완료.

[v] 환경 설정 파일화: config.json을 통한 C++ & Python 설정 공유 완료.
```
pip install pandas matplotlib mysql-connector-python
```
---

## 🛠️ 기술 스택
- **Language**: C++ (Core Engine), Python (Data Collector)
- **Database**: MySQL 8.0
- **Environment**: Windows 11, Visual Studio 2022
- **Library**: `libmysql`, `requests` (Python)
---------------------------------------------


