import httplib2
import urllib
import json
import hashlib
import hmac
import time

class btceapi:

    def __init__(self):
        self.key = ''
        self.secret = ''
        self.signature = ''
        self.conn = ''
        self.uri = 'https://btc-e.com'

    def load_key(self):
        f = open('btc-e.key', 'r')
        self.key = f.readline().strip('\n')
        f.close()

    def load_secret(self):
        f = open('btc-e.secret', 'r')
        self.secret = f.readline().strip('\n')
        f.close()

    def sign(self, data):
        key = self.secret.encode()
        digestmod = hashlib.sha512
        msg = data.encode()
        self.signature = hmac.new(key, msg, digestmod).hexdigest()

    def post_request(self, method, body={}):
        body['nonce'] = int(time.time())
        body['method'] = method
        self.sign(urllib.parse.urlencode(body))
        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Key': self.key,
            'Sign': self.signature
            }
        h = httplib2.Http()
        resp, content = h.request(self.uri + '/tapi', 'POST', headers=headers, body=urllib.parse.urlencode(body));
        if resp['status'] == '200':
            data = json.loads(content.decode())
            if data['success'] == 1:
                return(data['return'])
            elif method == 'ActiveOrders' and data['success'] == 0 and data['error'] == 'no orders':
                return([])
            else:
                print('[WARNING]: ' + method + ' failed => ' + data['error'])
        return(None)

    def get_request(self, pair, method):
        h = httplib2.Http()
        resp, content = h.request(self.uri + '/api/2/' + pair + '/' + method, 'GET');
        if resp['status'] == '200':
            data = json.loads(content.decode())
            return(data)
        return(None)

    def get_info(self):
        return(self.post_request('getInfo'))
    
    def get_asset_ticker(self, pair):
        return(self.get_request(pair, 'ticker'))

    def get_asset_depth(self, pair):
        return(self.get_request(pair, 'depth'))

    def activeorders(self):
        return(self.post_request('ActiveOrders'))
   
    def trade(self, pair, ordertype, rate, amount):
        body = {}
        body['type'] = ordertype
        body['pair'] = pair
        body['rate'] = round(rate, 8)
        body['amount'] = round(amount, 8)
        return(self.post_request('Trade', body))
