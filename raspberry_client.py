import socket
import sys
import time

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('192.168.1.78', 1112)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

try:
    
    # Send data
    message = 'This is the message.  It will be repeated.'
    print >>sys.stderr, 'sending "%s"' % message
    sock.sendall(message)

    # Look for the response
    amount_received = 0
    amount_expected = len(message)
    print(amount_expected)
    
    while amount_received < amount_expected:
        data = sock.recv(amount_expected)
        amount_received += len(data)
        print >>sys.stderr, 'received "%s"' % data
finally:
	while True:
		time.sleep(10)
