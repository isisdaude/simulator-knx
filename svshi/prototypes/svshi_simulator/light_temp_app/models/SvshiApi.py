class SvshiApi:
    def __init__(self):
        pass

    def get_time(self) -> int:
        """
        get the machine's time (ex 1649865437 for Wed Apr 13 15:57:17 2022 UTC)
        :returns the current UNIX time of the machine
        """
        pass

    def get_hour_of_the_day(self) -> int:
        """
        get the machine's hour in 24 hours format (return is between 0 and 23)
        example : 15 for Wed Apr 13 15:57:17 2022 UTC
        :returns the current hour based on the machine's time
        """
        pass
