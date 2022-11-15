"""
:module:    test_io_time.py

:author:    GM (genuinemerit @ pm.me)
"""
from pprint import pprint as pp         # noqa: F401
from io_time import TimeIO
TI = TimeIO("time_data")

class TestTimeIO(object):
    """Class for testing Calendar-related data and methods.
    """
    def __init__(self):
        print(TI.COLOR.YELLOW)
        print("Commencing test")
        print(TI.COLOR.DARKCYAN)
        pp(TI.CAL)
        print(TI.COLOR.GREEN + TI.COLOR.BOLD + "bold green text")
        print(TI.COLOR.END)

    def test_cal(self):
        print(TI.COLOR.RED + "Stars" + TI.COLOR.END)
        pp(TI.CAL.STARS)
        print(TI.COLOR.RED + "Planets" + TI.COLOR.END)
        pp(TI.CAL.PLANETS)
        print(TI.COLOR.RED + "Moons" + TI.COLOR.END)
        pp(TI.CAL.MOONS)
        print(TI.COLOR.RED + "Parts of Time" + TI.COLOR.END)
        pp(TI.CAL.PARTS)
        print(TI.COLOR.RED + "Seasons" + TI.COLOR.END)
        pp(TI.CAL.SEASON)
        print(TI.COLOR.RED + "Calendars" + TI.COLOR.END)
        pp(TI.CAL.CALENDAR)
        print(TI.COLOR.RED + "Calendar Names" + TI.COLOR.END)
        for cal_id in list(TI.CAL.CALENDAR.keys()):
            print(cal_id +
                  "\t" + TI.CAL.CALENDAR[cal_id]["name"] +
                  "\t" + TI.CAL.CALENDAR[cal_id]["desc"])
        print(TI.COLOR.END)

    def test_file(self):
        print(TI.COLOR.RED + "File Name" + TI.COLOR.END)
        print(TI.set_file_name("time_data"))
        print(TI.COLOR.RED + "Test getting file" + TI.COLOR.END)
        TI.get_time_data("time_data")
        print(TI.COLOR.RED + "Test setting file" + TI.COLOR.END)
        TI.set_time_data("time_data")

    def test_congruence(self):
        print(TI.COLOR.RED + "Testing congruence calculations" + TI.COLOR.END)
        print(TI.COLOR.YELLOW)
        for p1 in list(TI.CAL.PLANETS["Faton"].keys()):
            for p2 in list(TI.CAL.PLANETS["Faton"].keys()):
                if p1 != p2:
                    print(p1 + " orbit: " +
                          str(int(round(TI.CAL.PLANETS["Faton"][p1]["orbit"]))) +
                          " days / " + 
                          p2 + " orbit: " +
                          str(int(round(TI.CAL.PLANETS["Faton"][p2]["orbit"]))) +
                          " days") 
                    print(p1 + "/ "  + p2 + " orbital congruence is every: " +
                          str(int(round(TI.orbital_congruence(
                            TI.CAL.PLANETS, "Faton", p1, p2)))) +
                          " days\n")
        print(TI.COLOR.END)

    def test_lunar_phases(self):
        print(TI.COLOR.RED + "Testing lunar phases" + TI.COLOR.END)
        print(TI.COLOR.YELLOW)
        for moon in list(TI.CAL.MOONS["Gavor"].keys()):
            print("\n" + moon + " orbit: " +
                    str(int(round(TI.CAL.MOONS["Gavor"][moon]["orbit"]))) + " days") 
            print(moon + " phases:")
            pp(TI.lunar_phases(TI.CAL.MOONS, "Gavor", moon))
        print(TI.COLOR.END)

    def test_year_zero(self):
        print(TI.COLOR.RED + "Testing year zero" + TI.COLOR.END)
        print(TI.COLOR.YELLOW)
        for cal_nm in list(TI.CAL.CALENDAR.keys()):
        # for cal_nm in ["SAG", "AG"]:
            pp(TI.year_zero(cal_nm))
        print(TI.COLOR.END)


if __name__ == '__main__':
    TTI = TestTimeIO()
    TTI.test_cal()
    TTI.test_file()
    TTI.test_congruence()
    TTI.test_lunar_phases()
    TTI.test_year_zero()
