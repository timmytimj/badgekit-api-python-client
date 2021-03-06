import badgekitapiclient
from badgekitapiclient.remote import errors
from urlparse import urlparse, parse_qsl

try:
    import json
except ImportError:
    import simplejson


MethodNotAllowedError = errors['MethodNotAllowedError']
ResourceNotFoundError = errors['ResourceNotFoundError']
ValidationError = errors['ValidationError']

class Remote (badgekitapiclient.Remote):

    def __init__ (self):
        self.endpoint = 'http://mock'
        self._auth = 'MockRemote'

    def _request (self, request):
        method = request.get('method').lower()
        url = request.get('url')

        if 'data' in request:
            request['data'] = json.loads(request['data'])

        try:
            parts = urlparse(url)
            path = 'fixtures' + parts.path.replace('/', '.')
            module = __import__(path, fromlist=(method,))

            rsp = getattr(module, method)(request, dict(parse_qsl(parts.query)))

        except (AttributeError, TypeError):
            body = {
                'code': 'MethodNotAllowedError',
                'message': '%s is not allowed' % method.upper()
            }
            status_code = 405

        except ImportError:
            body = {
                'code': 'ResourceNotFound',
                'message': 'Not found: %s' % url
            }
            status_code = 404

        else:
            if type(rsp) == dict:
                rsp = [rsp]

            body = rsp[0]
            status_code = rsp[1] if len(rsp) > 1 else 200

        return Response(body, status_code)


class Response (object):
    def __init__ (self, body, status_code=200):
        self.body = body
        self.status_code = status_code

    def json (self):
        return self.body
