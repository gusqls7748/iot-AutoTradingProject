#include "DatabaseManager.h"

DatabaseManager::DatabaseManager() 
	: conn(nullptr), host(""), user(""), pw(""), db_name(""), buy_volume(0.0) //  이렇게 초기화 목록을 추가!
{
	conn = mysql_init(NULL);
}

DatabaseManager::~DatabaseManager() {
	close();
}

// [추가] JSON 파일을 읽어오는 함수
bool DatabaseManager::loadConfig() { 
	std::ifstream file("config.json"); // 파일 열기 시도
	if (!file.is_open()) {
		std::cout << " config.json 파일을 열 수 없습니다!" << std::endl;
		return false;
	}

	try {
		json config;
		file >> config;

		this->host = config["database"]["host"];
		this->user = config["database"]["user"];
		this->pw = config["database"]["pw"];
		this->db_name = config["database"]["db"];
		this->buy_volume = config["trading"]["buy_volume"];

		std::cout << "✅ 설정 파일 로드 완료" << std::endl;
		return true;
	}
	catch (const std::exception& e) {
		std::cerr << "❌ JSON 파싱 에러: " << e.what() << std::endl;
		return false;
	}
}


bool DatabaseManager::connect() {
	// c_str()을 붙여서 string을 C 스타일 문자열로 바꿔서 넣어줍니다.
	if (!mysql_real_connect(conn, host.c_str(), user.c_str(), pw.c_str(), db_name.c_str(), 3306, NULL, 0)) {
		std::cerr << " DB 연결 실패: " << mysql_error(conn) << std::endl;
		return false;
	}
	return true;
}
// 쿼리 실행 전 연결 상태를 확인하고, 끊겼다면 재연결하는 헬퍼 함수
bool DatabaseManager::ensureConnection() {
	if (mysql_ping(conn) != 0) {// 연결 확인 (0이 아니면 끊긴 것
		std::cerr << "DB 연결 끊김 감지! 재시도 중..." << std::endl;
		return connect();
	}
	return true;
}

void DatabaseManager::close() {
	if (conn) {
		mysql_close(conn);
		conn = nullptr;
	}
}

// 1. 자산 잔고 확인 (CASH 또는 BTC)
double DatabaseManager::getBalance(std::string assetType) {
	if (!ensureConnection()) return -1.0; // 반환값이 double인 경우는 return -1.0;
	std::string query = "SELECT balance FROM assets WHERE asset_type = '" + assetType + "'";
	double balance = 0;

	if (mysql_query(conn, query.c_str()) == 0) {
		MYSQL_RES* res = mysql_store_result(conn);
		MYSQL_ROW row = mysql_fetch_row(res);
		if (row && row[0]) balance = std::atof(row[0]);
		mysql_free_result(res);
	}
	return balance;
}

// 2. MA5 (5회차 이동평균선) 계산
double DatabaseManager::getMA5() {
	if (!ensureConnection()) return -1.0; // 연결 실패 시 안전하게 -1 반환
	std::string query = "SELECT AVG(price) FROM(SELECT price FROM market_data ORDER BY id DESC LIMIT 5) AS temp";
	double ma5 = 0;
	if (mysql_query(conn, query.c_str()) == 0) {
		MYSQL_RES* res = mysql_store_result(conn);
		MYSQL_ROW row = mysql_fetch_row(res);
		if (row && row[0]) ma5 = std::atof(row[0]);
		mysql_free_result(res);
	}
	return ma5;
}


// 3. 최신 현재가 조회
double DatabaseManager::getCurrentPrice() {
	if (!ensureConnection()) return -1.0; // 연결 실패 시 안전하게 -1 반환
	std::string query = "SELECT price FROM market_data ORDER BY id DESC LIMIT 1";
	double price = 0;
	if (mysql_query(conn, query.c_str()) == 0) {
		MYSQL_RES* res = mysql_store_result(conn);
		MYSQL_ROW row = mysql_fetch_row(res);
		if (row && row[0]) price = std::atof(row[0]);
		mysql_free_result(res);
	}
	return price;
}

// 4. 마지막 매수 평단가 조회
double DatabaseManager::getLastBuyPrice() {
	if (!ensureConnection()) return -1.0; // 연결 실패 시 안전하게 -1 반환
	std::string query = "SELECT price FROM trade_logs WHERE side = 'BUY' ORDER BY id DESC LIMIT 1";
	double price = 0;
	if (mysql_query(conn, query.c_str()) == 0) {
		MYSQL_RES* res = mysql_store_result(conn);
		MYSQL_ROW row = mysql_fetch_row(res);
		if (row && row[0]) price = std::atof(row[0]);
		mysql_free_result(res);
	}
	return price;
}

// 5. 매매 기록 저장
void DatabaseManager::recordTrade(double price, std::string side) {
	if (!ensureConnection()) return; // 반환값이 double인 경우는 return -1.0;
	std::stringstream ss;
	ss << std::fixed << std::setprecision(0);
	ss << "INSERT INTO trade_logs (ticker, side, price, volume) VALUES ('KRW-BTC', '" << side << "'," << price << ", 0.001)";
	mysql_query(conn, ss.str().c_str());
	std::cout << "\n [DB 기록]" << side << " 완료" << std::endl;
}

// 6. 자산 테이블 업데이트
void DatabaseManager::updateAssets(double price, double volume) {
	if (!ensureConnection()) return; // 반환값이 double인 경우는 return -1.0;
	double totalPrice = price * std::abs(volume);
	std::stringstream ss1, ss2;
	ss1 << std::fixed << std::setprecision(0);
	ss2 << std::fixed << std::setprecision(8);

	if (volume > 0) { // 매수
		ss1 << "UPDATE assets SET balance = balance - " << totalPrice << " WHERE asset_type = 'CASH'";
		ss2 << "INSERT INTO assets (asset_type, balance) VALUES ('BTC', " << volume << ") ON DUPLICATE KEY UPDATE balance = balance + " << volume;
	}
	else { // 매도
		ss1 << "UPDATE assets SET balance = balance + " << totalPrice << " WHERE asset_type = 'CASH'";
		ss2 << "UPDATE assets SET balance = 0 WHERE asset_type = 'BTC'";
	}
	mysql_query(conn, ss1.str().c_str());
	mysql_query(conn, ss2.str().c_str());
	std::cout << " [자산 반영 완료] ";
}