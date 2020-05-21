from flask import Flask
import os

PORT = int(os.getenv("PORT", 8080))
app = Flask(__name__)

@app.route('/')
def app(environ, start_response):

    data = b'Entrypoint to my application\n'
    status = '200 OK'

    response_headers = [
        ('Content-type', 'text/plain'),
        ('Content-Length', str(len(data)))
    ]

    start_response(status, response_headers)

    return iter([data])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
