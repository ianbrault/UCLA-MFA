"""
app.py
base web server for the UCLA MFA extension

author: Ian Brault <ianbrault@ucla.edu>
created: 19 May 2018
"""

import os
import re
from urllib.parse import unquote_plus

from aiohttp import web
from twilio.rest import Client

import env
from logger import log

# load environment variables
env.load()

# set up Twilio client
twilio_num = os.getenv('TWILIO_NUM')
twilio_sid = os.getenv('TWILIO_SID')
twilio_tok = os.getenv('TWILIO_TOKEN')
twilio_client = Client(twilio_sid, twilio_tok)


def is_mfa_sms(msg):
    """
    check if a received SMS contains MFA passcodes
    @param msg (str): SMS message contents
    @return (bool)
    """
    return msg.startswith("SMS passcodes: ")


def store_codes(codes):
    """
    write the MFA passcodes to the .codes file
    format is: <current><1code><2code>...<0code>
    @param codes (list(str)): a list of the passcode strings
    """
    log.info("writing passcodes to file")

    file_path = os.path.dirname(os.path.realpath(__file__)) + "/.codes"
    codes_file = open(file_path, 'w')
    codes_file.write("1")  # current
    for code in codes: codes_file.write(code)


def get_code():
    """
    fetch the MFA passcode specified by the current code index (from .codes)
    and update .codes with an incremented current code index
    @return (str): current passcode string
    @raise ValueError on attempted int('x') conversion i.e. out of codes
    """
    log.info("fetching MFA passcode")

    file_path = os.path.dirname(os.path.realpath(__file__)) + "/.codes"
    codes_file = open(file_path, 'r+')

    # get current code index
    # if index is 0, set 'out of codes' flag
    drained = False
    current = int(codes_file.read(1))
    if current == 0: drained = True

    # calculate code offset & read value
    idx = current - 1
    if idx < 0: idx = 9
    codes_file.seek(1 + 7*idx)
    code = codes_file.read(7)

    # update current passcode index
    codes_file.seek(0)
    if drained: codes_file.write('x')
    else: codes_file.write(str((current + 1) % 10))

    log.info("fetched passcode %d: %s", current, code)
    return code


async def sms(req):
    """
    POST handler for receiving SMS
    @param req (aiohttp.web.Request): request object
    @return (aiohttp.web.Response): response object
    """
    log.info("POST /sms received from %s", req.remote)

    # extract SMS message body
    content = await req.text()
    body = list(filter(lambda x: x.startswith("Body="), content.split('&')))[0]
    msg = unquote_plus(body.split('=')[-1])

    if is_mfa_sms(msg):
        log.info("MFA SMS received")
        # extract passcodes & replace file
        codes = msg[15:].split()
        store_codes(codes)

    return web.Response(content_type="text/plain")  # no reply


async def mfa(req):
    """
    GET handler for MFA code requests
    @param req (aiohttp.web.Request): request object
    @return (aiohttp.web.Response): response object
    """
    log.info("GET /passcode received from %s", req.remote)

    # check origin URL of active tab
    origin = req.headers.get('Tab-Url')
    if not origin or not re.match(r'.*://shb.ais.ucla.edu/.*', origin):
        return web.Response(text="invalid origin", status=400)

    # attempt to fetch MFA passcode
    # if ValueError thrown, passcodes are drained
    try:
        code = get_code()
        return web.Response(text=code)
    except ValueError:
        log.info("passcodes file drained")
        return web.Response(text="out of codes")


@web.middleware
async def cors_middleware(req, handler):
    """ add CORS headers to requests """
    log.info("running CORS middleware handler")

    res = await handler(req)
    origin = req.headers.get('Origin')

    # set CORS headers
    if origin: res.headers['Access-Control-Allow-Origin'] = req.headers['Origin']
    res.headers['Access-Control-Allow-Credentials'] = 'true'
    res.headers['Access-Control-Allow-Methods'] = 'GET'
    res.headers['Access-Control-Allow-Headers'] = 'Tab-Url'

    return res


@web.middleware
async def options_middleware(req, handler):
    """ support OPTIONS request handling """
    log.info("running OPTIONS middleware handler")

    if req.method == "OPTIONS":
        log.info("OPTIONS request received")
        return web.Response()

    res = await handler(req)
    return res


routes = [
    web.get('/passcode', mfa),
    web.post('/sms', sms),
]

middleware = [
    cors_middleware,
    options_middleware,
]

app = web.Application(middlewares=middleware)
app.router.add_routes(routes)

log.info("starting server")
web.run_app(app, port=8888, access_log=None)
