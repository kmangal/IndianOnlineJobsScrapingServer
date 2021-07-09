CREATE TABLE dashboard.mainpage (
    site VARCHAR(45) NOT NULL,
    filesuffix VARCHAR(45) NOT NULL,
    datastart DATETIME,
    dataend DATETIME,
    nrows INT,
    uniquelinks INT,
    fractionblank FLOAT,
    retries INT,
    success BOOL,
    logmissing BOOL,
	PRIMARY KEY (site, filesuffix) 
);


CREATE TABLE dashboard.details (
    site VARCHAR(45) NOT NULL,
    filesuffix VARCHAR(45) NOT NULL,
    datastart DATETIME,
    dataend DATETIME,
    nrows INT,
    uniquelinks INT,
    fractionblank FLOAT,
    alreadyscraped INT,
    status0 INT,
    status1 INT,
    retries INT,
    success BOOL,
    logmissing BOOL,
	PRIMARY KEY (site, filesuffix) 
);

CREATE TABLE dashboard.mainpage_test (
    site VARCHAR(45) NOT NULL,
    filesuffix VARCHAR(45) NOT NULL,
    datastart DATETIME,
    dataend DATETIME,
    nrows INT,
    uniquelinks INT,
    fractionblank FLOAT,
    retries INT,
    success BOOL,
    logmissing BOOL,
	PRIMARY KEY (site, filesuffix) 
);


CREATE TABLE dashboard.details_test (
    site VARCHAR(45) NOT NULL,
    filesuffix VARCHAR(45) NOT NULL,
    datastart DATETIME,
    dataend DATETIME,
    nrows INT,
    uniquelinks INT,
    fractionblank FLOAT,
    alreadyscraped INT,
    status0 INT,
    status1 INT,
    retries INT,
    success BOOL,
    logmissing BOOL,
	PRIMARY KEY (site, filesuffix) 
);