#!/usr/bin/env python
from flask import Flask, request, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import validators
from api import get_streams

app = Flask(__name__)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="memory://",
)


# Lee los parámetros de URL y redirige a Streamlink.
def query_handler(args):
    """Comprueba y prueba los argumentos antes de atender la solicitud"""
    if not args.get("streaming-ip"):
        return "No diste ninguna URL."

    # para dacast, tenga en cuenta que tenemos MÚLTIPLES parámetros. Consíguelo si existe
    if args.get("provider"):
        valid = validators.url(args.get("streaming-ip"))
        url = args.get("streaming-ip") + "&provider=" + args.get('provider')
        return get_streams(url) if valid else "La URL que has introducido no es válida."
    else:
        valid = validators.url(args.get("streaming-ip"))
        return get_streams(args.get("streaming-ip")) if valid else "La URL que has introducido no es válida."


# Pagina de presentación
@app.route("/", methods=['GET'])
def index():
    return "Este programa le permite obtener acceso directo a las transmisiones usando Streamlink.\r\nSi tiene un enlace que " \
           "necesita ser tratado, desde esta página web, agregue /iptv-query?streaming-ip= *su URL*.\r\nTenga en cuenta que" \
           "work " \
           "only on Streamlink-supported websites.\r\nEnjoy ! LaneSh4d0w. Special thanks to Keystroke for the API " \
           "usage. "


# iptv-query route -> proporciona un enlace a Streamlink, se analiza el enlace
# para el enrutamiento correcto del complemento y redirige (o muestra) al enlace de transmisión.
@app.route("/iptv-query", methods=['GET'])
@limiter.limit("20/minute")
@limiter.limit("1/second")
def home():
    response = query_handler(request.args)
    valid2 = validators.url(response)
    if response is None or not valid2:
        return response

    return response if request.args.get("noredirect") == "yes" else redirect(response)


# Sistema de limitación de velocidad.
@app.errorhandler(429)
def ratelimit_handler(e):
    return f'{e}. To ensure everyone gets a correct access to the program, we are rate-limiting the server.'


# cambie a su gusto, los parámetros son "ip", "port", "threaded"
if __name__ == '__main__':
    app.run(threaded=False, port=5000)
