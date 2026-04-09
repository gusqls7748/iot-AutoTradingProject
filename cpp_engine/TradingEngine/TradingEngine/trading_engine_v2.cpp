#include <iostream>
#include <mysql.h>
#include <string>
#include <vector>
#include <windows.h>
#include <sstream> 
#include <iomanip>
#include "DatabaseManager.h"

using namespace std;

// RSI 계산을 위한 엔진 클래스 추가
class StrategyEngine {
public:
    double calculateRSI(const std::vector<double>& prices, int period = 14) {
        if (prices.size() < period + 1) 
            return 50.0;
        double gainSum = 0.0, lossSum = 0.0;
        for (int i = 1; i <= period; i++) {
            double diff = prices[prices.size() - i] - prices[prices.size() - i - 1];
            if (diff > 0)gainSum += diff;
            else lossSum -= diff;
        }
        if (lossSum == 0) return 100.0;
        double rs = gainSum / lossSum;
        return 100.0 - (100.0 / (1.0 + rs));
    }
};

DatabaseManager db; // 전역 또는 메인 내 객체 생성
StrategyEngine engine; //engine 객체 생성

// --- [추가] 함수 선언 (컴파일러에게 나중에 이 함수가 나올 거라고 미리 알려줌) ---
double getBalance(string assetType);
// --- 여기서부터 함수 정의 (컴퓨터에게 도구 설명하기) ---

void checkMarketAndDecide() {
    double current = db.getCurrentPrice();
    double ma5 = db.getMA5();

    // [해결] 15개를 가져오는 함수는 아마 DatabaseManager에 새로 만드셔야 할 겁니다.
    // 만약 아직 안 만드셨다면 임시로 현재가만 넣은 벡터를 만들어 테스트합니다.
    std::vector<double> prices = db.getRecentPrices(15);
    double rsi = engine.calculateRSI(prices, 14);

    // 실제로는 DatabaseManager에 아래와 같은 함수를 추가하는 것이 정석입니다:
    // std::vector<double> prices = db.getRecentPrices(15);

    if(ma5 > 0 && current > 0){
        cout << " 가격: " << (long long)current
            << " | MA5: " << (long long)ma5
            << " | RSI: " << fixed << setprecision(1) << rsi;
    
        // --- 매수 조건: 골든크로스 + 과매수 방지(RSI 60 이하) ---
        if (current > ma5 && rsi <= 60.0) {
            if (db.getBalance("BTC") <= 0 && db.getBalance("CASH") >= current * 0.001) {
                cout << " -> 전략 일치! 매수 실행";
                db.recordTrade(current, "BUY");
                db.updateAssets(current, 0.001);
            }
        }
        // 매도 조건: 익절/손절 + 과열 구간(RSI 70 이상) --
            else if (db.getBalance("BTC") > 0) {
            double avgPrice = db.getLastBuyPrice();
            double roi = ((current - avgPrice) / avgPrice) * 100;

            if(roi >= 0.5 || rsi >= 70.0){
                cout << " -> 목표 도달 또는 과열! 매도 실행";
                db.recordTrade(current, "SELL");
                db.updateAssets(current, -0.001);
            }
        }
        cout << endl;
    }
}

// [6] 프로그램 시작점
int main() {
    if (!db.loadConfig()) return -1;
    if (!db.connect()) return -1;

    std::cout << "트레이딩 엔진 v2 시작 (RSI 전략 도입)" << std::endl;

    while (true) {
        try {
            checkMarketAndDecide();
        }
        catch (const std::exception& e) {
            std::cout << "\n [에러]: " << e.what() << std::endl;
        }
        Sleep(5000);
    }
    return 0;
}