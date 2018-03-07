## попытка написать external captive portal для UniFI контроллера

полезные ссылки:  
учебник FLASK:  
https://habrahabr.ru/post/346344/  
http://exploreflask.com/en/latest/forms.html  

DB Modeler: http://ondras.zarovi.cz/sql/demo/  

UniFI API Bash: https://dl.ubnt.com/unifi/5.4.15/unifi_sh_api  
UniFI API python: https://github.com/calmh/unifi-api  
UniFI API PHP: https://github.com/Art-of-WiFi/UniFi-API-client  
Django-Unifi-Portal: https://github.com/bsab/django-unifi-portal   

Redirection to a custom URL from the UniFi controller JSP-based captive portal: https://gist.github.com/malle-pietje

WTForms:  
http://wtforms.simplecodes.com/docs/0.6.1/fields.html  
http://exploreflask.com/en/latest/forms.html

На данный момент работает регистрация, генерация PIN и логин  
ссылка на регистрацию должна содержать параметры id и ap (mac адреса клиента и точки соответственно)  
http://127.0.0.1:5000/?ap=12:23:34:45:56:ff&id=33:33:33:33:33:55

для отладки сделана страницу с индексом клиента  
http://127.0.0.1:5000/user/6

отсталось по минимум реализовать отправку PIN по SMS  
совместить с Unifi контроллером  
и сделать красиво
красота наводится с помощью стилей отсюда: https://getbootstrap.com/docs/3.3/getting-started/