#!/usr/bin/env python3
#
# Copyright (C) 2017 Joseph W. Metcalf
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby 
# granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING 
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, 
# DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, 
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE 
# USE OR PERFORMANCE OF THIS SOFTWARE.
#

import sys
import defs
import argparse
import string
import logging
import datetime
import time
import subprocess
import calendar

def alert_start(JJJHHMM, format='%j%H%M'):
    """Convert EAS date string to datetime format"""
    utc_dt = datetime.datetime.strptime(JJJHHMM, format).replace(year=datetime.datetime.utcnow().year)
    timestamp = calendar.timegm(utc_dt.timetuple())
    return datetime.datetime.fromtimestamp(timestamp)

def fn_dt(dt, format='%I:%M %p'):
    """Return formatted datetime"""
    return dt.strftime(format)

def format_error(info=''):
    logging.warning('INVALID FORMAT ' + info)

def time_str(x, type='hour'):
    if x == 1:
        return f"{x} {type}"
    elif x >= 2:
        return f"{x} {type}s"
    
def get_length(TTTT):
    hh, mm = TTTT[:2], TTTT[2:]  
    return ' '.join(filter(None, (time_str(int(hh)), time_str(int(mm), type='minute'))))

def county_decode(input, COUNTRY):
    """Convert SAME county/geographic code to text list"""
    P, SS, CCC, SSCCC = input[:1], input[1:3], input[3:], input[1:]
    if COUNTRY == 'US':
        if SSCCC in defs.SAME_CTYB:
            SAME__LOC = defs.SAME_LOCB
        else:
            SAME__LOC = defs.SAME_LOCA
        if CCC == '000':
            county = 'ALL'
        else:
            county = defs.US_SAME_CODE[SSCCC]
        return [' '.join(filter(None, (SAME__LOC[P], county))), defs.US_SAME_AREA[SS]]
    else:
        if CCC == '000':
            county = 'ALL'
        else:
            county = defs.CA_SAME_CODE[SSCCC]
        return [county, defs.CA_SAME_AREA[SS]]

def get_division(input, COUNTRY='US'):
    if COUNTRY == 'US':
        try:
            DIVISION = defs.FIPS_DIVN[input]
            if not DIVISION:
                DIVISION = 'areas'
        except KeyError:
            DIVISION = 'counties'
    else:
        DIVISION = 'areas'
    return DIVISION

def get_event(input):
    event = None
    try:
        event = defs.SAME__EEE[input]
    except KeyError:
        if input[2:] in 'WAESTMN':
            event = ' '.join(['Unknown', defs.SAME_UEEE[input[2:]]])
    return event

def get_indicator(input):
    indicator = None
    try:
        if input[2:] in 'WAESTMNR':
            indicator = input[2:]
    except IndexError:
        pass
    return indicator

def printf(output=''):   
    output = output.lstrip(' ')
    output = ' '.join(output.split())
    sys.stdout.write(output + '\n')
 
def alert_end(JJJHHMM, TTTT):
    alertstart = alert_start(JJJHHMM)
    delta = datetime.timedelta(hours=int(TTTT[:2]), minutes=int(TTTT[2:]))
    return alertstart + delta

def alert_length(TTTT):
    delta = datetime.timedelta(hours=int(TTTT[:2]), minutes=int(TTTT[2:]))
    return delta.seconds

def get_location(STATION=None, TYPE=None): 
    location = ''
    if TYPE == 'NWS':
        try:
            location = defs.ICAO_LIST[STATION].title()
        except KeyError:
            pass
    return location

def check_watch(watch_list, PSSCCC_list, event_list, EEE):
    if not watch_list:
        watch_list = PSSCCC_list
    if not event_list:
        event_list = [EEE] 
    w, p = [], []
    w += [item[1:] for item in watch_list]
    p += [item[1:] for item in PSSCCC_list]
    if (set(w) & set(p)) and EEE in event_list:
        return True
    else:
        return False

def kwdict(**kwargs):
    return kwargs

def format_message(command, ORG='WXR', EEE='RWT', PSSCCC=[], TTTT='0030', JJJHHMM='0010000', STATION=None, TYPE=None, LLLLLLLL=None, COUNTRY='US', LANG='EN', 
