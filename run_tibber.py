#!/bin/python3
from dataclasses import dataclass
from typing import Iterable

import tibber
from aiohttp import ClientSession

from pprint import pprint


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


async def main(
    db_path: str,
    config_path: str,
    resolution: str,
    records: int,
    verbose: bool,
) -> None:
    config = Config(filepath=config_path)

    if db_path:
        pass
    else:
        db_path = config.database_path

    if verbose:
        print(f"The database path is: {db_path}")
        print(f"The config path is: {config_path}")
        print(f"Fetching {records} in {resolution} resolution")

    db = Database(db_path)
    tib = TibberConnector(config.tibber_api_key)
    history = await tib.get_history(resolution=resolution, records=records)
    data = History(data=history)

    db.create_table()
    if verbose:
        print("Consumption table created")
    db.upsert_table(values=data.values())
    if verbose:
        print("Cleaning rows with NULL or empty time values")
    db.delete_null_rows()
    if verbose:
        print("Consumption values upserted")
        print("Latest 10 consumption values:")
        db.show_latest_data()
    db.close()


if __name__ == "__main__":
    from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
    from asyncio import new_event_loop
    from os import getcwd, path
    from sys import exit

    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--db-path",
        type=str,
        required=False,
        help="The path where the SQLite database file is/will be stored. Can be set in DATABASE_PATH key in your config file.",
        default=path.join(getcwd(), "tibber.db"),
    )
    parser.add_argument(
        "--config-path",
        type=str,
        required=False,
        help="The path to the JSON configuration file for Tibberios",
        default=path.join(getcwd(), "config.json"),
    )
    parser.add_argument(
        "--resolution",
        type=str,
        required=False,
        default="HOURLY",
        help="The resolution to fetch records from the Tibber API. (HOURLY, DAILY, WEEKLY, MONTHLY)",
    )
    parser.add_argument(
        "--records",
        type=int,
        required=False,
        default=24 * 2,
        help="The number of latest records to fetch from now to the past from the Tibber API.",
    )
    parser.add_argument(
        "--verbose",
        required=False,
        default=False,
        action="store_true",
        help="Show more information from the process.",
    )
    args = parser.parse_args()

    loop = new_event_loop()
    loop.run_until_complete(
        main(
            db_path=args.db_path,
            config_path=args.config_path,
            resolution=args.resolution,
            records=args.records,
            verbose=args.verbose,
        )
    )
    loop.close()
    exit(0)
