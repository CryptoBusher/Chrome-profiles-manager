# 🗂️ Chrome profiles manager

В последнее время **взломы антидетект-браузеров** стали происходить с пугающей регулярностью. Многие криптаны **осознали риски** и приняли решение отказаться от подобных инструментов, особенно когда речь идет о **хранении и управлении средствами**.

Я, как и многие здравомыслящие коллеги, полностью переношу ончейн-активности в **профили Chrome**.
Это решение, скорее всего, будет несовместимо с аккаунтами социальных сетей, но для большинства ончейн операций оно **более, чем оправдано**.  

> безопасность > удобство

🚀 Канал с разъебами: [@CryptoKiddiesClub](https://t.me/CryptoKiddiesClub)  
💬 Чат для комьюнити: [@CryptoKiddiesChat](https://t.me/CryptoKiddiesChat)  
🔥 Связь с создателем: [@CryptoBusher](https://t.me/CryptoBusher)

<p>
  <img src="assets/demo.gif" width="400" alt="Демонстрация работыF" style="border: 1px solid #ccc; border-radius: 5px;">
</p>

## ⌛ Роадмап
- [x] Headless mode
- [x] Скрипт для импорта EVM кошелька в Rabby Wallet
- [x] Удаление кеша расширений при их замене или снесении
- [ ] Почему пропадают некоторые расширения?
- [ ] Почему Oxy Proxy не пробрасывает авторизацию прокси?
- [ ] Убивать драйвер даже в случае неожиданной ошибки
- [ ] Фикс бага с переименованием профиля
- [ ] Интегрировать команду _chmod +x chromedriver_ - для маководов
- [ ] Гайд для интеграции собственных chrome / manager скриптов
- [ ] Многопоточное выполнение скриптов на selenium
- [ ] Скрипт для импорта SOL кошелька в Phantom Wallet

## 🎯 **Описание меню**

    -> ГЛАВНОЕ МЕНЮ <-
    🚀 запуск профилей                  открывает ранее созданные профиля Chrome
    📖 просмотр профилей                отображение списка всех профилей и ранее заданные комментарии к ним
    📝 задать комментарии               присвоение профилям комментариев для дальнейшего удобного запуска
    🤖 прогон скриптов [chrome]         выполнение скриптов, реализованных на selenium
    🤖 прогон скриптов [manager]        выполнение скриптов, не связанных с web-автоматизацией
    🧩 работа с расширениями            добавление и удаление расширений
    ➕ создание профилей                создание новых профилей
    💀 убить процессы Chrome            завершить все запущенные процессы Chrome
    🚪 выход                            завершение работы программы

    -> ВЫБОР АККАУНТОВ <-
    📋 выбрать из списка                ручной выбор из всего списка
    📝 вписать названия                 выбор путем перечисления названий профилей через запятую
    📒 выбрать по комментарию           выбор путем указания подстроки комментария к профилю
    📦 выбрать все                      выбрать все профиля
    🏠 назад в меню                     вернуться в главное меню

    -> РАБОТА С РАСШИРЕНИЯМИ <-
    🟢 добавить дефолтные без замены    добавить дефолтные расширения без замены уже имеющихся
    🔴 добавить дефолтные с заменой     добавить дефолтные расширения с заменой уже имеющихся
    ❌ удалить расширения               удалить расширения и их кеш
    🏠 назад в меню                     вернуться в главное меню

    -> СОЗДАНИЕ ПРОФИЛЕЙ <-
    📝 задать вручную                   указать названия аккаунтов через запятую
    🤖 задать автоматически             для имен используется нумерация, начиная с уже имеющегося наивысшего номера
    🏠 назад в меню                     вернуться в главное меню

## 🔋 Батарейки в комплекте
### Selenium скрипты
- Первичная настройка Chrome
- Настройка Omega Proxy
- Настройка Agent Switcher
- Импорт Rabby Wallet

## ⚙️ Как подтягивать обновления
Для подтягивания обнов необходимо клонировать репозиторий на ваш ПК (а не качать архивом). Вам понадобится [GIT](https://git-scm.com/), но это того стоит.
```
git clone https://github.com/CryptoBusher/Chrome-profiles-manager.git
```

После клонирования у вас появится папка с проектом, переходим в нее и производим настройки софта согласно инструкции в "Первый запуск". Для подтягивания обновлений, находясь в папке проекта, вписываем в терминале команду:
```
git pull
```

## 📚 Первый запуск
1. Устанавливаем [Python 3.12](https://www.python.org/downloads/).
2. Скачиваем проект, в терминале, находясь в папке проекта, вписываем команду ```pip install -r requirements.txt``` для установки всех зависимостей.
3. Переименовываем папку "data.example" в "data".
   1. ```не обязательно``` Добавляем нужные нам расширения распакованные в папку "data/default_extensions". Можно создать пустой профиль, установить на него расширение и скопировать его в эту общую папку (в таком случае установленное на профиль расширение надо искать в директории "data/profiles/Profile 1/Extensions" (если профиль мы назвали "1")). Распакованное расширение выглядит как папка, имеющая название наподобие "acmacodkjbdgmoleebolmdjonilkdbch", эту папку и нужно искать.
   2. ```не обязательно``` Настраиваем конфигурационные файлы для каждого интересующего нас скрипта в папках "data/scripts/chrome" и "data/scripts/manager". Подробности по каждому отдельному скрипту читать в README.md для этих скриптов.
   3. ⚠️ Файл "data/comments_for_profiles.json" не трогаем, он будет заполняться через CLI.
4. ```не обязательно``` Если хотим использовать "прогон скриптов [chrome]" (то есть автоматизацию с помощью selenium) - необходимо скачать chromedriver для вашей операционной системы и конкретной версии Chrome. Версию Chrome можно посмотреть, вбив в поисковую строку "chrome://version/" (например: Google Chrome	**132**.0.6834.111). Скачать chromedriver можно [тут](https://googlechromelabs.github.io/chrome-for-testing/). Нас интересует совпадение первого числа в версии, если не нашли - можно поискать по [запросу](https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json). Нужен не chrome а именно **chromedriver**. После скачивания необходимо извлечь из архива файл "chromedriver.exe" (или "chromedriver" для macOS) и поместить в папку "src/chrome/scripts". 
5. ```не обязательно``` Настраиваем файл "config.py".
6. В терминале, находясь в папке проекта, вписываем команду ```python3 main.py``` и жмем ENTER.
7. На Windows можно сделать ярлык файла "start.bat", переименовать его и переместить в удобное место, через двойной клик по ярлыку будет запускаться программа в новом терминале.

## 🌵 Дополнительная информация
- Программа работает на Windows и macOS.
- Для корректной работы selenium скриптов лучше постараться изолироваться от чрезмерного спама "welcome" страниц от ненастроенных расширений.
- Если при прогоне chrome скриптов драйверу не удается подключиться к профилю браузера - возможно, надо перезапустить скрипт, перед этим закрыв все окна Google Chrome.
- Я, пока что, не придумал, как управлять профилями через debug port в многопотоке. Если ты такое делал - буду рад совету.
- На написание скрипта меня вдохновила [статья](https://teletype.in/@trupimnepout/GOOGLE_CHROME_GUIDE) от админа [@k1r0shi_DAO](https://t.me/k1r0shi_DAO). Я реализовал базовых набор функционала, но над структурой заморочился для расширяемости. Буду рад рекомендациям по улучшению user experience и расширению функционала.

## 💴 Донат
Поддержи мой канал донатом в любой EVM сети
<b>0x77777777323736d17883eac36d822d578d0ecc80</b>



