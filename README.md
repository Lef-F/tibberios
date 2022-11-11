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

### Setup the Python environment

First setup your environment using: `poetry install`

For ARM devices (Raspberry Pi 4 tested) we provide the [`Makefile`](/Makefile) target `rpi-setup` which you can execute with `make rpi-setup`.

**Note:** For ARM devices (e.g. Raspberry Pi) we provide [`requirements_rpi.txt`](/requirements_rpi.txt).
After the introduction of the [`kaleido`](https://github.com/plotly/Kaleido) Python package we've had some issues setting up the Python environment for ARM devices due to them having split up the support into a new version `0.2.1.post1` for some reason. 🤷‍♂️
Maybe we'll get something from [this GitHub issue](https://github.com/plotly/Kaleido/issues/151).
In the future we will have to move away from `plotly` since it can only use the `kaleido` engine for exporting plots to static files [and it looks under-maintained](https://github.com/plotly/Kaleido/issues/150).
We haven't tested [`orca`](https://github.com/plotly/orca) but it looks outdated.

It is recommended that you use a virtual environment for the best results.
`poetry install` will already create one for you which you can activate with `poetry shell`.
If you're going the `pip` way then you can:

- `make rpi-setup`
- or `make py-setup`

Or if you wanna do it yourself:

1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r the_requirements_file_that_fits_you.txt`

### Create your `config.json` file

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

Else, if you installed with `pip` then you can use the provided [`run`](/run) script:

```shell
./run --help
```

### Get your consumption data and store them in a `sqlite` database file

The following will get you the latest 1000 hours of your data:

```shell
tibberios --config-path config.json --resolution HOURLY --records 1000
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

#### To generate a new image visualization

Run something like the following:

```shell
tibberios --config-path config.json vis electricity_prices.png
```

#### To update your `epd7in5_V2` Waveshare e-Paper Display

You can run something like the following:

```shell
tibberios --config-path config.json display electricity_prices.png
```

**Note 1:** Currently only the `epd7in5_V2` is supported.
Unsure if it would make sense to support smaller display sizes at the moment, since the text won't be legible.
Maybe the way forward is to have an API to allow folks to setup Tibberios for their own displays.
Raise a GitHub Issue or create a Pull Request if you have some good ideas. ❤️

**Note 2:** Yes, it is a bit against intuition to have to run a Tibber API update in order to visualize future data or update your display.
It will be solved when we implement something like subcommands with [`click`](https://click.palletsprojects.com/en/8.1.x/).

---

#### So here's a first demo of how it looks like

Here you can see a sample of the graph rendered by `plotly`:

![Hourly Electricity Data](docs/img/electricity_prices.png)

And here you can see how the same picture looks like when printed on the e-paper display:

![e-Paper Display showing electricity data](docs/img/e-paper-electricity-prices.jpeg)

Don't worry about it being so naked, I have ordered [a case for it from Waveshare](https://www.waveshare.com/7.5inch-e-paper-case.htm) as a development enclosure and will likely move to a nice looking frame for the production environment. 🏡

**Note 1:** *This project is currently in progress, come back for updates. 🕺*

**Note 2:** *The "cost of a shower" price analogy was copied from [duscha.nu](http://www.duscha.nu/). 😊*

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
