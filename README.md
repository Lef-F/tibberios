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

---

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

---

## Deploying 🚀

Currently the deployment is managed manually:

1. `git clone` this repository into your remote machine
2. Create a cronjob in `crontab -e` by adding your own modified version the following command combo:

```shell
# Tibber update data
*/10 * * * * ( . /home/pi/.cache/pypoetry/virtualenvs/tibberios-someRandomThingsHere-py3.10/bin/activate && tibberios --records 100 --verbose --config-path /home/pi/tibberios/config.json >> /home/pi/tibberios/run.log 2>&1 )
```

In my case, I have setup Grafana to be able to read local files in the `/opt/grafana/` path in my Raspberry Pi.
Thus, I store and run my `sqlite` databases there and Grafana operates them from there using this [Grafana plugin](https://github.com/fr-ser/grafana-sqlite-datasource).

By trial and error I found `--records 100` to work great for backfilling consumption and cost data, if you don't have access to real-time Tibber data.

---

## Visualize your data 📊

### Grafana 📈

SQLite + self-hosted Grafana = ❤️

I'm hosting a Grafana instance in my Raspberry Pi to monitor a bunch of things, which is great because by running `Tibberios` on the same machine allows us to query the resulting tables in `Tibberios`'s SQLite database.

[For more read the `Tibberios` docs on Grafana and check out the Grafana dashboard JSON models.](grafana/README.md)

### e-Paper Display 📜

As much as I enjoy these electricity management apps, I have noticed that they introduce some new limitations to my life:

- I am the only person in the family with access to the current and future electricity price
- I have to check my phone every time

As such, I came up with a fun project idea:
Hook-up an e-Paper Display to my Raspberry Pi and show the current and future prices for all in an accessible location at home! 🤯

So after a bunch of research I ordered the [Waveshare 7.5 Inch E-Paper Display](https://www.waveshare.com/7.5inch-e-paper-hat.htm) which comes with a HAT for Raspberry Pi.
The reasons being:

- It seems quite popular on Amazon and the price was fine.
- There is a few GitHub repositories with support for it, and [from Waveshare themselves](https://github.com/waveshare/e-Paper)
- The size is just right, not too large not too small (lagom as they say in swedish 🇸🇪)

#### So here's a first demo of how it looks like

Here you can see a sample of the graph rendered by `plotly`:

![Hourly Electricity Data](docs/img/electricity_prices.png)

And here you can see how the same picture looks like when printed on the e-paper display:

![e-Paper Display showing electricity data](docs/img/e-paper-electricity-prices.jpeg)

Don't worry about it being so naked, I have ordered [a case for it from Waveshare](https://www.waveshare.com/7.5inch-e-paper-case.htm) as a development enclosure and will likely move to a nice looking frame for the production environment. 🏡

**Note:** *This project is currently in progress, come back for updates. 🕺*

---

## Further reading

- [Tibber Dev Docs](https://developer.tibber.com/)
- [pyTibber](https://github.com/Danielhiversen/pyTibber)
- [Grafana](https://grafana.com/docs/grafana/latest/)
- [Grafana SQLite data source plugin](https://github.com/fr-ser/grafana-sqlite-datasource)
- [Waveshare eShop](https://www.waveshare.com/)
- [Waveshare on GitHub](https://github.com/waveshare)

---

## Referral copy/pasted from my Tibber App

Hey! 🤗 Here’s a tip! You can save money, save the environment, and avoid unnecessary energy consumption at the same time. How? With Tibber’s hourly energy prices, I can easily move my consumption to the cheapest hours, and avoid expensive hours. Try it out, and we’ll both get 500 kr as a bonus to use in the Tibber Store. ⚡ [Read more here](https://invite.tibber.com/o10520f3)
