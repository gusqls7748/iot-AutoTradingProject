#ifndef DATABASE_MANAGER_H
#define DATABASE_MANAGER_H

#include <mysql.h>
#include <string>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <fstream>	// JSON 라이브러리 포함
#include "json.hpp"

// 2. 별명 만들기 (여기에 두는 게 가장 좋습니다)
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
	DatabaseManager();
	~DatabaseManager();

	bool loadConfig();
	bool ensureConnection();
	bool connect();			// DB연결 및 재연결 로직
	void close();			// 연결 종료

	// 기존 함수들을 메서드로 전환
	double getBalance(std::string assetType);
	void recordTrade(double price, std::string side);
	void updateAssets(double price, double volume);

	// 전략에 필요한 데이터 가져오기
	double getMA5();
	double getCurrentPrice();
	double getLastBuyPrice();
	std::vector<double> getRecentPrices(int limit);

};


#endif // !DATAVASE_MANAGER_H
