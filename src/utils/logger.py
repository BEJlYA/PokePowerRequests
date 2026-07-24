import json
import logging
import logging.handlers
from datetime import datetime

from src.utils.path import get_app_data_dir


class UniversalLogger:
    def __init__(self):
        self.log_dir = get_app_data_dir() / 'logs'
        self.max_file_size = 5 * 1024 * 1024
        self.log_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger('PPRCheat')
        self.logger.setLevel(logging.DEBUG)

        self.logger.handlers.clear()

        self.formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-2s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # ============ ХЕНДЛЕР ДЛЯ ПОСЛЕДНЕЙ СЕССИИ ============
        self.last_session_file = self.log_dir / "session_last.log"
        with open(self.last_session_file, 'w', encoding='utf-8') as f:
            f.write("")

        last_handler = logging.FileHandler(
            filename=self.last_session_file,
            mode='a',
            encoding='utf-8'
        )
        last_handler.setFormatter(self.formatter)
        last_handler.setLevel(logging.INFO)
        self.logger.addHandler(last_handler)

        # ============ ХЭНДЛЕРЫ ЗА ПОСЛЕДНИЕ 3 СУТОК ============
        self.sessions_file = self.log_dir / "sessions.json"
        self.sessions = self.load_sessions()

        self.current_session_date = datetime.now().strftime('%Y%m%d')
        self.add_current_session()
        self.setup_file_handlers()
        self.cleanup_old_sessions()

    def load_sessions(self):
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_sessions(self):
        with open(self.sessions_file, 'w', encoding='utf-8') as f:
            json.dump(self.sessions, f, ensure_ascii=False, indent=2)

    def add_current_session(self):
        current_date = self.current_session_date

        if current_date not in self.sessions:
            self.sessions.append(current_date)

        self.sessions.sort(reverse=True)
        self.save_sessions()

    def get_session_files(self):
        session_files = []

        for session_date in self.sessions[:3]:
            log_file = self.log_dir / f"session_{session_date}.log"
            session_files.append(log_file)

        return session_files

    def setup_file_handlers(self):
        session_files = self.get_session_files()

        for log_file in session_files:
            handler = logging.handlers.RotatingFileHandler(
                filename=log_file,
                maxBytes=self.max_file_size,
                backupCount=1,
                encoding='utf-8'
            )
            handler.setFormatter(self.formatter)
            self.logger.addHandler(handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def cleanup_old_sessions(self):
        all_session_files = list(self.log_dir.glob("session_*.log*"))

        keep_sessions = set(self.sessions[:3])

        for log_file in all_session_files:
            try:
                date_str = log_file.stem.replace('session_', '')
                if date_str not in keep_sessions:
                    log_file.unlink()
                    self.info(f"Old session log deleted: {log_file.name}")
            except:
                continue

        existing_sessions = []
        for session_date in self.sessions:
            log_file = self.log_dir / f"session_{session_date}.log"
            if log_file.exists():
                existing_sessions.append(session_date)

        self.sessions = existing_sessions[:3]
        self.save_sessions()

    def debug(self, message, extra_data=None):
        full_message = self.format_message(message, extra_data)
        self.logger.debug(full_message)

    def info(self, message, extra_data=None):
        full_message = self.format_message(message, extra_data)
        self.logger.info(full_message)

    def warning(self, message, extra_data=None):
        full_message = self.format_message(message, extra_data)
        self.logger.warning(full_message)

    def error(self, message, extra_data=None):
        full_message = self.format_message(message, extra_data)
        self.logger.error(full_message)

    def critical(self, message, extra_data=None):
        full_message = self.format_message(message, extra_data)
        self.logger.critical(full_message)

    @staticmethod
    def format_message(message, extra_data):
        if extra_data:
            return f"{message} | Extra: {extra_data}"
        return message

    def bot_start(self, settings_info=None):
        self.info(
            "BOT_STARTED", settings_info
        )

    def bot_stop(self, reason=None, des_reason=None, traceback=None):
        reason = f" | {reason}" if reason else ""
        des_reason = f" | {des_reason}" if des_reason else ""
        traceback = f" | {traceback}" if traceback else " |"

        self.info(
            f"BOT_STOPPED{reason}{des_reason}{traceback}"
        )

    def battle_start(self, enemy_num, enemy_name, enemy_level, enemy_shiny=0):
        enemy_shiny = f" | Shiny: +" if enemy_shiny == 1 else ""

        self.info(
            f"BATTLE_START | Enemy: #{enemy_num} '{enemy_name}' | Level: {enemy_level}{enemy_shiny}"
        )

    def battle_action(self, action_type, description):
        self.info(
            f"BATTLE_ACTION | {action_type} | Description: {description}"
        )

    def team_action(self, action_type, description):
        self.info(
            f"TEAM_ACTION | {action_type} | Description: {description}"
        )

    def inventory_change(self, name, count=None, change_type=True):
        change_type = 'ADD' if change_type else 'REMOVE'
        count = f" | Count: {count}" if count else ""

        self.info(
            f"INVENTORY | {change_type} | {name}{count}"
        )

    def task_progress(self, task_type, name_task, remainder, gender=None):
        gender = f" | Gender: {gender}" if gender else ""

        self.info(
            f"TASK_PROGRESS | {task_type} | {name_task} | {remainder}{gender}"
        )

    def pokecenter(self, action, reason=None):
        self.info(
            f"POKECENTER | {action} | Reason: {reason}"
        )

    def get_session_info(self):
        session_info = []

        for session_date in self.sessions[:3]:
            log_file = self.log_dir / f"session_{session_date}.log"
            if log_file.exists():
                size_mb = log_file.stat().st_size / (1024 * 1024)
                session_info.append({
                    'date': session_date,
                    'filename': f"session_{session_date}.log",
                    'size_mb': round(size_mb, 2),
                    'modified': datetime.fromtimestamp(log_file.stat().st_mtime)
                })

        return session_info

    def get_log_directory(self):
        return self.log_dir
