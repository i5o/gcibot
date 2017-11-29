#!/usr/bin/env python
from flask import Flask
from flask import request
from OpenSSL import SSL
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('key.key')
context.use_certificate_file('key.crt')

app = Flask(__name__)

@app.route('/', methods=['POST'])
def notification():
  print request.json
  message = "OK"
  if request.json['event_type'] == "abandon":
    message = "[GCI] %s has abandoned the task (%s)" % (request.json['author'], request.json['task_instance_url'])

  return message

if __name__ == '__main__':
    app.run(host="localhost", port=5324, ssl_context=context)