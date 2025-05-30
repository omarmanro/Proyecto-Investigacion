-- Script de migración para crear la tabla WeatherData en Supabase
CREATE TABLE
IF NOT EXISTS WeatherData
(
    STATION TEXT NOT NULL,
    DATE TIMESTAMP NOT NULL,
    LATITUDE NUMERIC
(9, 6),
    LONGITUDE NUMERIC
(9, 6),
    ELEVATION NUMERIC
(10, 2),
    WND_DIRECTION INTEGER,
    WND_SPEED NUMERIC
(5, 2),
    CIG_HEIGHT INTEGER,
    VIS_DISTANCE INTEGER,
    TMP NUMERIC
(5, 2),
    DEW NUMERIC
(5, 2),
    SLP NUMERIC
(6, 2),
    LLOVIÓ INTEGER,
    PRIMARY KEY
(STATION, DATE)
);

-- Índices adicionales para mejorar el rendimiento
CREATE INDEX
IF NOT EXISTS idx_weatherdata_date ON WeatherData
(DATE);
CREATE INDEX
IF NOT EXISTS idx_weatherdata_station ON WeatherData
(STATION);
