import os
import datetime
import time


class DumpHelper:
    # 最大日志保留小时数
    MAX_RETAIN_HOURS = 5

    def __init__(self, to_dir, file_name_prefix, file_name_suffix):
        self.to_dir = to_dir
        self.file_name_prefix = file_name_prefix
        self.file_name_suffix = file_name_suffix
        self.current_hour = None
        self.hour_list = []

    def _create_hourly_directory(self):
        os.makedirs(self._get_hourly_dir_path(), exist_ok=True)

    @staticmethod
    def _get_current_hour():
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d-%H")

    def _get_file_path(self):
        timestamp = time.time()
        hourly_dir_path = self._get_hourly_dir_path()
        return f"{hourly_dir_path}/{self.file_name_prefix}{timestamp}{self.file_name_suffix}"

    def _get_hourly_dir_path(self):
        return os.path.join(self.to_dir, self.current_hour)

    def _cleanup_old_directories(self):
        print("[debug] hour list: ", self.hour_list)
        sorted_hour_list = sorted(self.hour_list)
        print("[debug] sorted hour list: ", sorted_hour_list)
        if len(sorted_hour_list) > self.MAX_RETAIN_HOURS:
            oldest_hour_list = sorted_hour_list[:len(
                sorted_hour_list) - self.MAX_RETAIN_HOURS]
            for hour in oldest_hour_list:
                to_delete_directory = os.path.join(self.to_dir, hour)
                if os.path.isdir(to_delete_directory):
                    for file_name in os.listdir(to_delete_directory):
                        to_delete_file = os.path.join(
                            to_delete_directory, file_name)
                        print("[debug] delete file: ", to_delete_file)
                        os.remove(to_delete_file)
                    os.rmdir(to_delete_directory)
                    self.hour_list.remove(hour)

    def dump(self, content):
        cur_hour = self._get_current_hour()
        if cur_hour != self.current_hour:
            self.current_hour = cur_hour
            self.hour_list.append(cur_hour)
            print("hour: ", cur_hour)
            self._create_hourly_directory()
            self._cleanup_old_directories()

        to_file = self._get_file_path()
        with open(to_file, "wb+") as f:
            f.write(content)
        print("[debug] write to file ", to_file, " successfully!")
