[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Twitch Integration with Factorio and useful book [PUBTwitchFactorio]

Allows you to print Twitch messages in Factorio and send custom commands in Factorio, customizing them via [Useful book][Useful book]. Fully customizable.

(Perhaps, I'm not going to develop it because there are issues with Python and TwitchIO etc. Also, I don't have enough followers etc. on Twitch to test some stuff like "rewards for points" etc.)
(It might work not so stable on Windows sometimes)

## 🏁 Getting Started
It is assumed that you have:
- [**Useful book**][Useful book] - Factorio mod on the server
- [**Factorio**](https://www.factorio.com/download) or its headless server
- [**Twitch**](https://twitch.tv/) account for your bot
- [**Python 3.10**](https://www.python.org/) installed. (I didn't test it on any other version)
- [**Pip**](https://pip.pypa.io/en/stable/) installed

```bash
python --version
pip --version
```

## How to setup

* After clone this repo, rename `config-example.toml` to `config.toml` and `UB_data-example.csv` to `UB_data.csv` in configs directory. Open and change `config.toml`.
* Change `UB_data.csv` and check/add your scripts in [Useful book][Useful book].

### Changing Factorio RCON settings to host the server locally

If you are hosting the game locally, instead of a dedicated server then follow these instruction.
Otherwise if you already have a dedicated server, look up how to enable the RCON interface with a particular port and password.

1. On the main menu screen, hold Ctrl+Alt and then left click "Settings"
2. Now select the last item "The rest".
3. By `local-rcon-socket`, enter `127.0.0.1:25575`
4. By `local-rcon-password`, enter `my_password` (or any secret password, the same one as in config.toml)
5. Then click confirm, and go back to the main menu.
6. Click Multiplayer -> Host a save game
7. Select the game you want to host.
8. Click Play

### Generate client ID

For the bot, you may want to create a separate twitch account (alternatively you can just use your current twitch account).
Note: you'll need Two-Factor Authentication (2FA) enabled for this step.

Go to https://dev.twitch.tv/ and login with this twitch account. Then click `Your Console`->`Register Your Application`.
Fill in the fields:

 * name: `FactorioChatBot`
 * OAuth Redirect URLs: `https://twitchapps.com/tokengen/`
 * Category: `Chat Bot`

Complete the reCAPTCHA and click `save` at the bottom.
Copy the Client ID and paste it into `config.toml`.


### ▶️ Run

You can create "Virtual Environment"s to keep libraries from polluting system installs or to help maintain a different version of libraries than the ones installed on the system.

Execute the following commands in the main directory:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

After that you'll need this to run the bot within the directory:
```bash
source venv/bin/activate
python main.py
```

[Useful book]: https://mods.factorio.com/mod/useful_book