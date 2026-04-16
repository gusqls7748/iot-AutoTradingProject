#ifndef DATABASE_MANAGER_H
#define DATABASE_MANAGER_H

#include <mysql.h>
#include <string>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <fstream>	// JSON 라이브러리 포함
#include "json.hpp"

// 2. 별명 만들기 
using json = nlohmann::json;	// 별명 만들기

class DatabaseManager {
private:
	MYSQL* conn;

	// 이제 변수만 선언하고 값은 비워둡니다.
	std::string host;
	std::string user;
	std::string pw;
	std::string db_name;
	
	double buy_volume;

public:
	DatabaseManager();		// 데이터를 넣고 빼는 기능
	~DatabaseManager();

	bool loadConfig();
	bool ensureConnection(); // 자동 복구 시스템,
	bool connect();			// DB연결 및 재연결 로직
	void close();			// 연결 종료

	// 기존 함수들을 메서드로 전환
	//현재 보유 중인 현금(KRW)이나 코인(BTC)의 잔고를 조회
	double getBalance(std::string assetType);
	//매매 시간, 종류(BUY/SELL), 가격을 기록
	void recordTrade(double price, std::string side);
	//매매 결과에 맞춰 실제 내 가상 자산 테이블의 잔고를 업데이트
	void updateAssets(double price, double volume);

	// 전략에 필요한 데이터 가져오기
	double getMA5();
	double getCurrentPrice();
	//매도 전략(익절/손절)을 계산하기 위해 마지막으로 매수했던 평균 단가를 가져오는역활
	double getLastBuyPrice();
	// RSI 알고리즘 데이터 공급
	std::vector<double> getRecentPrices(int limit);

};


#endif // !DATAVASE_MANAGER_H
