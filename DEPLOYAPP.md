# App deployment

### Disclaimer: Я не настоящий DevOps, да даже и не знаком ни с одним из них. Так что на зрелость подхода не претендую

## Установка приложения

#### 1. Установка необходимых пакетов
Приложение публикуется с помощью web-сервера **apache2** и модуля **wsgi** для python3
Вероятно **apache2** уже есть в системе, а вот модуля **wsgi** может и не быть. В любом случае следующая команда инсталирует и то и другое. Заодно установим **git** и модуль **venv** для **python3**:  
```
root@wlc-server:# apt install apache2 libapache2-mod-wsgi-py3 git python3-venv
```

#### 2. Установка приложения, виртуального окружения и зависимостей
Для простоты и удобства разместим наше приложение в папке */var/www/FLASKAPP*
Доступ в эту папку требует root-овых привелегий, но как говорится для поиграться и так сойдет


Клонируем код из GIT репозитария в заданную директорию (captive) и сразу в нее проваливаемся:
```
root@wlc-server:# mkdir -p /var/www/FLASKAPP
root@wlc-server:# cd !$
root@wlc-server:/var/www/FLASKAPP# git clone http://zabbix.msk.vbrr.loc:3000/idqdd/unifi_captive.git captive && cd captive
Cloning into 'captive'...
remote: Counting objects: 85, done.
remote: Compressing objects: 100% (82/82), done.
remote: Total 85 (delta 26), reused 0 (delta 0)
Unpacking objects: 100% (85/85), done.
Checking connectivity... done.

```

Разворачиваем виртуальное окружение **venv**
```
root@wlc-server:/var/www/FLASKAPP/captive# python3 -m venv venv
```

Активируем виртуальное окружение:
```
root@wlc-server:/var/www/FLASKAPP/captive# source venv/bin/activate
(venv) root@wlc-server:/var/www/FLASKAPP/captive#
```

Устанавливаем все пакеты необходимые для нашего приложения
(пакеты перечислены в переменной *install_requires* в **setup.py**)
```
(venv) root@wlc-server:/var/www/FLASKAPP/captive# pip install -e .
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
(venv) root@wlc-server:/var/www/FLASKAPP/captive# pip install git+https://github.com/podshumok/python-smpplib.git
Collecting git+https://github.com/podshumok/python-smpplib.git
  Cloning https://github.com/podshumok/python-smpplib.git to /tmp/pip-tkhjpgrb-build
Requirement already satisfied (use --upgrade to upgrade): six in ./venv/lib/python3.5/site-packages (from python-smpplib===1.0.1)
Installing collected packages: python-smpplib
  Running setup.py install for python-smpplib ... done
Successfully installed python-smpplib-1.0.1
```
#### 3. Инициализация БД
В тестовых целях можно воспользоваться базой из репозитория  
Но в любом случае необходимо дать права для процесса *apache2* на изменение *файла captive/app.db*

Инициализировать базу данных SQLite следующим образом:

```
(venv) root@wlc-server:/var/www/FLASKAPP/captive# rm -rf migrations captive/app.db
(venv) root@wlc-server:/var/www/FLASKAPP/captive# export FLASK_APP=captive/__init__.py
(venv) root@wlc-server:/var/www/FLASKAPP/captive# flask db init
  Creating directory /home/idqdd/python/flask/captive/migrations ... done
  Creating directory /home/idqdd/python/flask/captive/migrations/versions ... done
  Generating /home/idqdd/python/flask/captive/migrations/script.py.mako ... done
  Generating /home/idqdd/python/flask/captive/migrations/README ... done
  Generating /home/idqdd/python/flask/captive/migrations/alembic.ini ... done
  Generating /home/idqdd/python/flask/captive/migrations/env.py ... done
  Please edit configuration/connection/logging settings in '/home/idqdd/python/flask/captive/migrations/alembic.ini' before proceeding.
  
(venv) root@wlc-server:/var/www/FLASKAPP/captive# flask db migrate
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'user'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_user_mac' on '['mac']'
INFO  [alembic.autogenerate.compare] Detected added table 'auth'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_auth_timestamp' on '['timestamp']'
  Generating /home/idqdd/python/flask/captive/migrations/versions/920de77b9b2e_.py ... done
  
(venv) root@wlc-server:/var/www/FLASKAPP/captive# flask db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 920de77b9b2e, empty message
```

#### 4. Пробный запуск приложения
Теперь пора запустить приложение и убелиться, что приложение развернуто правильно и все зависимости соблюдены

```
(venv) root@wlc-server:/var/www/FLASKAPP/captive# flask run
 * Serving Flask app "captive"
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

#### 5. Настройка apache2 и мод WSGI

Пора научить apache2 запускать наше приложение. Для этого используется модуль **wsgi**  
Конфигурация для этого модуля находится в файле captive-apache.conf
Скопируем этот файл в /etc/apache2/sites-enabled а так же сделаем наш сайт сайтом по умолчанию.
Дак же необходимо активировать модуль **wsgi**

```
(venv) root@wlc-server:/var/www/FLASKAPP/captive# cp captive-apache.conf /etc/apache2/sites-enabled/

(venv) root@wlc-server:/var/www/FLASKAPP/captive# a2dissite 000-default
Site 000-default disabled.
To activate the new configuration, you need to run:
  service apache2 reload
  
(venv) root@wlc-server:/var/www/FLASKAPP/captive# a2ensite captive-apache
Enabling site captive-apache.
To activate the new configuration, you need to run:
  service apache2 reload

(venv) root@wlc-server:/var/www/FLASKAPP/captive# a2enmod wsgi
Enabling module wsgi.
To activate the new configuration, you need to run:
  service apache2 restart

(venv) root@wlc-server:/var/www/FLASKAPP/captive# service apache2 restart
```

Готово! Наше приложение должно заработать на 80-м порту


-----


## Установка и настройка контроллера UniFi

Контроллер может быть установлен отдельно от приложения.  
Одно единственное требование: приложение должно иметь доступ к контроллеру по порту 8443 для авторизации пользователей.

#### Устанока контроллера на Ubuntu Linux 16.04
Проходим по ссылке https://www.ubnt.com/download/unifi и выбираем версию контроллера
Скачиваем контроллер
```
idqdd@wlc-server:~$ wget http://dl.ubnt.com/unifi/5.7.20/unifi_sysvinit_all.deb 
Connecting to dl.ubnt.com (dl.ubnt.com)|54.192.99.193|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 64551764 (62M) [application/x-debian-package]
Saving to: ‘unifi_sysvinit_all.deb’

unifi_sysvinit_all.deb               100%[=====================================================================>]  61,56M  2,97MB/s    in 20s     

2018-04-02 14:13:56 (3,15 MB/s) - ‘unifi_sysvinit_all.deb’ saved [64551764/64551764]
```
И устанавливаем
```
idqdd@wlc-server:~$ sudo dpkg -i unifi_sysvinit_all.deb 
Selecting previously unselected package unifi.
(Reading database ... 96207 files and directories currently installed.)
Preparing to unpack unifi_sysvinit_all.deb ...
Unpacking unifi (5.7.20-10627) ...
dpkg: dependency problems prevent configuration of unifi:
 unifi depends on binutils; however:
  Package binutils is not installed.
 unifi depends on jsvc; however:
  Package jsvc is not installed.
 unifi depends on mongodb-server (>= 2.4.10) | mongodb-10gen (>= 2.4.14) | mongodb-org-server (>= 2.6.0); however:
  Package mongodb-server is not installed.
  Package mongodb-10gen is not installed.
  Package mongodb-org-server is not installed.
 unifi depends on java8-runtime-headless; however:
  Package java8-runtime-headless is not installed.

dpkg: error processing package unifi (--install):
 dependency problems - leaving unconfigured
Processing triggers for systemd (229-4ubuntu21.2) ...
Processing triggers for ureadahead (0.100.0-19) ...
Errors were encountered while processing:
 unifi
```
Из-за отсутствия зависимых пакетов установка завершается ошибкой.  
Исправляем эту неприятную ситуацию магическим заклинанием:
```
idqdd@wlc-server:~$ sudo apt install -f
Reading package lists... Done
Building dependency tree       
Reading state information... Done
Correcting dependencies... Done
The following additional packages will be installed:
  binutils ca-certificates-java default-jre-headless fontconfig-config fonts-dejavu-core java-common jsvc libavahi-client3 libavahi-common-data
  libavahi-common3 libboost-filesystem1.58.0 libboost-program-options1.58.0 libboost-system1.58.0 libboost-thread1.58.0 libcommons-daemon-java
  libcups2 libfontconfig1 libgoogle-perftools4 libjpeg-turbo8 libjpeg8 liblcms2-2 libnspr4 libnss3 libnss3-nssdb libpcrecpp0v5 libsnappy1v5
  libtcmalloc-minimal4 libunwind8 libv8-3.14.5 libxi6 libxrender1 libxtst6 libyaml-cpp0.5v5 mongodb-clients mongodb-server openjdk-8-jre-headless
  x11-common
Suggested packages:
  binutils-doc default-jre java-virtual-machine cups-common liblcms2-utils libnss-mdns fonts-dejavu-extra fonts-ipafont-gothic
  fonts-ipafont-mincho fonts-wqy-microhei fonts-wqy-zenhei fonts-indic
The following NEW packages will be installed:
  binutils ca-certificates-java default-jre-headless fontconfig-config fonts-dejavu-core java-common jsvc libavahi-client3 libavahi-common-data
  libavahi-common3 libboost-filesystem1.58.0 libboost-program-options1.58.0 libboost-system1.58.0 libboost-thread1.58.0 libcommons-daemon-java
  libcups2 libfontconfig1 libgoogle-perftools4 libjpeg-turbo8 libjpeg8 liblcms2-2 libnspr4 libnss3 libnss3-nssdb libpcrecpp0v5 libsnappy1v5
  libtcmalloc-minimal4 libunwind8 libv8-3.14.5 libxi6 libxrender1 libxtst6 libyaml-cpp0.5v5 mongodb-clients mongodb-server openjdk-8-jre-headless
  x11-common
0 upgraded, 37 newly installed, 0 to remove and 0 not upgraded.
1 not fully installed or removed.
Need to get 90,5 MB of archives.
After this operation, 321 MB of additional disk space will be used.
Do you want to continue? [Y/n] Y
```

Нажимаем "Y" устанавливаем и заходим на Unifi Wizard браузером по ссылке:
> https://wlc-srv:8443/manage/wizard/


#### Настройка контроллера для использования External Captive Portal
В свежеустановленном контроллере проходим Wizard, устанавливаем пароль для пользователя admin 


##### Добавляем пользователя для API
Далее необходимо создать нового пользователя, под которым наше приложение будет управлять авторизацией пользователей. Для чего идем [Admins] -> [Add New Admin]

Теперь нужно заполнить соответствующие поля в файле **captive/config.py**:
```
    UNIFI_WLC_IP = '10.0.1.2'
    UNIFI_WLC_PORT = '8443'
    UNIFI_WLC_USER = 'admin_api'
    UNIFI_WLC_PASSW = 'verystrongpassworg'
    INIFI_WLC_VER = 'v5'
    UNIFI_WLC_SITE_ID = 'default'
    UNIFI_WLC_SSL_VERIFY = False

```
##### Настройка Guest Control

Идем в меню GuestControl    
Guest Portal : Enable Guest Portal  
Authentication : External portal server  
Custom Portal IPv4 Address : IP address на котором мы запустили apache (10.0.1.2)  

Возможно в вашем сценарии так же нужно будет поднастроить **Access Control**    
Например по умолчанию после авторизации точка не пускает клиента в сеть 192.168/16, что может поставить в тупик при тестировании. Ну по крайней мере я на это попался, поэтому и предупреждаю

##### Создание гостевой сети
Идем в меню Wireless Networks  
Нажимаем на Create New Wireless Network и создаем сеть с следующими параметрами:  
Name/SSID : YORGWARD  
Enabled : Yes  
Security : Open  
Guest Policy : Yes  

На этом все. Остальное в мануле по UniFi контроллеру



-----

Ой ну ладно ...  
Вдруг кто не знает как Adoption делается т.е. привязка точек к контроллеру.  
Миллион способов на самом деле. Я выбрал [**DHCP Option 43**](https://help.ubnt.com/hc/en-us/articles/204909754-UniFi-Device-Adoption-Methods-for-Remote-UniFi-Controllers#DHCP)

Для адреса контроллера 192.168.74.250 получилась такая строка для DHCP сервера на JuniperSRX: 
```
set routing-instances INET access address-assignment pool DHCP_WLAN family inet dhcp-attributes option 43 hex-string 0104c0a84afa
```

Дальше сунуть точку в нужный *VLAN*, скрепкой ткнуть в *Reset* на точке и увидеть точку на UniFi контроллере в раздеде *Devices* (изображение AP похожее на блюдце) в статусе *Pending*.

