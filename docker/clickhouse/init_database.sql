create table staging.nhl_team_stats
(
    requested_at          DateTime,
    team_id               Int32,
    team_name             String,
    stat_name             String,
    game_type_id          String,
    game_type_description String,
    statistics            String
)
    engine = MergeTree PARTITION BY toYYYYMM(requested_at)
        ORDER BY (requested_at, team_id)
        SETTINGS index_granularity = 8192;