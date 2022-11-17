import src.deadlines as dl
import datetime
import pytz

def test_init() -> None:
    d = dl.Deadline({"name":"CW1", "subject":"F28PL", "start-datetime" : "2022-10-08 00:00", "due-datetime" : "2022-10-26 15:30", "mark":0.4, "room":"EM250", "url":"google.com", "info":"lol this is a test"})
    assert d.name == "CW1"
    assert d.subject == "F28PL"
    assert d.mark == 40
    assert d.room == "EM250"
    assert d.url == "google.com"
    assert d.info == "lol this is a test"

def test_announce_times_before_start() -> None:
    d_0000 = dl.Deadline({"name":"CW1", "subject":"F28PL", "start-datetime" : "2022-10-08 00:00", "due-datetime" : "2022-10-26 15:30", "mark":0, "room":"", "url":"", "info":""})
    d_2359 = dl.Deadline({"name":"CW1", "subject":"F28PL", "start-datetime" : "2022-10-07 23:59", "due-datetime" : "2022-10-26 15:30", "mark":0, "room":"", "url":"", "info":""})
    d_1530 = dl.Deadline({"name":"CW1", "subject":"F28PL", "start-datetime" : "2022-10-08 15:30", "due-datetime" : "2022-10-26 15:30", "mark":0, "room":"", "url":"", "info":""})
    d_no = dl.Deadline({"name":"CW1", "subject":"F28PL", "start-datetime" : "", "due-datetime" : "", "mark":0, "room":"", "url":"", "info":""})

    times_0000 = d_0000.calculate_announce_before_start()
    times_2359 = d_2359.calculate_announce_before_start()
    times_1530 = d_1530.calculate_announce_before_start()
    times_no = d_no.calculate_announce_before_start()

    assert set(times_0000) == {d_0000.timezone.localize(datetime.datetime(2022, 10, 6, 18, 0)), d_0000.timezone.localize(datetime.datetime(2022, 10, 7, 18, 0))}
    assert set(times_2359) == {d_2359.timezone.localize(datetime.datetime(2022, 10, 6, 18, 0)), d_2359.timezone.localize(datetime.datetime(2022, 10, 7, 18, 0))}
    assert set(times_1530) == {d_1530.timezone.localize(datetime.datetime(2022, 10, 7, 15, 30)), d_1530.timezone.localize(datetime.datetime(2022, 10, 8, 15, 0))}
    assert set(times_no) == set()

def test_announce_times_before_due() -> None:
    d_0000 = dl.Deadline({"name":"CW1", "subject":"F28PL", "start-datetime" : "", "due-datetime" : "2022-10-8 00:00", "mark":0, "room":"", "url":"", "info":""})
    d_2359 = dl.Deadline({"name":"CW1", "subject":"F28PL", "start-datetime" : "", "due-datetime" : "2022-10-7 23:59", "mark":0, "room":"", "url":"", "info":""})
    d_1530 = dl.Deadline({"name":"CW1", "subject":"F28PL", "start-datetime" : "", "due-datetime" : "2022-10-8 15:30", "mark":0, "room":"", "url":"", "info":""})
    d_no = dl.Deadline({"name":"CW1", "subject":"F28PL", "start-datetime" : "", "due-datetime" : "", "mark":0, "room":"", "url":"", "info":""})

    times_0000 = d_0000.calculate_announce_before_due()
    times_2359 = d_2359.calculate_announce_before_due()
    times_1530 = d_1530.calculate_announce_before_due()
    times_no = d_no.calculate_announce_before_due()

    assert set(times_0000) == {d_0000.timezone.localize(datetime.datetime(2022, 10, 6, 18, 0)), d_0000.timezone.localize(datetime.datetime(2022, 10, 7, 18, 0))}
    assert set(times_2359) == {d_2359.timezone.localize(datetime.datetime(2022, 10, 6, 18, 0)), d_2359.timezone.localize(datetime.datetime(2022, 10, 7, 18, 0))}
    assert set(times_1530) == {d_1530.timezone.localize(datetime.datetime(2022, 10, 7, 15, 30)), d_1530.timezone.localize(datetime.datetime(2022, 10, 8, 15, 0))}
    assert set(times_no) == set()


def test_due_in_() -> None:
    d_due_in_past = dl.Deadline({"name":"CW1", "subject":"F28PL", "start-datetime" : "", "due-datetime" : datetime.datetime.strftime((datetime.datetime.now() - datetime.timedelta(seconds=100)), "%Y-%m-%d %H:%M"), "mark":0, "room":"", "url":"", "info":""})
    d_due_in_future = dl.Deadline({"name":"CW1", "subject":"F28PL", "start-datetime" : "", "due-datetime" : datetime.datetime.strftime((datetime.datetime.now() + datetime.timedelta(seconds=100)), "%Y-%m-%d %H:%M"), "mark":0, "room":"", "url":"", "info":""})
    d_not_due = dl.Deadline({"name":"CW1", "subject":"F28PL", "start-datetime" : "", "due-datetime" : "", "mark":0, "room":"", "url":"", "info":""})
    assert d_due_in_past.due_in_past()
    assert not d_due_in_past.due_in_future()

    assert not d_due_in_future.due_in_past()
    assert d_due_in_future.due_in_future()

    assert d_not_due.due_in_future()
    assert not d_not_due.due_in_past()


# def test_filter_after() -> None:
#     deadlines = [
#         dl.Deadline({"name":"1", "subject":"1", "start-datetime" : "2022-10-08 00:02", "due-datetime" : "2022-10-26 15:33", "mark":0.4, "room":"", "url":"", "info":""}),
#         dl.Deadline({"name":"1", "subject":"1", "start-datetime" : "2022-10-08 00:01", "due-datetime" : "2022-10-26 15:32", "mark":0.4, "room":"", "url":"", "info":""}),
#         dl.Deadline({"name":"1", "subject":"1", "start-datetime" : "2022-10-08 00:00", "due-datetime" : "2022-10-26 15:31", "mark":0.4, "room":"", "url":"", "info":""})
#     ]
#     dl.filter_due_after(deadlines, deadlines[0].str_to_datetime("2022-10-08 00:00"))