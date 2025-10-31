import urllib.parse


def application(environ, response):
    """
    WSGI application that prints out the HTTP request method, GET parameters, and POST parameters.

    Parameters:
    environ (dict): A dictionary containing the WSGI environment variables.
    response (function): A function that takes a status code and a list of response headers as arguments.

    Returns:
    list: A list containing a single byte string which is the response body.
    """
    method = environ.get('REQUEST_METHOD', 'GET')
    get_params = urllib.parse.parse_qs(environ.get('QUERY_STRING', ''))
    post_params = {}
    try:
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        if content_length > 0:
            post_data = environ['wsgi.input'].read(content_length)
            post_params = urllib.parse.parse_qs(post_data.decode('utf-8'))
    except (ValueError, KeyError):
        pass
    output = f'Method: {method}\n\n'
    output += "GET Parameters:\n"
    for key, values in get_params.items():
        for value in values:
            output += f"  {key}: {value}\n"

    output += "\nPOST Parameters:\n"
    for key, values in post_params.items():
        for value in values:
            output += f"  {key}: {value}\n"

    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/plain; charset=utf-8'),
        ('Content-Length', str(len(output.encode('utf-8'))))
    ]

    response(status, response_headers)
    return [output.encode('utf-8')]
