import os
import json
from pathlib import Path

from rich.table import Table
from src.utils.constants import ProjectPaths
from src.exceptions import ProfilesNotFoundError, ProfileAlreadyExistsError


class ProfileManager:
    COMMENTS_FILE_PATH = ProjectPaths.profiles_data_path / "comments_for_users.json"

    @staticmethod
    def sort_profiles(profiles_list: list[str]) -> list[str]:
        profiles_list_str = [str(p) for p in profiles_list]

        numeric_profiles = [p for p in profiles_list_str if p.isdigit()]
        non_numeric_users = [p for p in profiles_list_str if not any(char.isdigit() for char in p)]
        numeric_profiles.sort(key=int)
        non_numeric_users.sort()

        profiles_list_sorted = numeric_profiles + non_numeric_users
        return profiles_list_sorted

    @staticmethod
    def get_profile_welcome_page_path(profile_name: str | int) -> Path:
        profile_name = str(profile_name)
        template_welcome_page_path = ProjectPaths.assets_path / "welcome_page_template.html"
        profile_welcome_page_path = ProjectPaths.profiles_path / profile_name / "Default" / "welcome.html"

        with open(template_welcome_page_path, 'r') as template_file:
            template_content = template_file.read()

        profile_page_content = template_content.replace("{{ profile_name }}", profile_name)

        with open(profile_welcome_page_path, 'w') as profile_page_file:
            profile_page_file.write(profile_page_content)

        return profile_welcome_page_path

    @classmethod
    def get_profile_comment(cls, profile_name: str | int) -> str:
        profile_name = str(profile_name)

        if not cls.COMMENTS_FILE_PATH.exists():
            cls.COMMENTS_FILE_PATH.write_text("{}", encoding="utf-8")

        with open(cls.COMMENTS_FILE_PATH, 'r', encoding="utf-8") as f:
            comments: dict[str, str] = json.load(f)

        return comments.get(profile_name, '')

    @classmethod
    def set_profile_comment(cls, profile_name: str | int, new_comment: str | int) -> None:
        profile_name = str(profile_name)
        new_comment = str(new_comment)

        if not cls.COMMENTS_FILE_PATH.exists():
            cls.COMMENTS_FILE_PATH.write_text("{}", encoding="utf-8")

        with open(cls.COMMENTS_FILE_PATH, 'r', encoding="utf-8") as f:
            comments: dict[str, str] = json.load(f)

        comments[profile_name] = new_comment

        cls.COMMENTS_FILE_PATH.write_text(
            json.dumps(comments, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )

    @classmethod
    def get_sorted_profiles_list(cls) -> list[str] | None:
        profiles = [p.name for p in ProjectPaths.profiles_path.iterdir()]
        return cls.sort_profiles(profiles)

    @classmethod
    def get_profiles_table(cls) -> Table | None:
        profiles_list = cls.get_sorted_profiles_list()

        if not profiles_list:
            raise ProfilesNotFoundError()

        table = Table(style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Comment", style="green")

        for profile_name in profiles_list:
            comment = cls.get_profile_comment(profile_name)
            table.add_row(profile_name, comment)

        return table

    @classmethod
    def get_highest_numeric_profile_name(cls) -> int:
        existing_profile_names = cls.get_sorted_profiles_list()

        highest_existing_numeric_name = 0
        for name in existing_profile_names:
            try:
                num = int(name)
                if num > highest_existing_numeric_name:
                    highest_existing_numeric_name = num
            except ValueError:
                continue

        return highest_existing_numeric_name

    @classmethod
    def create_profile(cls, profile_name: str | int) -> None:
        profile_name = str(profile_name)
        profile_path = ProjectPaths.profiles_path / profile_name

        if profile_path.exists():
            os.makedirs(profile_path / "Default" / "Extensions", exist_ok=True)  # In case  structure is missing
            raise ProfileAlreadyExistsError()

        os.makedirs(profile_path / "Default" / "Extensions")
