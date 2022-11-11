from .core import DbTable, Event

# TABLES
CONSUMPTION_TBL = DbTable(
    name="consumption",
    columns={
        "start_time": "DATE PRIMARY KEY",
        "unit_price": "REAL",
        "total_cost": "REAL",
        "cost": "REAL",
        "consumption": "REAL",
    },
    pk="start_time",
)

EVENTS_TBL = DbTable(
    name="events",
    columns={
        "start_time": "DATE PRIMARY KEY",
        "end_time": "DATE",
        "event_type": "TEXT",
        "payload": "JSON",
    },
    pk="start_time",
)

# EVENT TYPES
DATA_UPDATE = Event(
    name="Consumption Update",
    schema={
        "records": int,
        "resolution": int,
        "count_historical_data": int,
        "count_current_data": int,
        "db_rows": int,
    },
)

VIS_GEN = Event(name="Generate Visualization", schema={"filename": str})

DISPLAY_UPDATE = Event(name="Update Display", schema={})
