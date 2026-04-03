-- 1. 마켓 데이터 (현재가 저장용)
CREATE TABLE IF NOT EXISTS market_data(
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    price DOUBLE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 매매 기록 (언제, 얼마에 샀는지)
CREATE TABLE IF NOT EXISTS trade_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,  --AUTO_INCREMENT 자동으로 값 증가
    ticker VARCHAR(20) NOT NULL,
    side ENUM('BUY', 'SELL') NOT NULL,
    price DOUBLE NOT NULL,
    volume DOUBLE NOT NULL,
    traded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 자산현황
CREATE TABLE IF NOT EXISTS assets (
    asset_type VARCHAR(20) PRIMARY KEY, -- 'CASH', 'BTC' 등
    balance DOUBLE DEFAULT 0.0
);

-- 초기 자금 설정 (예 100만원)
INSERT INTO assets (asset_type, balance) values ('CASH', 1000000);