#include <iostream>
#include <mysql.h>
#include <string>
#include <vector>
#include <windows.h>
#include <sstream> 
#include <iomanip>

using namespace std;

// [1] 전역 변수 설정
const char* host = "127.0.0.1";
const char* user = "root";
const char* pw = "my123456";
const char* db = "AutoTrading";

// --- 여기서부터 함수 정의 (컴퓨터에게 도구 설명하기) ---

// [2] 매매 기록 함수 (가장 기초)
void recordTrade(double price, string side) {
    MYSQL* conn = mysql_init(NULL);
    if (!mysql_real_connect(conn, host, user, pw, db, 3306, NULL, 0)) return;
    stringstream ss;
    ss << fixed << setprecision(0);
    ss << "INSERT INTO trade_logs (ticker, side, price, volume) VALUES ('KRW-BTC', '" << side << "', " << price << ", 0.001)";
    mysql_query(conn, ss.str().c_str());
    cout << "\n✅ [DB 기록] " << side << " 완료" << endl;
    mysql_close(conn);
}

// [3] 자산 업데이트 함수 (기초)
void updateAssets(double price, double volume) {
    MYSQL* conn = mysql_init(NULL);
    if (!mysql_real_connect(conn, host, user, pw, db, 3306, NULL, 0)) return;
    mysql_autocommit(conn, true);
    double totalPrice = price * volume;

    stringstream ss1, ss2;
    ss1 << fixed << setprecision(0) << "UPDATE assets SET balance = balance - " << totalPrice << " WHERE asset_type = 'CASH'";
    ss2 << fixed << setprecision(8) << "INSERT INTO assets (asset_type, balance) VALUES ('BTC', " << volume << ") "
        << "ON DUPLICATE KEY UPDATE balance = balance + " << volume;

    mysql_query(conn, ss1.str().c_str());
    mysql_query(conn, ss2.str().c_str());
    mysql_query(conn, "COMMIT");
    cout << "💰 [자산 반영 완료]" << endl;
    mysql_close(conn);
}

// [4] 수익률 체크 및 매도 판단 함수
void checkSaleCondition(double currentPrice) {
    MYSQL* conn = mysql_init(NULL);
    if (!mysql_real_connect(conn, host, user, pw, db, 3306, NULL, 0)) return;
    string query = "SELECT AVG(price) FROM trade_logs WHERE side = 'BUY'";
    double avgPrice = 0;
    if (mysql_query(conn, query.c_str()) == 0) {
        MYSQL_RES* res = mysql_store_result(conn);
        MYSQL_ROW row = mysql_fetch_row(res);
        if (row && row[0]) avgPrice = atof(row[0]);
        mysql_free_result(res);
    }
    if (avgPrice > 0) {
        double roi = ((currentPrice - avgPrice) / avgPrice) * 100;
        cout << fixed << setprecision(2) << " | 평단: " << (long long)avgPrice << " | 수익률: " << roi << "%";

        if (roi >= 2.0) {
            cout << "\n✨ [익절 실행!]";
            recordTrade(currentPrice, "SELL");
            updateAssets(currentPrice, -0.001);
        }
        else if (roi <= -1.0) {
            cout << "\n📉 [손절 실행!]";
            recordTrade(currentPrice, "SELL");
            updateAssets(currentPrice, -0.001);
        }
    }
    mysql_close(conn);
}

// [5] 메인 전략 함수 (위의 함수들을 다 모아서 사용)
void checkMarketAndDecide() {
    MYSQL* conn = mysql_init(NULL);
    if (!mysql_real_connect(conn, host, user, pw, db, 3306, NULL, 0)) return;

    string maQuery = "SELECT AVG(price) FROM(SELECT price FROM market_data ORDER BY id DESC LIMIT 5) AS temp";
    string curQuery = "SELECT price FROM market_data ORDER BY id DESC LIMIT 1";
    double ma5 = 0, current = 0;

    if (mysql_query(conn, maQuery.c_str()) == 0) {
        MYSQL_RES* res = mysql_store_result(conn);
        MYSQL_ROW row = mysql_fetch_row(res);
        if (row && row[0]) ma5 = atof(row[0]);
        mysql_free_result(res);
    }
    if (mysql_query(conn, curQuery.c_str()) == 0) {
        MYSQL_RES* res = mysql_store_result(conn);
        MYSQL_ROW row = mysql_fetch_row(res);
        if (row && row[0]) current = atof(row[0]);
        mysql_free_result(res);
    }

    if (ma5 > 0 && current > 0) {
        cout << "📊 현재: " << (long long)current << " | MA5: " << (long long)ma5;
        if (current > ma5) {
            cout << " -> 🚀 매수 신호!";
            recordTrade(current, "BUY");
            updateAssets(current, 0.001);
        }
        else {
            cout << " -> 💤 관망";
        }
        checkSaleCondition(current);
        cout << endl;
    }
    mysql_close(conn);
}

// [6] 프로그램 시작점
int main() {
    cout << "🛡️ Trading Engine 가동 (MA5 전략)" << endl;
    while (true) {
        checkMarketAndDecide();
        Sleep(5000);
    }
    return 0;
}