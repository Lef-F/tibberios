from .core import Config, Database, TibberConnector, History
from datetime import datetime


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

    print(f"Starting at {datetime.now().isoformat()}")
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
    print(f"Ended at {datetime.now().isoformat()}")


def run() -> None:
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
        default=path.normpath(
            path.join(
                getcwd(),
                "..",
                "tibber.db",
            ),
        ),
    )
    parser.add_argument(
        "--config-path",
        type=str,
        required=False,
        help="The path to the JSON configuration file for Tibberios",
        default=path.normpath(
            path.join(
                getcwd(),
                "..",
                "config.json",
            ),
        ),
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
