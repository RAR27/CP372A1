# Import socket module
from socket import * 
import sys # In order to terminate the program
from random import randint
from struct import *

# Assign a port number
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Bind the socket to server address and server port
serverSocket.bind(("", serverPort))

packet, clientAddress = serverSocket.recvfrom(1024)
packet_length = len(packet)
data_length, pcode, entity = unpack("!IHH", packet[:8])
data = unpack("!{}s{}x".format(data_length, 4 - data_length%4), packet[8:])
print("receiving from the client: data_length: {} code: {} entity: {} data: {}".format(data_length, pcode, entity, bytes(data[0]).decode()))

if packet_length%4 != 0:
    print("Packet length not divisible by 4")
    serverSocket.close()  

print("\n------------ Starting Stage A  ------------\n")

format_str = "!IHHIIHH"
entity = 2
repeat = randint(5, 20)
udp_port = randint(20000, 30000)
len_var = randint(50, 100)
codeA = randint(100, 400)
packet = pack(format_str, data_length, pcode, entity, repeat, udp_port, len_var, codeA)
print("sending to the client: data_length: {}  code: {}  entity: {}  repeat: {}  udp_port: {}  len: {} codeA: {}".format(data_length, pcode, 2, repeat, udp_port, len_var, codeA))
serverSocket.sendto(packet, clientAddress)

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(("", udp_port))
print("SERVER: Server ready on the new UDP port: {}".format(udp_port))
print("\nSERVER:------------ End of Stage A  ------------\n")
print("\nSERVER:------------ Starting Stage B  ------------")

for _ in range(repeat):
    packet, clientAddress = serverSocket.recvfrom(2048)
    packet_length = len(packet)
    data_length, pcode, entity, packet_id = unpack("!IHHI", packet[:12])
    data = unpack("!{}s{}x".format(data_length, 4 - data_length%4), packet[12:])
    print("SERVER: received_packet_id =  {} data_len =  {}  pcode: {}".format(packet_id, data_length, pcode))

    if packet_length%4 != 0:
        print("Packet length not divisible by 4")
        serverSocket.close()  

    format_str = "!IHHI"
    packet = pack(format_str, 4, pcode, 2, packet_id)
    serverSocket.sendto(packet, clientAddress)
codeB = randint(100, 400)
tcp_port = randint(20000, 30000)
data_length = 8

format_str = "!IHHII"

packet = pack(format_str, data_length, pcode, 2, tcp_port, codeB)
print("------------- B2: sending tcp_port {} codeB {}".format(tcp_port, codeB))
serverSocket.sendto(packet, clientAddress)
print("------------ End of Stage B  ------------")

serverSocket.close()  
sys.exit()#Terminate the program after sending the corresponding data
