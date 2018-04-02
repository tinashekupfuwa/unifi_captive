# App deployment

### Disclaimer: Я не настоящий DevOps, да даже и не знаком ни с одним из них. Так что на зрелость подхода не претендую

#### 1. Установка необходимых пакетов
Приложение публикуется с помощью web-сервера **apache2** и модуля **wsgi** для python3
Вероятно **apache2** уже есть в системе, а вот модуля **wsgi** может и не быть. В любом случае следующая команда инсталирует и то и другое. Заодно установим **git** и модуль **venv** для **python3**:  
```
root@aws-ryzhkov2:# apt install apache2 libapache2-mod-wsgi-py3 git python3-venv
```

#### 2. Установка приложения, виртуального окружения и зависимостей
Для простоты и удобства разместим наше приложение в папке */var/www/FLASKAPP*
Доступ в эту папку требует root-овых привелегий, но как говорится для поиграться и так сойдет


Клонируем код из GIT репозитария в заданную директорию (captive) и сразу в нее проваливаемся:
```
root@aws-ryzhkov2:# mkdir -p /var/www/FLASKAPP
root@aws-ryzhkov2:# cd !$
root@aws-ryzhkov2:/var/www/FLASKAPP# git clone http://zabbix.msk.vbrr.loc:3000/nryzhkov/unifi_captive.git captive && cd captive
Cloning into 'captive'...
remote: Counting objects: 85, done.
remote: Compressing objects: 100% (82/82), done.
remote: Total 85 (delta 26), reused 0 (delta 0)
Unpacking objects: 100% (85/85), done.
Checking connectivity... done.

```

Разворачиваем виртуальное окружение **venv**
```
root@aws-ryzhkov2:/var/www/FLASKAPP/captive# python3 -m venv venv
```

Активируем виртуальное окружение:
```
root@aws-ryzhkov2:/var/www/FLASKAPP/captive# source venv/bin/activate
(venv) root@aws-ryzhkov2:/var/www/FLASKAPP/captive#
```

Устанавливаем все пакеты необходимые для нашего приложения
(пакеты перечислены в переменной *install_requires* в **setup.py**)
```
(venv) root@aws-ryzhkov2:/var/www/FLASKAPP/captive# pip install -e .
Obtaining file:///var/www/FLASKAPP/captive
Collecting alembic (from captive-protal===0.1)
Collecting Flask (from captive-protal===0.1)
  Downloading Flask-0.12.2-py2.py3-none-any.whl (83kB)
    100% |████████████████████████████████| 92kB 710kB/s 
Collecting Flask-Login (from captive-protal===0.1)
Collecting Flask-Migrate (from captive-protal===0.1)
  Using cached Flask_Migrate-2.1.1-py2.py3-none-any.whl
Collecting Flask-SQLAlchemy (from captive-protal===0.1)
  Using cached Flask_SQLAlchemy-2.3.2-py2.py3-none-any.whl
Collecting Flask-WTF (from captive-protal===0.1)
  Using cached Flask_WTF-0.14.2-py2.py3-none-any.whl
Collecting Jinja2 (from captive-protal===0.1)
  Downloading Jinja2-2.10-py2.py3-none-any.whl (126kB)
    100% |████████████████████████████████| 133kB 1.6MB/s 
Collecting Mako (from captive-protal===0.1)
  Downloading Mako-1.0.7.tar.gz (564kB)
    100% |████████████████████████████████| 573kB 1.6MB/s 
Collecting pyunifi (from captive-protal===0.1)
Collecting requests (from captive-protal===0.1)
  Downloading requests-2.18.4-py2.py3-none-any.whl (88kB)
    100% |████████████████████████████████| 92kB 1.4MB/s 
Collecting SQLAlchemy (from captive-protal===0.1)
Collecting urllib3 (from captive-protal===0.1)
  Downloading urllib3-1.22-py2.py3-none-any.whl (132kB)
    100% |████████████████████████████████| 133kB 885kB/s 
Collecting Werkzeug (from captive-protal===0.1)
  Downloading Werkzeug-0.14.1-py2.py3-none-any.whl (322kB)
    100% |████████████████████████████████| 327kB 639kB/s 
    
    ...................
    
Successfully installed Flask-0.12.2 Flask-Login-0.4.1 Flask-Migrate-2.1.1 Flask-SQLAlchemy-2.3.2 Flask-WTF-0.14.2 Jinja2-2.10 Mako-1.0.7 MarkupSafe-1.0 SQLAlchemy-1.2.5 WTForms-2.1 Werkzeug-0.14.1 alembic-0.9.9 captive-protal certifi-2018.1.18 chardet-3.0.4 click-6.7 idna-2.6 itsdangerous-0.24 python-dateutil-2.7.0 python-editor-1.0.3 pyunifi-2.13 requests-2.18.4 six-1.11.0 urllib3-1.22
```
Во время инсталяции пакетов получим несколько сообщений: 
> Failed building wheel for MarkupSafe  
Честно, не знаю что это значит, но работе приложения это не мешает.

Библиотека python-smpplib отсутствует в репозиториях PIP, поэтому ставим отдельно с github-а

```
(venv) root@aws-ryzhkov2:/var/www/FLASKAPP/captive# pip install git+https://github.com/podshumok/python-smpplib.git
Collecting git+https://github.com/podshumok/python-smpplib.git
  Cloning https://github.com/podshumok/python-smpplib.git to /tmp/pip-tkhjpgrb-build
Requirement already satisfied (use --upgrade to upgrade): six in ./venv/lib/python3.5/site-packages (from python-smpplib===1.0.1)
Installing collected packages: python-smpplib
  Running setup.py install for python-smpplib ... done
Successfully installed python-smpplib-1.0.1
```
#### 3. Инициализация БД
Далее нужно инициализировать базу данных SQLite
```
(venv) ✔ ~/python/flask/captive [master|✚ 2] 
17:19 $ export FLASK_APP=captive/__init__.py
(venv) ✔ ~/python/flask/captive [master|✚ 2] 
17:19 $ flask db init
  Creating directory /home/nryzhkov/python/flask/captive/migrations ... done
  Creating directory /home/nryzhkov/python/flask/captive/migrations/versions ... done
  Generating /home/nryzhkov/python/flask/captive/migrations/script.py.mako ... done
  Generating /home/nryzhkov/python/flask/captive/migrations/README ... done
  Generating /home/nryzhkov/python/flask/captive/migrations/alembic.ini ... done
  Generating /home/nryzhkov/python/flask/captive/migrations/env.py ... done
  Please edit configuration/connection/logging settings in '/home/nryzhkov/python/flask/captive/migrations/alembic.ini' before proceeding.
(venv) ✔ ~/python/flask/captive [master|✚ 2…4]  
17:20 $ flask db migrate
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'user'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_user_mac' on '['mac']'
INFO  [alembic.autogenerate.compare] Detected added table 'auth'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_auth_timestamp' on '['timestamp']'
  Generating /home/nryzhkov/python/flask/captive/migrations/versions/920de77b9b2e_.py ... done
(venv) ✔ ~/python/flask/captive [master|✚ 3…5] 
17:20 $ flask db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 920de77b9b2e, empty message
```
если при миграции лезут ошибки - достаточно грохнуть старую базу данных *captive/app.db*

#### 4. Пробный запуск приложения
Теперь пора запустить приложение и убелиться, что приложение развернуто правильно и все зависимости соблюдены

```
(venv) root@aws-ryzhkov2:/var/www/FLASKAPP/captive# flask run
 * Serving Flask app "captive"
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

#### 5. Настройка apache2 и мод WSGI

Пора научить apache2 запускать наше приложение. Для этого используется модуль **wsgi**  
Конфигурация для этого модуля находится в файле captive-apache.conf
Скопируем этот файл в /etc/apache2/sites-enabled а так же сделаем наш сайт сайтом по умолчанию.
Дак же необходимо активировать модуль **wsgi**

```
(venv) root@aws-ryzhkov2:/var/www/FLASKAPP/captive# cp captive-apache.conf /etc/apache2/sites-enabled/

(venv) root@aws-ryzhkov2:/var/www/FLASKAPP/captive# a2dissite 000-default
Site 000-default disabled.
To activate the new configuration, you need to run:
  service apache2 reload
  
(venv) root@aws-ryzhkov2:/var/www/FLASKAPP/captive# a2ensite captive-apache
Enabling site captive-apache.
To activate the new configuration, you need to run:
  service apache2 reload

(venv) root@aws-ryzhkov2:/var/www/FLASKAPP/captive# a2enmod wsgi
Enabling module wsgi.
To activate the new configuration, you need to run:
  service apache2 restart

(venv) root@aws-ryzhkov2:/var/www/FLASKAPP/captive# service apache2 restart
```

Готово! Наше приложение должно заработать на 80-м порту
