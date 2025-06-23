-- Results table
CREATE TABLE "footballresults" (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  "Home Team" TEXT,
  "Away Team" TEXT,
  "League" TEXT,
  "Score" TEXT,
  "Result" TEXT,
  "HomePower" REAL,
  "AwayPower" REAL,
  "H1.5" REAL,
  "H2.5" REAL,
  "A1.5" REAL,
  "A2.5" REAL,
  "HomeBTTS" REAL,
  "AwayBTTS" REAL,
  "Home Form" TEXT,
  "Away Form" TEXT,
  "1" REAL,
  "2" REAL,
  "Home GD" REAL,
  "Home Position" REAL,
  "Away Position" REAL,
  "Match Date" TEXT,
  "Total Goals" INTEGER
)

-- Upcomingmatches table 
CREATE TABLE "Upcomingmatches" (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  "Home Team" TEXT,
  "Away Team" TEXT,
  "League" TEXT,
  "Home Position" REAL,
  "Away Position" REAL,
  "Home GD" REAL,
  "Pick" TEXT,
  "1" REAL,
  "X" REAL,
  "2" REAL,
  "Home Form" TEXT,
  "Away Form" TEXT,
  "H1.5" INTEGER,
  "A1.5" INTEGER,
  "H2.5" INTEGER,
  "A2.5" INTEGER,
  "HomeBTTS" INTEGER,
  "AwayBTTS" INTEGER,
  "HomePower" REAL,
  "AwayPower" REAL,
  "Match Date" TIMESTAMP
)

-- Predictions table 
CREATE TABLE "Predictions" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "Home Team" TEXT,
    "Away Team" TEXT,
    "League" TEXT,
    "Match Date" TEXT,
    "Odd" REAL,
    "Prediction" TEXT,
    "Success" INTEGER CHECK("Success" IN (0, 1))
)