CREATE DATABASE EcoTrack;
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

CREATE TABLE IF NOT EXISTS transportation (
    TransportationID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    Gasoline_Carbon REAL,
    Diesel_Carbon REAL,
    Tricycle_Carbon REAL,
    Jeep_Carbon REAL,
    Van_Carbon REAL,
    Bus_Carbon REAL,
    Total_CarbonFootprint_Transportation REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES user(UserID)
);

CREATE TABLE IF NOT EXISTS food_consumption (
    FoodConsumptionID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    FreshVegetables_Carbon REAL,
    Rice_Carbon REAL,
    Eggs_Carbon REAL,
    MilkPowder_Carbon REAL,
    Cheese_Carbon REAL,
    Butter_Carbon REAL,
    Beef_Carbon REAL,
    PigMeat_Carbon REAL,
    PoultryMeat_Carbon REAL,
    Fish_Carbon REAL,
    Coffee_Carbon REAL,
    Chocolate_Carbon REAL,
    Total_CarbonFootprint_Food REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES user(UserID)
);

CREATE TABLE IF NOT EXISTS full_assessment (
    Full_AssessmentID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    Household_Total FLOAT NOT NULL,
    Transportation_Total FLOAT NOT NULL,
    Food_Consumption_Total FLOAT NOT NULL,
    Overall_Total FLOAT NOT NULL,
    Full_AssessmentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES user(UserID)
);
