-- schema.sql: normalized schema for the Urban Mobilty Explorer
-- Works on MySQL and SQLite. Tables are dropped first so you can re-run safely.

DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS zones;
DROP TABLE IF EXISTS boroughs;

CREATE TABLE boroughs (
    borough_id    INTEGER PRIMARY KEY,
    borough_name  VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE zones (
    zone_id       INTEGER PRIMARY KEY,
    zone_name     VARCHAR(100) NOT NULL,
    service_zone  VARCHAR(50),
    borough_id    INTEGER NOT NULL,
    centroid_lat  DECIMAL(9, 6),
    centroid_lon  DECIMAL(9,6),
    boundary_geojson LONGTEXT,
    FOREIGN KEY (borough_id) REFERENCES boroughs (borough_id)
);

CREATE TABLE trips (
    trip_id            INTEGER PRIMARY KEY,
    pickup_datetime    DATETIME NOT NULL,
    dropoff_datetime   DATETIME NOT NULL,
    pickup_zone_id     INTEGER NOT NULL,
    dropoff_zone_id    INTEGER NOT NULL,
    passenger_count    INTEGER,
    trip_distance      DECIMAL(8, 2) NOT NULL,
    fare_amount        DECIMAL(8, 2) NOT NULL,
    tip_amount         DECIMAL(8, 2),
    total_amount       DECIMAL(8, 2),
    trip_duration_min  DECIMAL(8, 2) NOT NULL,
    avg_speed_mph      DECIMAL(8, 2) NOT NULL,
    cost_per_minute    DECIMAL(8, 4) NOT NULL,
    FOREIGN KEY (pickup_zone_id)  REFERENCES zones (zone_id),
    FOREIGN KEY (dropoff_zone_id) REFERENCES zones (zone_id) 
);

-- Indexes on the columns the dashboard filters by (time, location, fare)
CREATE INDEX idx_trips_pickup_time ON trips (pickup_datetime);
CREATE INDEX idx_trips_pickup_zone ON trips (pickup_zone_id);
CREATE INDEX idx_trips_dropoff_zone ON trips(dropoff_zone_id);
CREATE INDEX idx_trips_fare ON trips (fare_amount);
CREATE INDEX idx_zones_borough ON zones (borough_id);
