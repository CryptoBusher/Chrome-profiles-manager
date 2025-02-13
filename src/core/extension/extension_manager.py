import os
import json
import shutil
from pathlib import Path

from src.exceptions import ExtensionNotFoundError, ExtensionAlreadyInstalledError
from src.utils.constants import ProjectPaths


class ExtensionManager:
    @staticmethod
    def __read_manifest_name(manifest_path: Path | str) -> str:
        try:
            with open(manifest_path, 'r', encoding='utf-8') as file:
                manifest = json.load(file)

            return manifest.get("action", {}).get("default_title", "")
        except (json.JSONDecodeError, OSError):
            return ""

    @classmethod
    def __get_extension_name(cls, extension_path: Path | str) -> str:
        extension_path = Path(extension_path)
        
        manifest_path = extension_path / "manifest.json"
        if manifest_path.is_file():
            return cls.__read_manifest_name(manifest_path)

        for subdir in extension_path.iterdir():
            version_path = subdir
            manifest_path = version_path / "manifest.json"
            if manifest_path.is_file():
                return cls.__read_manifest_name(manifest_path)

        return ""
    
    @classmethod
    def get_all_default_extension_names(cls) -> dict[str, str]:
        extensions = {}

        for extension in ProjectPaths.default_extensions_path.iterdir():
            if extension.is_dir():
                extensions[extension.name] = cls.__get_extension_name(extension)

        return extensions

    @classmethod
    def get_profiles_extension_names(cls, profiles_list: list[str | int]) -> dict[str, str]:
        # TODO: refactor to process single profile
        extensions_info = {}

        for profile_name in profiles_list:
            profile_path = ProjectPaths.profiles_path  / str(profile_name) / "Default"
            extensions_path = profile_path / "Extensions"
            extensions_settings_path = profile_path / "Local Extension Settings"

            if not extensions_path.exists() and not extensions_settings_path.exists():
                continue

            if extensions_path.exists():
                for extension in extensions_path.iterdir():
                    if extension.is_dir():
                        name = cls.__get_extension_name(extension)
                        extensions_info[extension.name] = name

            if extensions_settings_path.exists():
                for extension in extensions_settings_path.iterdir():
                    if extension.is_dir():
                        if extensions_info.get(extension.name) is None:
                            extensions_info[extension.name] = ''  # because there is no manifest file

        return extensions_info
    
    @classmethod
    def add_extension_to_profile(cls, profile_name: str | int, ext_id: str, replace: bool = False) -> None:
        profile_name = str(profile_name)
        profile_path = ProjectPaths.profiles_path / profile_name / "Default"
        source_path = ProjectPaths.default_extensions_path / ext_id
        destination_path = profile_path / "Extensions" / ext_id

        if not source_path.is_dir():
            raise ExtensionNotFoundError(ext_id)

        if replace:
            cls.remove_extension_from_profile(profile_name, ext_id)

        if destination_path.is_dir():
            raise ExtensionAlreadyInstalledError()

        shutil.copytree(source_path, destination_path)

    @classmethod
    def remove_extension_from_profile(cls, profile_name: str | int, ext_id: str) -> None:
        profile_path = ProjectPaths.profiles_path  / str(profile_name) / "Default"
        profile_extension_path = profile_path / "Extensions" / ext_id
        profile_extension_settings_path = profile_path / "Local Extension Settings" / ext_id

        extension_found = False

        if profile_extension_path.is_dir():
            shutil.rmtree(profile_extension_path)
            extension_found = True

        if profile_extension_settings_path.is_dir():
            shutil.rmtree(profile_extension_settings_path)

        if not extension_found:
            raise ExtensionNotFoundError(ext_id)
