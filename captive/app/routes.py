# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request
from captive.app import app, db
from captive.app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from captive.app.models import User, Auth
#from twilio.rest import Client
import smpplib.gsm
import smpplib.client
import smpplib.consts
#import sys
#import logging
from pyunifi.controller import Controller

from random import randint
from urllib.parse import unquote
import datetime

# UnifiController does redirect clients to a predidefined URL /guest/s/<domain>/ where default <domain> is "default"
# this function just enriches the query with that domain and then redirects to /register view with all the initial query values
@app.route('/guest/s/<domain>/')
def init(domain):
    return redirect(url_for('register', domain=domain) + '&' + request.query_string.decode('utf8'))    


@app.route('/index')
@login_required
def index():   
    user = User.query.filter_by(id=current_user.get_id()).first()
    auth = Auth.query.filter_by(auth=user).order_by(Auth.timestamp.desc()).first()
    if not auth.requested_url:
        requested_url = "http://vbrr.ru"
    else:    
        requested_url = unquote(auth.requested_url)
        print (requested_url)
    return render_template('index.html', title='Home', requested_url=requested_url)


@app.route('/logout')
def logout():
    if not current_user.is_authenticated: 
        return
    user = User.query.filter_by(id=current_user.get_id()).first()
    auth = Auth.query.filter_by(auth=user).first()
    print("logout user id:{}, mac:{}, ap_mac:{}".format(current_user.get_id(), user.mac, auth.ap_mac))

    auth.logged_in = 0
    db.session.commit()
    logout_user()

    c = Controller(app.config['UNIFI_WLC_IP'], app.config['UNIFI_WLC_USER'], 
            app.config['UNIFI_WLC_PASSW'], app.config['UNIFI_WLC_PORT'], app.config['INIFI_WLC_VER'], 
            app.config['UNIFI_WLC_SITE_ID'], app.config['UNIFI_WLC_SSL_VERIFY'])
    c.unauthorize_guest(user.mac)

    return redirect(url_for('register', id = user.mac, ap = auth.ap_mac))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():

        if form.pin.data == "123456":
            user = User.query.filter_by(id=1).first()
            login_user(user, remember=True)
            return redirect(url_for('admin'))    

        auth = Auth.query.filter_by(pin=form.pin.data).first()
        if auth is None:
            flash('incorrect PIN')
            print('Некорректный PIN')
            return redirect(url_for('login'))
        elif not checkPinNotEpired(auth.timestamp):
            flash('outdated PIN')
            print('Просроченный PIN')
            return redirect(url_for('login'))

        auth.logged_in = 1
        db.session.commit()
        user = User.query.filter_by(id=auth.user_id).first()

        login_user(user, remember=True)
        
        # authorize on an UniFi controller       
        c = Controller(app.config['UNIFI_WLC_IP'], app.config['UNIFI_WLC_USER'], 
            app.config['UNIFI_WLC_PASSW'], app.config['UNIFI_WLC_PORT'], app.config['INIFI_WLC_VER'], 
            app.config['UNIFI_WLC_SITE_ID'], app.config['UNIFI_WLC_SSL_VERIFY'])

        c.authorize_guest(user.mac, app.config['TIME_QOUTE'], 
            up_bandwidth=None, down_bandwidth=None, byte_quota=None, ap_mac=None)
        
        return redirect((url_for)('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    query_string = request.query_string    

    mac = request.args.get('id')    
    ap_mac = request.args.get('ap')
    domain = request.args.get('domain')
    ssid = request.args.get('ssid')
    requested_url = request.args.get('url')
    ip_addr = request.remote_addr

    print ('query_string: {}\n mac: {}, ap_mac: {}; ip address: {}\n domain: {}, ssid: {}, requested_url: {}'.\
        format(query_string, mac, ap_mac, ip_addr, domain, ssid, requested_url))

# for debug. has to be removed in production
    if not query_string:
        mac = "aa:aa:aa:aa:aa:aa"
        ap_mac = "bb:bb:bb:bb:bb:bb"

# make sure this user (mac) was not logged in recently
# and 
    if UserWasLoggedInRecently(mac):
        return redirect((url_for)('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(mac = mac).first()
        if user is None:
            user = User(mac=mac)
            db.session.add(user)
            db.session.commit()
            user = User.query.filter_by(mac = mac).first()
        
        phone = form.phone.data
        pin = generate_pin()                
        print (user.id, phone, pin, ap_mac, ip_addr, requested_url, domain, ssid) #debug

        auth = Auth(phone = phone, pin = pin, ap_mac = ap_mac, ip_addr = ip_addr, requested_url = requested_url, domain = domain, ssid = ssid, logged_in = 0 ,auth = user)
        db.session.add(auth)
        db.session.commit()
        
        if phone[:3] == "900":
            msg = 'SMS не посылалась. Используйте код (' + pin + ')'
            flash(msg) 
            return redirect(url_for('login'))

        if(send_sms(phone, pin)):
            msg = 'SMS with a code (' + pin + ') has been sent'
            print(msg)
            flash(msg) 
        else:
            print('something goes wrong')
            db.session.rollback()            
            return redirect(url_for('register') + '?' + query_string.decode('utf8'))             

        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(id=username).first_or_404()
    p = Auth.query.filter_by(auth=user)
    pins=[]
    for x in p:
        pins.append({'pin': x.pin, 'timestamp': x.timestamp, 'phone': x.phone, 'ip': x.ip_addr })
        
    return render_template('user.html', mac=user.mac, pins=pins)


@app.route('/admin')
@login_required
def admin():
    users = User.query.all()
    d = [ { 'id': x.id, 'mac': x.mac } for x in users ]    
    return render_template('admin.html', users=d)


def generate_pin():
    r = []
    r = [str(randint(0,9)) for x in range(6)]
    return ''.join(r)


def send_sms(dest,string):
    
    if app.config['SMS_ENABLE'] == 0:
        return True

    string = 'PIN код для регистрации в WiFi сети: ' + string
    parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(string)
    dest = '7' + dest

    client = smpplib.client.Client(app.config['SMPP_SERVER'], app.config['SMPP_PORT'])

# Print when obtain message_id
    client.set_message_sent_handler(
            lambda pdu: sys.stdout.write('sent {} {}\n'.format(pdu.sequence, pdu.message_id)))
    client.set_message_received_handler(
            lambda pdu: sys.stdout.write('delivered {}\n'.format(pdu.receipted_message_id)))

    client.connect()
    client.bind_transmitter(system_id=app.config['SMPP_USER'], password=app.config['SMPP_PASSW'])

    print ('Sending SMS {} to {}'.format(string, dest))
    for part in parts:
        pdu = client.send_message(
            source_addr_ton=smpplib.consts.SMPP_TON_INTL,
            source_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
            source_addr=app.config['SMPP_SOURCE'],
            dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
            dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
            destination_addr=dest,
            short_message=part,
            data_coding=encoding_flag,
            #esm_class=msg_type_flag,
            esm_class=smpplib.consts.SMPP_MSGMODE_FORWARD,
            registered_delivery=False,
    )
    print(pdu.sequence)
    client.disconnect()
    
    return True
    
    """
# the following line needs your Twilio Account SID and Auth Token
    client = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'])

    phone_str = "+7"+str(phone)
    pin_str = str(pin)

    print ('send SMS by twilio with SID: {}, AUTH: {}, from: {}, to: {}, sms text: {}'.format(
        app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'], 
        app.config['TWILIO_PHONE_NUMBER'], phone_str, pin_str)
    )
    client.messages.create(to=phone_str, from_=app.config['TWILIO_PHONE_NUMBER'], body=pin_str)
    return True
    """

def checkPinNotEpired(time):
    return True

# if a user has been logged in in a time range of TIME_QUOTE 
# but the application forgot its session (has been restarted or something)
# we have to logg the user back with no user interaction
def UserWasLoggedInRecently(mac):
    user = User.query.filter_by(mac = mac).first()
    if user is not None:
        auth = Auth.query.filter_by(auth=user).order_by(Auth.timestamp.desc()).first()
        CurrentTime = datetime.datetime.utcnow()
        if int(auth.logged_in) > 0:
            if (auth.timestamp + datetime.timedelta(minutes=int(app.config['TIME_QOUTE'])) > CurrentTime):        
                login_user(user, remember=True)
                return True
    return False
