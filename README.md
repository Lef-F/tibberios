# Tibberios 🏛

The Greek is playing around with Tibber.

Store, update and visualize your own Tibber data from your own `sqlite` database.

[Click here to get your own Tibber invite from your fellow Greek μαλάκα!](https://invite.tibber.com/o10520f3)

## But why? 👀

I really wanted to store some of my Tibber data in a database I control to achieve the following goals:

- Keep a copy of my long-term history of hourly consumption handy
- Allow me to perform all sorts of neat analytical SQL queries on it
- Allow me to visualize it in my own tools of preference e.g. Grafana
- Use it in my own application e.g. e-paper display that shows a graph of today's (and tomorrow, once available) spot prices

## Setup 🛠

First setup your environment using: `poetry install --only main` or `pip install -r requirements.txt`.

You need the following `config.json` file in your project root:

```json
{
    "TIBBER_API_KEY": "some_gsdgri_strange_r3f4ww_looking_f43erke_key_from_tibber_dev",
    "DATABASE_PATH": "/some/path/tibber.db",
}
```

Get your [Tibber API key](https://developer.tibber.com/).

## Run 🏃‍♀️

(Hopefully) you will find all you need in the attached Python help:

If you installed with `poetry`, activate the virtual environment for `tibberios` and run:

```shell
tibberios --help
```

Else, if you installed with `pip` then you can use the provided `run.py` script:

```shell
python run.py --help
```

### Get your consumption data and store them in a `sqlite` database file

The following will get you the latest 1000 hours of your data:

```shell
tibberios --resolution HOURLY --records 1000
```

I recommend you run with a lot of records the first time, in order to populate your past data.
Then you can run every hour and update the last ~48 records, or less if you have a live electricity meter.
In my case (not live) the consumption data appears with 1-2 days of delay, thus I need to re-fetch the past data in order to keep everything updated.

## Deploying

Currently the deployment is managed manually:

1. `git clone` this repository into your remote machine
2. Create a cronjob in `crontab -e` by adding your own modified version the following command combo:

```shell
# Tibber update data
*/10 * * * * ( . /home/pi/.cache/pypoetry/virtualenvs/tibberios-someRandomThingsHere-py3.10/bin/activate && tibberios --verbose --config-path /home/pi/tibberios/config.json >> /home/pi/tibberios/run.log 2>&1 )
```

In my case, I have setup Grafana to be able to read local files in the `/opt/grafana/` path in my Raspberry Pi.
Thus, I store and run my `sqlite` databases there and Grafana operates them from there using this [Grafana plugin](https://github.com/fr-ser/grafana-sqlite-datasource).

## Further reading

- [Tibber Dev Docs](https://developer.tibber.com/)
- [pyTibber](https://github.com/Danielhiversen/pyTibber)
- [Grafana](https://grafana.com/docs/grafana/latest/)
- [Grafana SQLite data source plugin](https://github.com/fr-ser/grafana-sqlite-datasource)

## Referral copy/pasted from my Tibber App

Hey! 🤗 Here’s a tip! You can save money, save the environment, and avoid unnecessary energy consumption at the same time. How? With Tibber’s hourly energy prices, I can easily move my consumption to the cheapest hours, and avoid expensive hours. Try it out, and we’ll both get 500 kr as a bonus to use in the Tibber Store. ⚡ [Read more here](https://invite.tibber.com/o10520f3)
