//#include <iostream>
//#include <mysql.h>
//#include <string>
//#include <windows.h> // Sleep 함수 사용
//
//using namespace std;
//
//// DB 접속 정보
//const char* host = "127.0.0.1";
//const char* user = "root";
//const char* pw = "my123456";
//const char* db = "AutoTrading";
//
//void runTradingLogic() {
//	MYSQL* conn = mysql_init(NULL);
//	if (!mysql_real_connect(conn, host, user, pw, db, 3306, NULL, 0)) {
//		cout << " 연결실패 " << endl;
//		return;
//	}
//
//	// 최근 가격 2개를 가져와서 비교 (현재가 vs 5초전 가격)
//	string query = "SELECT price FROM maket_data ORDER BY id DESC LIMIT 2";
//
//	if (mysql_query(conn, query.c_str()) == 0) {
//		MYSQL_RES* res = mysql_store_result(conn);
//		MYSQL_ROW row;
//
//		double prices[2] = { 0, 0 };
//		int i = 0;
//		while ((row = mysql_fetch_row(res)) && i < 2) {
//			prices[i++] = atof(row[0]);
//		}
//		mysql_free_result(res);
//
//		if (i == 2) {
//			double currentPrice = prices[0];	// 방금 들어온 가격
//			double prevPrice = prices[1];		// 5초전 가격
//
//			cout << "현재" << currentPrice << " | 이전: " << prevPrice;
//
//			if (currentPrice > prevPrice) {
//				cout << " -> 상승세!! (매수 검토)" << endl;
//				// 여기에 trade_logs INSERT 문을 놓으면 자동 매매가 실행됩니다.
//			}
//			else if (currentPrice < prevPrice) {
//				cout << " -> 하락세... (관망)" << endl;
//			}
//			else {
//				cout << " -> 횡보 중 " << endl;
//			}
//		}
//
//	}
//	mysql_close(conn);
//
//}
//
//int main() {
//	cout << "C++ 자동 매매 엔진이 가동되었습니다. (중지: Ctrl+c) " << endl;
//
//	while (true) {
//		runTradingLogic();
//		Sleep(5000); // 5초 대기 (파이썬 수집 주기와 맞춤
//	}
//	return 0;
//}
//
//-------------------------------------------------------------------------------------

#include <iostream>
#include <mysql.h>
#include <string>
#include <vector>
#include <windows.h>

using namespace std;

const char* host = "127.0.0.1";
const char* user = "root";
const char* pw = "my123456";
const char* db = "AutoTrading";

void checkMarketAndDecide() {
    MYSQL* conn = mysql_init(NULL);

    // 1. 연결 시도 로그
    if (!mysql_real_connect(conn, host, user, pw, db, 3306, NULL, 0)) {
        cout << "❌ DB 연결 실패: " << mysql_error(conn) << endl;
        mysql_close(conn);
        return;
    }

    // 2. 쿼리 실행 로그
    string query = "SELECT price FROM market_data ORDER BY id DESC LIMIT 2";
    if (mysql_query(conn, query.c_str()) != 0) {
        cout << "❌ 쿼리 에러: " << mysql_error(conn) << endl;
        mysql_close(conn);
        return;
    }

    MYSQL_RES* res = mysql_store_result(conn);
    if (!res) {
        cout << "❌ 결과 세트 없음" << endl;
        mysql_close(conn);
        return;
    }

    MYSQL_ROW row;
    vector<double> priceHistory;
    while ((row = mysql_fetch_row(res))) {
        priceHistory.push_back(atof(row[0]));
    }
    mysql_free_result(res);
    mysql_close(conn); // 연결을 여기서 확실히 닫아줍니다.

    // 3. 데이터 분석 로그
    if (priceHistory.size() >= 2) {
        double currentPrice = priceHistory[0];
        double prevPrice = priceHistory[1];

        cout << "📊 [분석 중] 현재: " << (long long)currentPrice << " | 이전: " << (long long)prevPrice;

        if (currentPrice > prevPrice) cout << " -> 🚀 상승!" << endl;
        else if (currentPrice < prevPrice) cout << " -> 📉 하락" << endl;
        else cout << " -> ➡️ 변동없음" << endl;
    }
    else {
        cout << "⏳ 데이터 수집 중... (현재 DB에 데이터 " << priceHistory.size() << "개 있음)" << endl;
    }
}

int main() {
    cout << "========================================" << endl;
    cout << "🛡️ C++ 자동 매매 엔진 작동 시작 (5초 주기)" << endl;
    cout << "========================================" << endl;

    while (true) {
        checkMarketAndDecide();
        Sleep(5000);
    }
    return 0;
}