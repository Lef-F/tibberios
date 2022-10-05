from dataclasses import dataclass
from datetime import date, datetime
from pprint import pprint
from typing import Iterable

import tibber
from aiohttp import ClientSession


@dataclass
class Config:
    filepath: str  # Path to configuration file

    def __post_init__(self) -> None:
        from json import load

        # TODO: Allow for fetching from environment variables
        with open(self.filepath, "r") as f:
            self.config = load(f)
        self.tibber_api_key = self.config["TIBBER_API_KEY"]
        self.database_path = self.config["DATABASE_PATH"]


@dataclass
class History:
    data: Iterable  # Historical tibber API data

    def values(self) -> Iterable[tuple]:
        return [tuple(row.values()) for row in self.data]


class TibberConnector:
    def __init__(self, tibber_api_key: str) -> None:
        self._access_token = tibber_api_key

    async def get_history(self, resolution: str, records: int) -> Iterable[dict]:
        # TODO: Allow for multiple homes
        async with ClientSession() as session:
            tibber_connection = tibber.Tibber(self._access_token, websession=session)
            await tibber_connection.update_info()
            home = tibber_connection.get_homes()[0]

            self.history = await home.get_historic_data(
                n_data=records,
                resolution=resolution,
            )

            # home.current_price_data()
        print(f"Got {len(self.history)} records with resolution: {resolution}")
        return self.history


class Database:
    def __init__(self, filename: str) -> None:
        from sqlite3 import connect

        self._database_path = filename
        self.connection = connect(database=self._database_path)

    def __del__(self) -> None:
        self.close()

    def create_table(self) -> None:
        # TODO: Make generic
        query = """
            CREATE TABLE IF NOT EXISTS consumption(
                start_time DATE PRIMARY KEY,
                unit_price REAL,
                total_cost REAL,
                cost REAL,
                consumption REAL
            );
        """
        cursor = self.connection
        cursor = cursor.execute(query)
        self.connection.commit()

    def show_latest_data(self, limit: int = 10) -> None:
        # TODO: Make generic
        query = f"""
            SELECT *
            FROM consumption
            ORDER BY start_time DESC
            LIMIT {limit};
        """
        cursor = self.connection
        cursor = cursor.execute(query)
        pprint(cursor.fetchall())

    def upsert_table(self, values: Iterable[tuple]) -> None:
        # TODO: Make generic
        query = """
            INSERT INTO consumption(
                start_time
                , unit_price
                , total_cost
                , cost
                , consumption
            )
            VALUES(?, ?, ?, ?, ?)
            ON CONFLICT(start_time) DO UPDATE SET
                unit_price = excluded.unit_price
                , total_cost = excluded.total_cost
                , cost = excluded.cost
                , consumption = excluded.consumption;
        """

        cursor = self.connection
        cursor.executemany(query, values)
        self.connection.commit()

    def delete_null_rows(self) -> None:
        # TODO: Make generic
        query = """
            DELETE
            FROM consumption
            WHERE start_time IS NULL
                OR trim(start_time) = '';
        """
        cursor = self.connection
        cursor.execute(query)
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()
