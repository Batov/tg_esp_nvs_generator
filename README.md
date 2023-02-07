# tg_esp_nvs_generator
Telegram bot for nvs.bin generation 

## Link
https://t.me/nvs_generator_bot

## Env
* TG_BOT_TOKEN - telegram token from BotFather;
* ENV_MOECO_CERT - proprietary certificate for in-place replacement file type;

## Setup
```
docker build .
docker run -e TG_BOT_TOKEN="<telegram bot token>" <container>
```

## Test wrapper
```
python -m wrapper.wrapper
```
