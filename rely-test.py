import requests
import time
from datetime import datetime
import random
from pprint import pprint
import itertools
import json
from enum import Enum
import os

###############################################################################
# App

result_file = "result.json"
total_requests = 1000000
# request_timeout =

url = os.getenv("ERPC_TEST_URL", "http://localhost:4010/main/evm")

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    # "Origin": "https://yourdomain.com"
}
data = {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "eth_blockNumber"
}
chain_ids = [
    8453,   # Base
    56,     # BNB Chain
    1,      # Ethereum Mainnet
    137,    # Polygon (MATIC)
    42161,  # Arbitrum One
    10,     # Optimism"
    43114,  # Avalanche C-Chain
    250,    # Fantom Opera
    1101,   # Polygon zkEVM
    25,     # Cronos
    42220,  # Celo
    100,    # Gnosis (xDai)
    8217,   # Klaytn
    5000,   # Mantle
    1088,   # Metis Andromeda
    128,    # Huobi ECO Chain (HECO)
    1284,   # Moonbeam
    42170,  # Arbitrum Nova
]

def mk_chain_info(chain_id):
    info = {
        "total": 0,
        "succs": 0,
        "fails": 0,
        "succ%": "0%",
        "avg_time": 0,
        "max_time": 0,
        "min_time": 0,
        "fails_with_status_codes": {}, # { status_code: count }
        "exception&noresponse": 0
    }
    return (chain_id, info)

result = {
    "total": 0,
    "total_successes": 0,
    "total_failures" : 0,
    "total_succ%": "0%",
    "avg_time": 0,
    "max_time": 0,
    "min_time": 0,
    "chains": dict(map(mk_chain_info, chain_ids))
}

time_taken = {
    "sum": 0,
    "num": 0,
    "max": 0,
    "min": 1000000,
}

def mk_chain_time_taken(chain_id):
    time_taken_ = {
        "sum": 0,
        "num": 0,
        "max": 0,
        "min": 1000000,
    }
    return (chain_id, time_taken_)

time_taken_per_chain = dict(map(mk_chain_time_taken, chain_ids))

def _add_time_taken_of_chain(chain_id, time_):
    tt = time_taken_per_chain[chain_id]
    rc = result["chains"][chain_id]

    tt["sum"] += time_
    tt["num"] += 1
    rc["avg_time"] += round3(tt["sum"] / tt["num"])
    tt["max"] = round3(max(time_, tt["max"]))
    rc["max_time"] += tt["max"]
    tt["min"] = round3(min(time_, tt["min"]))
    rc["min_time"] += tt["min"]

def add_succ(chain_id, time_):
    tt = time_taken
    res = result
    rc = res["chains"][chain_id]

    res["total"] += 1
    res["total_successes"] += 1
    res["total_succ%"] = mk_percent(res["total_successes"], res["total"])
    tt["sum"] += time_
    tt["num"] += 1
    res["avg_time"] += round3(tt["sum"] / tt["num"])
    tt["max"] = round3(max(time_, tt["max"]))
    res["max_time"] += tt["max"]
    tt["min"] = round3(min(time_, tt["min"]))
    res["min_time"] += tt["min"]

    rc["total"] += 1
    rc["succs"] += 1
    rc["succ%"] = mk_percent(rc["succs"], rc["total"])
    _add_time_taken_of_chain(chain_id, time_)


def add_fail_with_code(chain_id, status_code):
    _add_fail(chain_id)
    inc_or_add(status_code, result["chains"][chain_id]["fails_with_status_codes"])

def add_fail_with_except(chain_id, msg):
    _add_fail(chain_id)
    result["chains"][chain_id]["exception&noresponse"] += 1

def _add_fail(chain_id):
    result["total"] += 1
    result["total_failures"] += 1
    result["chains"][chain_id]["total"] += 1
    result["chains"][chain_id]["fails"] += 1

def write_result_to_file():
    with open(result_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(result, indent=2))

def eval_result(i, chain_id):
    log.debug(f"\n--- Request {i} at {datetime.now()} ---")
    succ_reqs = 0
    url_ = url + '/' + str(chain_id)
    log.debug(f"\nurl: {url_}\n")
    try:
        startt = time.perf_counter()
        resp = requests.post(url_, headers=headers, json=data)
        endt = time.perf_counter()
        elapsedt = endt - startt
        if resp.status_code == 200:
            add_succ(chain_id, elapsedt)
            log.debug(f"[{i}] Success (200)")
        else:
            add_fail_with_code(chain_id, resp.status_code)
            log.debug(f"[{i}] Failed with status {resp.status_code}")
    except requests.RequestException as e:
        add_fail_with_except(chain_id, str(e))
        log.debug(f"[{i}] Exception occurred: {e}")

###############################################################################
# Main

def main():
    log.info(f"\n--- Test started at {datetime.now()} ---")
    for i, chain_id in enumerate(itertools.cycle(chain_ids), start=1):
        eval_result(i, chain_id)
        write_result_to_file()

        if i < total_requests:
            if i % 3 == 0:
                write_result_to_file()
            time.sleep(10) # in second
        else:
            write_result_to_file()
            break

def test_dev():
    eval_result(1, 1)
    write_result_to_file()

###############################################################################
# Utile

def inc_or_add(key, dict_):
    if key in dict_: dict_[key] += 1
    else:            dict_[key] =  1

def mk_percent(x, y):
    return str(x / y * 100) + "%"

def round3(x):
    return round(x, 3)

class LogLevel(Enum):
    NONE = 1
    INFO = 2
    DEBUG = 3

class Log():
    def __init__(self, level):
        nothing = lambda _x : None
        print_if = lambda level_: print if level.value >= level_.value else nothing
        self.info  = print_if(LogLevel.INFO)
        self.debug = print_if(LogLevel.DEBUG)

###############################################################################
# Run

log = Log(LogLevel.INFO)

main()
# test_dev()

