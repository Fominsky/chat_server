import socket
import asyncio
import binascii

from collections import deque

ring_buffer = deque(maxlen=1024)

clients_counter = 0

class Client:
    global clients_counter
    def __init__(self, reader, writer, number):
        self.reader = reader        
        self.writer = writer
        self.number = number

    async def read(self):
        while True:
            try:
                data = await self.reader.readexactly(1)
                ring_buffer.append(data)
                data_to_log = binascii.hexlify(data)
                #try:
                #    print('Client ',self.number,'sent data. Data is: \n', data_to_log, 'end of data')
                #except:
                #    print('no')
                if len(ring_buffer) > 0:
                    data2sent = ring_buffer.popleft()
                    for client in clients:
                        if client != self:
                            #print('Client ',self.number,'sent data. Data is: \n', hex(data))
                            
                            await client.send(data2sent)
            except:
                print('Client has been disconected')
                self.writer.close()
                clients.remove(self)
                break
            
    async def send(self, data):
            self.writer.write(data)
            await self.writer.drain()
            if self.writer.is_closing():
                print('Client has been disconected')
                
clients = list()

async def client_conneted_cb(reader, writer):
    global clients_counter
    print('New client has been connected. Total connections are', clients_counter+1)
    new_client = Client(reader, writer, clients_counter)
    clients.append(new_client)
    clients_counter += 1 
    await asyncio.create_task(new_client.read())
    clients_counter -= 1
    print('Total connections are', clients_counter)


async def main():
    print('App started!')

    srv =   await asyncio.start_server(client_conneted_cb, '127.0.0.1', 3030)
    await srv.serve_forever()

asyncio.run(main())