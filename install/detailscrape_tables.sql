CREATE TABLE monster.history (
  `id` int NOT NULL AUTO_INCREMENT,
  `url` VARCHAR(255) NOT NULL,
  `datescraped` datetime DEFAULT NULL,
  `status` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE INDEX urllookup ON monster.history(url);

CREATE TABLE teamlease.history (
  `id` int NOT NULL AUTO_INCREMENT,
  `url` VARCHAR(255) NOT NULL,
  `datescraped` datetime DEFAULT NULL,
  `status` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE INDEX urllookup ON teamlease.history(url);

