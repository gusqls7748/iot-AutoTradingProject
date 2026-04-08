#include <iostream>
#include <mysql.h>
#include <string>
#include <vector>
#include <windows.h>
#include <sstream> 
#include <iomanip>
#include "DatabaseManager.h"

using namespace std;

DatabaseManager db; // 전역 또는 메인 내 객체 생성

// [1] 전역 변수 설정
const char* db_host = "127.0.0.1";
const char* db_user = "root";
const char* db_pw = "my123456";
const char* db_name = "AutoTrading";

// --- [추가] 함수 선언 (컴파일러에게 나중에 이 함수가 나올 거라고 미리 알려줌) ---
double getBalance(string assetType);
// --- 여기서부터 함수 정의 (컴퓨터에게 도구 설명하기) ---

void checkMarketAndDecide() {
    double ma5 = db.getMA5();
    double current = db.getCurrentPrice();

    if (ma5 > 0 && current > 0) {
        std::cout << " 현재: " << (long long)current << " | MA5: " << (long long)ma5;

        /*1.매수 로직*/
        if (current > ma5) {
            if (db.getBalance("BTC") > 0) {
                std::cout << " ->  이미 보유 중";
            }
            else if (db.getBalance("CASH") >= current * 0.001) {
                db.recordTrade(current, "BUY");
                db.updateAssets(current, 0.001);
            }
        }
        else {
            cout << " 관망 ";
        }
        // ... 매도 로직(checkSaleCondition)도 db 객체를 활용해 수행
       double avgPrice = db.getLastBuyPrice();
        if (db.getBalance("BTC") > 0 && avgPrice > 0) {
            double roi = ((current - avgPrice) / avgPrice) * 100;
                cout << fixed << setprecision(2) << " | 평단: " << (long long)avgPrice << " | 수익률: " << roi << "%";

            // 테스트를 위해 0.01% 기준으로 설정됨
            if (roi >= 0.01) {
                cout << "\n [익절 실행!]";
                db.recordTrade(current, "SELL");
                db.updateAssets(current, -0.001);
            }
            else if (roi <= -0.01) {
                cout << "[손절 실행]";
                db.recordTrade(current, "SELL");
                db.updateAssets(current, -0.001);
            }
        }
        cout << endl;
    }
}

//// [2] 매매 기록 함수 (가장 기초)
//void recordTrade(double price, string side) {
//    MYSQL* conn = mysql_init(NULL);
//    if (!mysql_real_connect(conn, host, user, pw, db, 3306, NULL, 0)) return;
//    stringstream ss;
//    ss << fixed << setprecision(0);
//    ss << "INSERT INTO trade_logs (ticker, side, price, volume) VALUES ('KRW-BTC', '" << side << "', " << price << ", 0.001)";
//    mysql_query(conn, ss.str().c_str());
//    cout << "\n✅ [DB 기록] " << side << " 완료" << endl;
//    mysql_close(conn);
//}
//
//void updateAssets(double price, double volume) {
//    MYSQL* conn = mysql_init(NULL);
//    if (!mysql_real_connect(conn, host, user, pw, db, 3306, NULL, 0)) return;
//
//    double totalPrice = price * abs(volume);
//    stringstream ss1, ss2;
//    ss1 << fixed << setprecision(0);
//    ss2 << fixed << setprecision(8);
//
//    if (volume > 0) { // 매수
//        ss1 << "UPDATE assets SET balance = balance - " << totalPrice << " WHERE asset_type = 'CASH'";
//        ss2 << "INSERT INTO assets (asset_type, balance) VALUES ('BTC', " << volume << ") "
//            << "ON DUPLICATE KEY UPDATE balance = balance + " << volume;
//    }
//    else { // 매도
//        ss1 << "UPDATE assets SET balance = balance + " << totalPrice << " WHERE asset_type = 'CASH'";
//        // [수정] BTC 잔고를 직접 0으로 밀어버리는 가장 확실한 방법 (일단 테스트용)
//        ss2 << "UPDATE assets SET balance = 0 WHERE asset_type = 'BTC'";
//    }
//
//    // 쿼리 실행 및 에러 확인
//    if (mysql_query(conn, ss1.str().c_str())) {
//        cout << "❌ 현금 업데이트 실패: " << mysql_error(conn) << endl;
//    }
//    if (mysql_query(conn, ss2.str().c_str())) {
//        cout << "❌ BTC 업데이트 실패: " << mysql_error(conn) << endl;
//    }
//
//    mysql_close(conn);
//    cout << " 💰 [자산 반영 시도 완료]";
//}
//
//// [4] 수익률 체크 및 매도 판단 함수
//void checkSaleCondition(double currentPrice) {
//    // 1. 먼저 BTC 잔고가 있는지 확인 (getBalance 활용)
//    double btcBalance = getBalance("BTC");
//
//    // 코인이 없거나 아주 미세한 양(먼지)만 있다면 함수 종료
//    if (btcBalance <= 0.00001) {
//        return;
//    }
//
//    MYSQL* conn = mysql_init(NULL);
//    if (!mysql_real_connect(conn, host, user, pw, db, 3306, NULL, 0)) return;
//    // 현재 보유 중인 코인의 평단가만 가져오기 위해 '최근 매수 기록'을 조회하는 것이 더 정확합니다.
//    string query = "SELECT price FROM trade_logs WHERE side = 'BUY' ORDER BY id DESC LIMIT 1";
//    double avgPrice = 0;
//
//    if (mysql_query(conn, query.c_str()) == 0) {
//        MYSQL_RES* res = mysql_store_result(conn);
//        MYSQL_ROW row = mysql_fetch_row(res);
//        if (row && row[0]) avgPrice = atof(row[0]);
//        mysql_free_result(res);
//    }
//    if (avgPrice > 0) {
//        double roi = ((currentPrice - avgPrice) / avgPrice) * 100;
//        cout << fixed << setprecision(2) << " | 평단: " << (long long)avgPrice << " | 수익률: " << roi << "%";
//
//        if (roi >= 0.01) {
//            cout << "\n✨ [익절 실행!]";
//            recordTrade(currentPrice, "SELL");
//            updateAssets(currentPrice, -0.001);
//        }
//        else if (roi <= -0.01) {
//            cout << "\n📉 [손절 실행!]";
//            recordTrade(currentPrice, "SELL");
//            updateAssets(currentPrice, -0.001);
//        }
//    }
//    mysql_close(conn);
//}
//
//// [추가] 자산 확인을 위한 도구 함수
//double getBalance(string assetType) {
//    MYSQL* conn = mysql_init(NULL);
//    if (!mysql_real_connect(conn, host, user, pw, db, 3306, NULL, 0)) return -1.0;
//
//    string query = "SELECT balance FROM assets WHERE asset_type = '" + assetType + "'";
//    double balance = 0;
//
//    if (mysql_query(conn, query.c_str()) == 0) {
//        MYSQL_RES* res = mysql_store_result(conn);
//        MYSQL_ROW row = mysql_fetch_row(res);
//        if (row && row[0])balance = atof(row[0]);
//        mysql_free_result(res);
//    }
//    mysql_close(conn);
//    return balance;
//}


// [5] 메인 전략 함수 (위의 함수들을 다 모아서 사용)
//void checkMarketAndDecide() {
//    MYSQL* conn = mysql_init(NULL);
//    if (!mysql_real_connect(conn, host, user, pw, db, 3306, NULL, 0)) return;
//
//    // 1. 데이터 조회 (MA5 및 현재가)
//    string maQuery = "SELECT AVG(price) FROM(SELECT price FROM market_data ORDER BY id DESC LIMIT 5) AS temp";
//    string curQuery = "SELECT price FROM market_data ORDER BY id DESC LIMIT 1";
//    double ma5 = 0, current = 0;
//
//    if (mysql_query(conn, maQuery.c_str()) == 0) {
//        MYSQL_RES* res = mysql_store_result(conn);
//        MYSQL_ROW row = mysql_fetch_row(res);
//        if (row && row[0]) ma5 = atof(row[0]);
//        mysql_free_result(res);
//    }
//    if (mysql_query(conn, curQuery.c_str()) == 0) {
//        MYSQL_RES* res = mysql_store_result(conn);
//        MYSQL_ROW row = mysql_fetch_row(res);
//        if (row && row[0]) current = atof(row[0]);
//        mysql_free_result(res);
//    }
//
//    if (ma5 > 0 && current > 0) {
//        cout << "📊 현재: " << (long long)current << " | MA5: " << (long long)ma5;
//
//        // [핵심] 골든크로스(매수 신호) 발생 시
//        if (current > ma5) {
//            // DB에서 실제 내 잔고를 다시 확인
//            double cashBalance = getBalance("CASH");
//            double btcBalance = getBalance("BTC");
//            double buyVolume = 0.001; // 살 수량
//            double requiredCash = current * buyVolume; // 필요한 현금
//
//            if (btcBalance > 0) {
//                // [중복 매수 방지] 이미 코인을 가지고 있다면 사지 않음
//                cout << " -> ⚠️ 이미 보유 중 (중복 매수 제한)";
//            }
//            else if (cashBalance < requiredCash) {
//                // [마이너스 잔고 방지] 돈이 모자라면 사지 않음
//                cout << " -> 💸 잔액 부족 (필요: " << (long long)requiredCash << " / 보유: " << (long long)cashBalance << ")";
//            }
//            else {
//                // 모든 조건 만족 시 매수 실행
//                cout << " -> 🚀 매수 신호! (진입)";
//                recordTrade(current, "BUY");
//                updateAssets(current, buyVolume);
//            }
//        }
//        else {
//            cout << " -> 💤 관망";
//        }
//
//        // 매도 조건 체크 (보유 여부 등은 checkSaleCondition 내부에서 판단)
//        checkSaleCondition(current);
//        cout << endl;
//    }
//    mysql_close(conn);
//}

// [6] 프로그램 시작점
int main() {
    if (!db.loadConfig()) {
        std::cout << " 설정을 불러오지 못해 프로그램을 종료합니다." << std::endl;
        return -1;
    }

    // 2. 읽어온 설정을 바탕으로 DB에 접속합니다.
    if (!db.connect()) {
        std::cout << " 연결 실패!" << std::endl;
        return -1;  // 연결 실패시 종료
    }

    std::cout << "트레이딩 엔진 시작" << std::endl;

    while (true) {
        try {
            checkMarketAndDecide();
        }

        catch (const std::exception& e) {
            // 어떤 에러가 났는지 출력하고 프로그램은 계속 실행
            std::cout << "\n [런타임 에러 발생]: " << e.what() << std::endl;
            std::cout << "5초후 다시 시도..." << std::endl;
        }
        catch (...) {
            std::cout << " 알수 없는 치명적 에러 발생" << std::endl;
        }
        Sleep(5000);    // 5초 대기

    }
    return 0;
}