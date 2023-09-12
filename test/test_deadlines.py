import src.deadlines as dl
import datetime


def test_init() -> None:
    d = dl.Deadline(("CW1", "F28PL", datetime.datetime.strptime("2022-11-26 15:30", "%Y-%m-%d %H:%M"), datetime.datetime.strptime("2022-11-27 15:30", "%Y-%m-%d %H:%M"), 40, "EM250", "google.com", "lol this is a test"))
    assert d.name == "CW1"
    assert d.subject == "F28PL"
    assert int(d.start_datetime.timestamp()) == 1669476600
    assert int(d.due_datetime.timestamp()) == 1669563000
    assert d.mark == 40
    assert d.room == "EM250"
    assert d.url == "google.com"
    assert d.info == "lol this is a test"


def test_announce_times_before_start() -> None:
    d_0000 = dl.Deadline(("CW1", "F28PL", datetime.datetime.strptime("2022-10-08 00:00", "%Y-%m-%d %H:%M"), datetime.datetime.strptime("2022-10-26 15:30", "%Y-%m-%d %H:%M"), 0, "", "", ""))
    d_2359 = dl.Deadline(("CW1", "F28PL", datetime.datetime.strptime("2022-10-07 23:59", "%Y-%m-%d %H:%M"), datetime.datetime.strptime("2022-10-26 15:30", "%Y-%m-%d %H:%M"), 0, "", "", ""))
    d_1530 = dl.Deadline(("CW1", "F28PL", datetime.datetime.strptime("2022-10-08 15:30", "%Y-%m-%d %H:%M"), datetime.datetime.strptime("2022-10-26 15:30", "%Y-%m-%d %H:%M"), 0, "", "", ""))
    d_no = dl.Deadline(("CW1", "F28PL", None, None, 0, "", "", ""))

    times_0000 = d_0000.calculate_announce_before_start()
    times_2359 = d_2359.calculate_announce_before_start()
    times_1530 = d_1530.calculate_announce_before_start()
    times_no = d_no.calculate_announce_before_start()

    assert set(times_0000) == {d_0000.timezone.localize(datetime.datetime(2022, 10, 6, 18, 0)), d_0000.timezone.localize(datetime.datetime(2022, 10, 7, 18, 0))}
    assert set(times_2359) == {d_2359.timezone.localize(datetime.datetime(2022, 10, 6, 18, 0)), d_2359.timezone.localize(datetime.datetime(2022, 10, 7, 18, 0))}
    assert set(times_1530) == {d_1530.timezone.localize(datetime.datetime(2022, 10, 7, 15, 30)), d_1530.timezone.localize(datetime.datetime(2022, 10, 8, 15, 0))}
    assert set(times_no) == set()


def test_announce_times_before_due() -> None:
    d_0000 = dl.Deadline(("CW1", "F28PL", None, datetime.datetime.strptime("2022-10-8 00:00", "%Y-%m-%d %H:%M"), 0, "", "", ""))
    d_2359 = dl.Deadline(("CW1", "F28PL", None, datetime.datetime.strptime("2022-10-7 23:59", "%Y-%m-%d %H:%M"), 0, "", "", ""))
    d_1530 = dl.Deadline(("CW1", "F28PL", None, datetime.datetime.strptime("2022-10-8 15:30", "%Y-%m-%d %H:%M"), 0, "", "", ""))
    d_no = dl.Deadline(("CW1", "F28PL", None, None, 0, "", "", ""))

    times_0000 = d_0000.calculate_announce_before_due()
    times_2359 = d_2359.calculate_announce_before_due()
    times_1530 = d_1530.calculate_announce_before_due()
    times_no = d_no.calculate_announce_before_due()

    assert set(times_0000) == {d_0000.timezone.localize(datetime.datetime(2022, 10, 6, 18, 0)), d_0000.timezone.localize(datetime.datetime(2022, 10, 7, 18, 0))}
    assert set(times_2359) == {d_2359.timezone.localize(datetime.datetime(2022, 10, 6, 18, 0)), d_2359.timezone.localize(datetime.datetime(2022, 10, 7, 18, 0))}
    assert set(times_1530) == {d_1530.timezone.localize(datetime.datetime(2022, 10, 7, 15, 30)), d_1530.timezone.localize(datetime.datetime(2022, 10, 8, 15, 0))}
    assert set(times_no) == set()


def test_due_in_() -> None:
    d_due_in_past = dl.Deadline(("CW1", "F28PL", None, datetime.datetime.now() - datetime.timedelta(seconds=100), 0, "", "", ""))
    d_due_in_future = dl.Deadline(("CW1", "F28PL", None, datetime.datetime.now() + datetime.timedelta(seconds=100), 0, "", "", ""))
    d_not_due = dl.Deadline(("CW1", "F28PL", None, None, 0, "", "", ""))
    assert d_due_in_past.due_in_past()
    assert not d_due_in_past.due_in_future()

    assert not d_due_in_future.due_in_past()
    assert d_due_in_future.due_in_future()

    assert d_not_due.due_in_future()
    assert not d_not_due.due_in_past()

# def test_format_for_embed() -> None:
#     d_no_info = dl.Deadline({"CW1", "F28PL", "", "2022-11-26 15:30", 0, "", "", ""})
#     embed = discord.Embed(title="CW1 | F28PL", url="", color=0xeb0000)
#     embed.add_field(name="Due", value="<t:1669476600:F>\n<t:1669476600:R>", inline=False)
#     assert embed.fields[0].__getattr__() == d_no_info.format_for_embed().fields[0].__getattr__()


def test_dt() -> None:
    a = dl.Deadline(("1", "1", None, datetime.datetime.strptime("2022-10-26 15:30", "%Y-%m-%d %H:%M"), 0, "", "", ""))
    assert dl.dt(a.due_datetime, "f") == "<t:1666794600:f>"
    assert dl.dt(a.due_datetime, "R") == "<t:1666794600:R>"


def test_date_exists() -> None:
    a = dl.Deadline(("1", "1", None, None, 0, "", "", ""))
    b = dl.Deadline(("1", "1", datetime.datetime.strptime("2022-10-26 15:30", "%Y-%m-%d %H:%M"), datetime.datetime.strptime("2022-10-27 15:30", "%Y-%m-%d %H:%M"), 0, "", "", ""))

    assert int(a.get_due_date_if_exsits().timestamp()) == int(datetime.datetime.now().timestamp() + 60 * 60 * 24 * 365 * 100)
    assert a.get_start_date_if_exsits().timestamp() == 0.0

    assert b.get_start_date_if_exsits().timestamp() == 1666794600
    assert b.get_due_date_if_exsits().timestamp() == 1666881000
