from flask import Flask, request, Response
import requests

app = Flask(__name__)

BASE_PATH = '/notebook/containername/proxy/8813'

@app.route(BASE_PATH + '/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    # Forward the request to the local server
    resp = requests.request(
        method=request.method,
        url=f'http://localhost:8812/{path}',
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)

    # Send the response back to the client
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    return Response(resp.content, resp.status_code, headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8813)
