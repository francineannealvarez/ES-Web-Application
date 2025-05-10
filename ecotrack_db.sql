USE EcoTrack;

CREATE TABLE IF NOT EXISTS user (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    User_FirstName VARCHAR(100) NOT NULL,
    User_MiddleName VARCHAR(100) NOT NULL,
    User_LastName VARCHAR(100) NOT NULL,
    Username VARCHAR(255) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS household (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    Electricity REAL,
    LPG REAL,
    WaterConsumption REAL,
    Waste REAL,
    Total_CarbonFootprint_Household REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES user(UserID) 
);
