"""
app.py
base web server for the UCLA MFA extension

author: Ian Brault <ianbrault@ucla.edu>
created: 19 May 2018
"""

import logging

from aiohttp import web

logfmt = logging.Formatter(fmt="[%(asctime)s]: %(message)s", datefmt='%I:%M:%S')
log = logging.getLogger()
log.setLevel(logging.INFO)

fileLog = logging.FileHandler("server.log")
fileLog.setFormatter(logfmt)
log.addHandler(fileLog)

consLog = logging.StreamHandler()
consLog.setFormatter(logfmt)
log.addHandler(consLog)


async def mfa(req):
    """
    GET request handler for MFA code requests
    @param req (aiohttp.web.Request): request object
    @return (aiohttp.web.Response): response object
    """

    log.info("GET / received from %s", req.remote)
    return web.Response(text="1234567", status=200)


routes = [
    web.get('/', mfa),
]

app = web.Application()
app.router.add_routes(routes)

log.info("starting server")
web.run_app(app, access_log=None)
