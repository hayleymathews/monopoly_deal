import asyncio
import telnetlib3


@asyncio.coroutine
def shell(reader, writer):
    while True:
        outp = yield from reader.read(1024)
        if not outp:
            # End of File
            break
        elif outp[-2:] == ': ' or '?' in outp:
            msg = input(outp)
            writer.write(msg)
        else:
            print(outp)
    # EOF
    print()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = telnetlib3.open_connection('localhost', 6023, shell=shell)
    reader, writer = loop.run_until_complete(coro)
    loop.run_until_complete(writer.protocol.waiter_closed)