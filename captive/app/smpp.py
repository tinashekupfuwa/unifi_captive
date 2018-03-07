#!/usr/bin/python
import logging
import sys

import smpplib.gsm
import smpplib.client
import smpplib.consts

# if you want to know what's happening
#logging.basicConfig(level='DEBUG')


def send_smpp_message(dest, string):
    parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(string)

    client = smpplib.client.Client(app.config['SMPP_SERVER'], app.config['SMPP_PORT'])

# Print when obtain message_id
    client.set_message_sent_handler(
            lambda pdu: sys.stdout.write('sent {} {}\n'.format(pdu.sequence, pdu.message_id)))
    client.set_message_received_handler(
            lambda pdu: sys.stdout.write('delivered {}\n'.format(pdu.receipted_message_id)))

    client.connect()
    client.bind_transceiver(system_id=app.config['SMPP_USER'], password=app.config['SMPP_PASSW'])


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
#dest = '79166133329'
#send_message(dest, 'Mahlzeit')
#client.listen()
