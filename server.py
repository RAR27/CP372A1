# Import socket module
from socket import * 
import sys # In order to terminate the program
from random import randint
from struct import *
from struct import calcsize, pack, unpack 

# Assign a port number
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Bind the socket to server address and server port
serverSocket.bind(("", serverPort))
serverSocket.settimeout(3.0)

packet, clientAddress = serverSocket.recvfrom(1024)
packet_length = len(packet)
data_length, pcode, entity = unpack("!IHH", packet[:8])
data = unpack("!{}s{}x".format(data_length, 4 - data_length%4), packet[8:])
print("receiving from the client: data_length: {} code: {} entity: {} data: {}".format(data_length, pcode, entity, bytes(data[0]).decode()))

if packet_length%4 != 0:
    print("Packet length not divisible by 4")
    serverSocket.close()  
    exit()
elif pcode != 0:
    print("Unexpected pcode")
    serverSocket.close()
    exit()
elif data_length != len(data[0]):
    print("Data length does not match")
    serverSocket.close()
    exit()

print("\nSERVER: ------------ Starting Stage A  ------------\n")

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

prev_id = 0
for _ in range(repeat):
    packet, clientAddress = serverSocket.recvfrom(2048)
    packet_length = len(packet)
    data_length, pcode, entity, packet_id = unpack("!IHHI", packet[:12])
    data = unpack("!{}s".format(data_length), packet[12:])
    print("SERVER: received_packet_id =  {} data_len =  {}  pcode: {}".format(packet_id, data_length, pcode))
    if packet_length%4 != 0:
        print("Packet length not divisible by 4")
        serverSocket.close()  
        exit()
    elif pcode != codeA:
        print("Unexpected pcode")
        serverSocket.close()
        exit()
    elif unpack("!I", packet[12:16])[0] != packet_id:
        print("packet_id does not match data {} {}".format(unpack("!I", packet[12:16]), packet_id))
        serverSocket.close()
        exit()
    elif packet_id > 0 and packet_id != prev_id + 1:
        print("Packets not sent in order")
        serverSocket.close()
        exit()
    elif data_length != len(data[0]):
        print("Data length does not match")
        serverSocket.close()
        exit()

    prev_id = packet_id

    format_str = "!IHHI"
    packet = pack(format_str, 4, pcode, 2, packet_id)
    serverSocket.sendto(packet, clientAddress)
codeB = randint(100, 400)
tcp_port = randint(20000, 30000)
data_length = 8

format_str = "!IHHII"

packet = pack(format_str, data_length, pcode, 2, tcp_port, codeB)
print("SERVER: ------------- B2: sending tcp_port {} codeB {}".format(tcp_port, codeB))
serverSocket.sendto(packet, clientAddress)
print("------------ End of Stage B  ------------")

serverSocket.close()  
# sys.exit()#Terminate the program after sending the corresponding data
print("\n------------ Starting Stage C ------------\n")

# Create a TCP server socket
#(AF_INET is used for IPv4 protocols)
#(SOCK_STREAM is used for TCP)

serverSocket = socket(AF_INET, SOCK_STREAM)

# Assign a port number
serverPort = 6789

# Bind the socket to server address and server port
serverSocket.bind(("", serverPort))

# Listen to at most 1 connection at a time
serverSocket.listen(5)

# Set up a new connection from the client
connectionSocket, addr = serverSocket.accept()
print('The server is ready to receive on tcp port:  {}'.format(serverPort))

format_str = '!IHHIIIc'
repeat2 = randint(5,20)
len2 = randint(50,100)
codeC = randint(100,400)
char = b'M' # make random
data_length = 13
packet = pack(format_str, data_length, codeB,2, repeat2, len2, codeC, char) #have to change pcode
connectionSocket.send(packet)
print('Server Sending to the client:  data_length: {} code: {}  entity: {}  repeat2: {}  len2: {} codeC:  {}'.format(data_length, codeB, 2, repeat2, len2, codeC))
print("\n------------ End of Stage C    ------------\n")
print("\n------------ Starting Stage D  ------------")


if (len2)%4 != 0:
    len2_adjusted = len2 + (4 - (len2%4))
else: len2_adjusted = len2
format_str_D = '!IHH{}s'.format(len2_adjusted)
print('Starting to Receive packets from client')
for i in range(repeat2):
    packetD = connectionSocket.recv(1024)
    assert calcsize(format_str_D)%4 == 0
    data_length_D, pcode, entity, data = unpack(format_str_D, packetD)
    assert data_length_D == len(data)
    assert pcode == codeC
    assert entity == 1
    assert len(data) == len2_adjusted
    print('i =  {} data_len:  {} pcode:  {} entity:  {} data:  {}'.format(i, data_length_D, pcode, entity, bytes(data).decode()))

format_strD2 = '!IIHI'
packetD2 = pack(format_strD2, 4, pcode, 2, randint(100,400))
connectionSocket.send(packetD2)
connectionSocket.close()

serverSocket.close()  
sys.exit()#Terminate the program after sending the corresponding data
