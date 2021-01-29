/* TODO: 
 *  Need to add UDF or constraint to check that for buying triggers user has enough money in their account.
 *  Or for selling triggers he user has the amount of stock in the account.
*/

-- Table for all accounts and amount of money available to invest 
CREATE TABLE accounts (
    userid varchar(50) PRIMARY KEY,
    funds integer CHECK (funds >= 0)
);

-- All of the users currents stocks
CREATE TABLE stocks (
    userid varchar(50) REFERENCES accounts(userid),
    stockSymbol varchar(20),
    amount integer,
    PRIMARY KEY (userid, stockSymbol)
);

-- Keeps track of set_buy_trigger/set_buy_trigger/cancel_set_buy
CREATE TABLE buy_triggers (
    userid varchar(50) REFERENCES accounts(userid),
    stockSymbol varchar(10),
    amount integer,
    price integer,
    PRIMARY KEY (userid, stockSymbol, amount)
);

-- Keeps track of set_sell_trigger/set_sell_trigger/cancel_set_sell
CREATE TABLE sell_triggers (
    userid varchar(50) REFERENCES accounts(userid),
    stockSymbol varchar(10),
    amount integer,
    price integer,
    PRIMARY KEY (userid, stockSymbol, amount)
);

-- Logs every transactions, for dumplog command
CREATE TABLE logs (
    command varchar(50),
    userid varchar(50),
    stockSymbol varchar(10),
    amount integer,
    timing timestamp,
);