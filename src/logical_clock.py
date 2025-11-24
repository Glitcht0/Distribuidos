from tinydb import TinyDB, Query

_db = TinyDB("superbanco.json").table("clock")  # TABELA clock
Clock = Query()

record = _db.get(Clock.type == "logical_clock")
if record:
    logical_clock = record["value"]
else:
    logical_clock = 0
    _db.insert({"type": "logical_clock", "value": logical_clock})

def increment():
    global logical_clock
    logical_clock += 1
    _db.upsert({"type": "logical_clock", "value": logical_clock}, Clock.type == "logical_clock")
    return logical_clock

def update(received_clock):
    global logical_clock
    logical_clock = max(logical_clock, received_clock) + 1
    _db.upsert({"type": "logical_clock", "value": logical_clock}, Clock.type == "logical_clock")
    return logical_clock

def get():
    return logical_clock
