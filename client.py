# Import socket module
from socket import * 
import sys # In order to terminate the program
from struct import *
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
print("Recieved packet from server: data_len: {} pcode: {} entity: {} repeat: {} len: {} udp_port: {} codeA: {}".format(data_length, pcode, entity, repeat, udp_port, len_var, codeA))

print("------------ End of Stage A  ------------\n")
print("------------ Starting Stage B  ------------")

for i in range(repeat):
    data = "{}{}".format(i, bytearray(len_var + 4 - len_var%4)).encode('utf-8')
    format_str = "!IHHI{}s{}x".format(len(data), 4 - len(data)%4)
    packet = pack(format_str, len(data), codeA, 1, i, data)
    clientSocket. sendto( packet, (serverName, udp_port))

    clientSocket.settimeout(5.0)
    try:
        packet, serverAddress = clientSocket.recvfrom(2048)
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
