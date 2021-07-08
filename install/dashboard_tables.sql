CREATE TABLE dashboard.mainpage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    site VARCHAR(45),
    filesuffix VARCHAR(45),
    datastart DATETIME,
    dataend DATETIME,
    nrows INT,
    uniquelinks INT,
    fractionblank FLOAT,
    retries INT,
    success BOOL
);

CREATE TABLE dashboard.details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    site VARCHAR(45),
    filesuffix VARCHAR(45),
    datastart DATETIME,
    dataend DATETIME,
    nrows INT,
    uniquelinks INT,
    fractionblank FLOAT,
    alreadyscraped INT,
    status0 INT,
    status1 INT,
    retries INT,
    success BOOL
);


CREATE TABLE dashboard.mainpage_test (
    id INT AUTO_INCREMENT PRIMARY KEY,
    site VARCHAR(45),
    filesuffix VARCHAR(45),
    datastart DATETIME,
    dataend DATETIME,
    nrows INT,
    uniquelinks INT,
    fractionblank FLOAT,
    retries INT,
    success BOOL
);


CREATE TABLE dashboard.details_test (
    id INT AUTO_INCREMENT PRIMARY KEY,
    site VARCHAR(45),
    filesuffix VARCHAR(45),
    datastart DATETIME,
    dataend DATETIME,
    nrows INT,
    uniquelinks INT,
    fractionblank FLOAT,
    alreadyscraped INT,
    status0 INT,
    status1 INT,
    retries INT,
    success BOOL
);