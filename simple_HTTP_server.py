"""
Exercise 4.4 - HTTP server shell
Author: Noam Cohen
Purpose: write a simple HTTP server
Note: The code is written in a simple way, with remarks and explains how the plan working
"""

# Import modules
import socket
import os
from ntpath import basename

# Set constants
IP = "0.0.0.0"
PORT = 80
SOCKET_TIMEOUT = 200

GET_INDEX = 0
URL_INDEX = 1
VERSION_INDEX = 2
ROOT_INDEX = 0

VERSION_PROTOCOL = "HTTP/1.1\r\n"
DEFAULT_URL = "C:\\Networks\\work\\webroot\\index.html"
ROOT = "C:\\Networks\\work\\webroot\\"
FORBIDDEN = ["file1.txt", "file2.txt", "file3.txt"]
REDIRECTION_DICTIONARY = {"C:\\Networks\\work\\webroot\\favicon.ico": "C:\\Networks\\work\\webroot\\imgs\\favicon.ico"}

CODE404 = "HTTP/1.1 404 Not Found\r\n\r\n"
CODE403 = "HTTP/1.1 403 Forbidden\r\n\r\n"
CODE302 = "HTTP/1.1 302 Found\r\nLocation: "
CODE200 = "HTTP/1.1 200 OK\r\n"
CODE500 = "HTTP/1.1 500 Internal Server Error\r\n\r\n"


def get_file_data(filename):
    """ Get data from file """
    # Open the file:
    with open(filename, 'rb') as read_file:
        # Read all the data from the file:
        data = read_file.read()
        return data


def get_file_type(url):
    """ Get the file type from the URL """
    # Extract requested file type from URL (html, jpg etc)
    # Get the type of the file:
    filetype = url.split('.')[-1]

    # If the file type is html or txt:
    if filetype in ['html', 'text']:
        # Then return:
        return 'Content-Type: text/html; charset=utf-8'

    # Else, if the file type is jpg:
    elif filetype == 'jpg':
        # Then return:
        return 'Content-Type: image/jpeg'

    # Else, if the file type is js:
    elif filetype == 'js':
        # Then return:
        return 'Content-Type: text/javascript; charset=UTF-8'

    # Else, if the file type is css:
    elif filetype == 'css':
        # Then return:
        return 'Content-Type: text/css'

    # Else, if the file type is ico:
    elif filetype == 'ico':
        # Then return:
        return 'Content-Type: x-icon'

    # Else, if all of those types are not what we are looking:
    return ''


def is_forbidden(url):
    """ Make sure the client has access to the file """
    # get file name from the URL:
    filename = basename(url)

    # If the client has not access to the file:
    if filename in FORBIDDEN:
        # Then return False:
        return False

    # Else, if the client has access to the file:
    return True


def handle_client_request(resource, client_socket):
    """
    Check the required resource,
    generate proper HTTP response and send to client
    """
    # if there is no specific location in the request:
    if resource == '':
        # Then turn to default location - 'DEFAULT_URL':
        url = DEFAULT_URL

    # Else, if there is a specific location in the request:
    else:
        # Then put in url the resource:
        url = ROOT + resource.replace('/', '\\')

    # If the client has not access to the file:
    if not is_forbidden(url):
        # Then send 403 forbidden response:
        client_socket.send(CODE403.encode())
        return

    # If URL had been redirected:
    elif url in REDIRECTION_DICTIONARY:
        # Then make 302 redirection response:
        redirection_rsp = CODE302 + REDIRECTION_DICTIONARY[url] + "\r\n\r\n"
        # And send it to the client:
        client_socket.send(redirection_rsp.encode())
        return

    # If the URL is not exists:
    elif not os.path.exists(url):
        # Then send 404 not found response:
        client_socket.send(CODE404.encode())
        return

    # Get the file type and put in type header:
    http_header = get_file_type(url)
    # Read the data from the file:
    data = get_file_data(url)
    # Make the response:
    http_response = ("Content-Length: " + str(len(data)) + '\r\n' + http_header + '\r\n\r\n').encode()
    http_response_final = CODE200.encode() + http_response + data
    # Send the data and headers:
    client_socket.send(http_response_final)
    return


def validate_http_request(request):
    """
    Check if request is a valid HTTP request,
    and returns TRUE / FALSE and the requested URL
    """
    # Insert the code into 'try' block to prevent an invalid access to the memory:
    try:
        # Split client's request into a few strings:
        client_request = request.split('\r\n')[0]
        client_request = client_request.split(' ')

        # Validate the client's request:
        command = client_request[GET_INDEX]

        # The command must be 'GET':
        if command != "GET":
            # Then the request is not valid, so return False:
            return False, None

        # Verify URL, after verified command:
        url = client_request[URL_INDEX]

        # Check if the URL begin with '/' (Root Directory):
        if url[ROOT_INDEX] != '/':
            # Then the request is not valid, so return False:
            return False, None

        # The version of HTTP protocol:
        version = client_request[VERSION_INDEX]

        # Check the HTTP version that sent with the request:
        if version not in VERSION_PROTOCOL:
            # Then the request is not valid, so return False:
            return False, None

        # Else, if all of those parts are valid:
        # Take the URL without the character that indicates the Root Directory ('/'):
        request_url = url[1:]
        # Return that the request is valid, and the URL:
        return True, request_url

    # In Error cases:
    except Exception as e:
        # Return False and Error number:
        return False, str(e)


def handle_client(client_socket):
    """
    Handles client requests:
    verifies client's requests are legal HTTP,
    calls function to handle the requests
    """
    # After a connection is made:
    print('Client connected')

    # Loop forever
    while True:
        # Get data from the client:
        client_request = client_socket.recv(1024).decode()

        # Verifies client's request are legal HTTP, and get the resource:
        (valid_http, resource) = validate_http_request(client_request)

        # If the request is valid:
        if valid_http:
            # Then alert that we received a valid HTTP request:
            print('Got a valid HTTP request')
            # call to 'handle_client_request':
            handle_client_request(resource, client_socket)
            # End the loop:
            break

        # Else, if the request is not valid:
        else:
            # If was sent an exception:
            if type(resource) == str:
                # Then was be an invalid access to the memory:
                print('Error: Not a valid HTTP request, ' + resource)
                # Send 500 Internal Server Error:
                client_socket.send(CODE500.encode())
                # End the loop:
                break

            # Else, print that an invalid HTTP request was received:
            print('Error: Not a valid HTTP request')
            # Send 500 Internal Server Error:
            client_socket.send(CODE500.encode())
            # End the loop:
            break

    # Close the connection:
    print('Closing connection')
    client_socket.close()


def main():
    # Open a socket:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))

    # Waiting for a connection to be made:
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))

    # Loop forever while waiting for clients:
    while True:
        # Accept to the connection:
        (client_socket, client_address) = server_socket.accept()
        # Alert that new connection received:
        print('New connection received')
        # Set TimeOut, in order to prevent cases where requests are sent at the same time by both sides:
        client_socket.settimeout(SOCKET_TIMEOUT)
        # Call to 'handle_client':
        handle_client(client_socket)


if __name__ == "__main__":
    # Call the main handler function
    main()
