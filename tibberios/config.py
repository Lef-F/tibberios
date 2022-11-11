from .core import DbTable

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

UPDATES_TBL = DbTable(
    name="updates",
    columns={
        "start_time": "DATE PRIMARY KEY",
        "end_time": "DATE",
        "requested_records": "REAL",
        "requested_resolution": "TEXT",
        "received_records": "REAL",
        "received_future_records": "REAL",
    },
    pk="start_time",
)

DISPLAY_TBL = DbTable(
    name="display",
    columns={
        "start_time": "DATE PRIMARY KEY",
        "end_time": "DATE",
        "event": "TEXT",
    },
    pk="start_time",
)
