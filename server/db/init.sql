-- TABLES
CREATE TABLE "Logs" (
  "driverID" INTEGER NOT NULL,
  "sessionNum" INTEGER NOT NULL,
  "sampleNum" INTEGER NOT NULL,
  time VARCHAR(255),
  "timeLong" INTEGER,
  "xCoord" FLOAT,
  "yCoord" FLOAT,
  PRIMARY KEY ("driverID", "sessionNum", "sampleNum")
);

CREATE TABLE "TMAs" (
  "tmaID" INTEGER NOT NULL,
  "xCoord" FLOAT,
  "yCoord" FLOAT,
  PRIMARY KEY ("tmaID")
);
