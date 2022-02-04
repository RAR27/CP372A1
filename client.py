# Import socket module
from socket import * 
import sys # In order to terminate the program
from struct import *
from struct import pack, unpack
import time

print("------------ Starting Stage A  ------------")
serverName = 'localhost'
#serverName = '10.84.88.53'
# Assign a port number
serverPort = 12000

# Bind the socket to server address and server port
clientSocket = socket(AF_INET, SOCK_DGRAM)
data = b'Hello World!!!'
data_length = len(data)
format_str = "!IHH{}s{}x".format(len(data), 4 - len(data)%4)
packet = pack(format_str, len(data), 0, 1, data)

#clientSocket.connect((serverName, serverPort))
clientSocket. sendto( packet, (serverName, serverPort))
packet, serverAddress = clientSocket.recvfrom(2048)
format_str = "!IHHIIHH"

data_length, pcode, entity, repeat, udp_port, len_var, codeA = unpack(format_str, packet)
print("Received packet from server: data_len: {} pcode: {} entity: {} repeat: {} len: {} udp_port: {} codeA: {}".format(data_length, pcode, entity, repeat, udp_port, len_var, codeA))

print("------------ End of Stage A  ------------\n")
print("------------ Starting Stage B  ------------")

for i in range(repeat):
    data_length = len_var + 4 - (4 if len_var%4 == 0 else len_var%4)
    data = "{}{}".format(i, bytearray(data_length)).encode()
    format_str = "!IHHI{}s{}x".format(len(data), 4 - len(data)%4)
    packet = pack(format_str, data_length, codeA, 1, i, data)
    clientSocket. sendto( packet, (serverName, udp_port))

    clientSocket.settimeout(5.0)
    while True:
        try:
            packet, serverAddress = clientSocket.recvfrom(2048)
            break
        except TimeoutError:
            clientSocket. sendto( packet, (serverName, udp_port))

    format_str = "!IHHI"
    data_length, pcode, entity, acked_packet_id = unpack(format_str, packet)
    print("Received acknowledgement packet from server: data_len: {}, pcode: {}, entity: {}, acknumber: {}".format(data_length, pcode, entity, acked_packet_id))
    
    if acked_packet_id != i:
        print("ID of packet send not equal to ID of packet acknowledged, exiting")
        clientSocket.close()

packet, serverAddress = clientSocket.recvfrom(2048)
format_str = "!IHHII"

data_length, pcode, entity, tcp_port, codeB = unpack(format_str, packet)
print("Recieved final packet: data_len: {}, pcode: {}, entity: {}, tcp_port: {}, codeB: {}".format(data_length, pcode, entity, tcp_port, codeB))
print("------------ End of Stage B  ------------")

clientSocket.close()

print("------------ Starting Stage C  ------------")

serverName = 'localhost'
# Assign a port number
serverPort = 6789
print('connecting to server at tcp port {}'.format(serverPort))
# Bind the socket to server address and server port
clientSocket = socket(AF_INET, SOCK_STREAM)

clientSocket.connect((serverName, serverPort))

time.sleep(2)

packetC, serverAddress = clientSocket.recvfrom(2048)
format_str = '!IHHIIIc'
data_length, pcode, entity, repeat2, len2, codeC, char = unpack(format_str, packetC)
print('Received packet from server: data_len: {}  pcode: {}   entity: {}   repeat2: {}   len2: {}   codeC: {}   char:  {}'.format(data_length, pcode, entity, repeat2, len2, codeC, bytes(char).decode()))

print("------------ End of Stage C  ------------\n")
print("------------ Starting Stage D  ------------")

if (len2)%4 != 0:
    len2_adjusted = len2 + (4 - (len2%4))
else: len2_adjusted = len2
format_str = '!IHH{}s'.format(len2_adjusted)
packetD = pack(format_str, len2_adjusted, codeC, 1, char*len2_adjusted)
print('sending  {} to server for {} times'.format(bytes(char*len2_adjusted).decode(), repeat2))
for _ in range(repeat2):
    clientSocket.sendto(packetD, (serverName, serverPort))

packetD = clientSocket.recv(2048)
format_str = '!IIHI'
data_length, pcode, entity, codeD = unpack(format_str, packetD)
print('Received from server: data_len: {}  pcode: {}  entity: {}  codeD: {}'.format(data_length, pcode, entity, codeD))

clientSocket.close()
sys.exit()
