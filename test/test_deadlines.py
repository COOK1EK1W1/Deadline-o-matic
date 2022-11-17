import src.deadlines as dl

def test_init() -> None:
    d = dl.Deadline({"name":"CW1", "subject":"F28PL", "start-datetime" : "2022-10-08 00:00", "due-datetime" : "2022-10-26 15:30", "mark":0.4, "room":"EM250", "url":"google.com", "info":"lol this is a test"})
    assert d.name == "CW1"
    assert d.subject == "F28PL"
    assert d.mark == 40
    assert d.room == "EM250"
    assert d.url == "google.com"
    assert d.info == "lol this is a test"

# def test_filter_after() -> None:
#     deadlines = [
#         dl.Deadline({"name":"1", "subject":"1", "start-datetime" : "2022-10-08 00:02", "due-datetime" : "2022-10-26 15:33", "mark":0.4, "room":"", "url":"", "info":""}),
#         dl.Deadline({"name":"1", "subject":"1", "start-datetime" : "2022-10-08 00:01", "due-datetime" : "2022-10-26 15:32", "mark":0.4, "room":"", "url":"", "info":""}),
#         dl.Deadline({"name":"1", "subject":"1", "start-datetime" : "2022-10-08 00:00", "due-datetime" : "2022-10-26 15:31", "mark":0.4, "room":"", "url":"", "info":""})
#     ]
#     dl.filter_due_after(deadlines, deadlines[0].str_to_datetime("2022-10-08 00:00"))