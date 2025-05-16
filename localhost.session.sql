INSERT INTO transportation (
    TransportationID,
    UserID,
    Gasoline_Carbon,
    Diesel_Carbon,
    Tricycle_Carbon,
    Jeep_Carbon,
    Van_Carbon,
    Bus_Carbon,
    Total_CarbonFootprint_Transportation,
    timestamp
  )
VALUES (
    TransportationID:int,
    UserID:int,
    'Gasoline_Carbon:double',
    'Diesel_Carbon:double',
    'Tricycle_Carbon:double',
    'Jeep_Carbon:double',
    'Van_Carbon:double',
    'Bus_Carbon:double',
    'Total_CarbonFootprint_Transportation:double',
    'timestamp:datetime'
  );