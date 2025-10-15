from datetime import datetime, timedelta


class TimeManager:
    @staticmethod
    def get_sleep_seconds_until(target_hour: int, target_minute: int = 0) -> int:
        """Calculates how many seconds are left until the specified time"""
        now = datetime.now()
        target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

        if target_time <= now:
            target_time += timedelta(days=1)

        return int((target_time - now).total_seconds())

    @staticmethod
    def get_current_seconds() -> int:
        """Current time in seconds since the start of the day"""
        return int(datetime.now().timestamp())

    @staticmethod
    def get_timestamp_socket():
        """Returns the current time for a socket connection"""
        time_now = TimeManager.get_current_seconds()
        return str(time_now * 1000)[-7:]

    @staticmethod
    def calculate_time(time_end: str) -> int:
        """Calculates the value of subtracting time from the current moment"""
        time_now = TimeManager.get_current_seconds()
        return (time_now - int(time_end)).total_seconds()

    @staticmethod
    def is_time_in_range(start_hour: int, end_hour: int) -> bool:
        """Checks if the current time is in a range"""
        current_hour = datetime.now().hour
        return start_hour <= current_hour < end_hour
