## iot-AutoTradingProject
2026년 Iot개발 miniProject 1

### 알고리즘 기반 '주식/가상화폐 자동 매매 시뮬레이션

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
---

## 🗺️ 향후 개발 로드맵 (Roadmap)

### 1️⃣ 전략 고도화 (Intelligence)
- [ ] **기술적 지표 도입**: 단순 가격 비교를 넘어 **이동평균선(MA5, MA20)**을 계산하여 추세 추종 매매 구현.
- [ ] **자동 손절/익절(Stop-Loss/Take-Profit)**: 설정한 수익률(예: -3% 손절, +5% 익절) 도달 시 자동 매도 로직 추가.
- [ ] **변동성 돌파 전략 이식**: 래리 윌리엄스의 변동성 돌파 로직을 활용한 진입 타점 정교화.

### 2️⃣ 시스템 안정성 및 최적화 (Stability)
- [ ] **예외 처리(Error Handling)**: API 응답 지연 및 DB 연결 유실 시 자동 재접속을 위한 `try-catch` 및 재시도 로직 강화.
- [ ] **멀티 스레딩(Multi-Threading)**: 데이터 수집(Python)과 분석/매매(C++)의 병목 현상을 제거하기 위한 스레드 분리 작업.

### 3️⃣ 시각화 및 관리 (Visualization & Config)
- [ ] **실시간 대시보드**: Python `matplotlib` 또는 `plotly`를 활용하여 자산 변화 추이 그래프 시각화.
- [ ] **환경 설정 파일화**: DB 접속 정보 및 매매 설정값(매수 단위 등)을 `config.json` 또는 `.env`로 외부화하여 보안 및 편의성 증대.

---

## 🛠️ 기술 스택
- **Language**: C++ (Core Engine), Python (Data Collector)
- **Database**: MySQL 8.0
- **Environment**: Windows 11, Visual Studio 2022
- **Library**: `libmysql`, `requests` (Python)
---------------------------------------------
비트코인 자동 매매 엔진 (IoT-AutoTrading-System)C++ & MySQL 기반의 기술적 지표(MA5) 추세 추종 매매 시스템 > 본 프로젝트는 실시간 시장 데이터를 분석하여 이동평균선 돌파 시 매수하고, 설정된 수익률에 따라 자동 익절 및 손절을 수행하는 트레이딩 엔진입니다.📌 핵심 기능 (Core Features)MA5(5일 이동평균선) 전략: 최근 5개 캔들의 평균 가격을 계산하여 현재가가 이를 돌파할 시 상승 추세로 판단 및 매수(BUY).실시간 수익률(ROI) 모니터링: 매수 평균 단가(Avg Price)를 실시간으로 추적하여 현재가 대비 수익률을 % 단위로 산출.자동 매도 시스템 (Exit Strategy):익절(Take-Profit): 수익률 +2.0% 달성 시 자동 매도.손절(Stop-Loss): 수익률 -1.0% 도달 시 손실 최소화를 위한 자동 매도.자산 동기화 (Asset Management): MySQL과 연동하여 현금(CASH) 및 코인(BTC) 잔고를 실시간으로 업데이트 및 영구 저장.🏗️ 시스템 아키텍처데이터 수집: Python(Upbit API)을 사용하여 실시간 시세를 MySQL market_data 테이블에 적재.전략 실행: C++ 엔진이 5초 주기로 DB를 조회하여 MA5 지표 계산 및 매매 의사결정.기록 및 반영: 매매 내역은 trade_logs에 기록되고, 최종 자산 상태는 assets 테이블에 즉시 반영.🛠️ 기술 스택 (Tech Stack)Language: C++11, Python 3.10Database: MySQL 8.0API/Library: libmysql (MySQL C API), Windows.h (System Control)IDE: Visual Studio 2022📊 매매 로직 (Trading Logic)진입(Entry): $CurrentPrice > MA5$ (상승 돌파 시 매수)수익률(ROI): $\frac{CurrentPrice - AvgPrice}{AvgPrice} \times 100$청산(Exit): $ROI \ge 2.0\%$ 또는 $ROI \le -1.0\%$🔍 Troubleshooting & Lessons Learned1. C++ 컴파일러의 순차적 독해 특성문제: 함수 정의 순서가 꼬여 recordTrade 등 하위 함수를 상단에서 호출할 때 "식별자를 찾을 수 없음" 에러 발생.해결: 기초 함수를 상단에, 이를 조합하는 고수준 함수(checkMarketAndDecide)를 하단에 배치하여 코드 의존성 문제 해결.2. 수치 데이터 표현 및 정밀도 문제문제: 비트코인 가격(억 단위) 처리 시 SQL 쿼리에 지수 형태(e+)로 전달되어 문법 오류 발생.해결: std::fixed와 std::setprecision을 사용하여 숫자를 정확한 정수/실수 문자열로 변환하여 쿼리 안정성 확보.3. 자산 관리의 필요성 (Risk Management)문제: 잔고 확인 로직 부재로 인해 보유 현금보다 많은 수량을 매수하여 CASH 잔고가 음수(-)로 기록되는 버그 발견.교훈: 실제 매매 시 '보유 잔고 내 매수' 조건이 전략만큼 중요하다는 것을 학습. (향후 잔고 체크 로직 추가 예정)🗺️ 향후 로드맵 (Roadmap)[ ] 중복 매수 방지: 이미 코인을 보유한 경우 추가 진입을 제한하여 리스크 관리.[ ] 코드 모듈화: main.cpp의 기능을 헤더(.h)와 소스(.cpp) 파일로 분리하여 유지보수성 향상.[ ] 고도화 지표: MA20(20일선)을 추가하여 골든크로스/데드크로스 전략 구현.


