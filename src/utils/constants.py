from dataclasses import dataclass
from sys import platform
from pathlib import Path


def find_project_root(current_path: Path) -> Path:
    for parent in current_path.parents:
        if (parent / "requirements.txt").exists():
            return parent
    
    raise Exception('Failed to find project root, make sure "requirements.txt" file exists')


@dataclass(frozen=True)
class ProjectPaths:
    root_path: Path = find_project_root(Path(__file__).resolve())

    automation_path = root_path / "automation"
    data_path: Path = root_path / "data"
    logs_path: Path = data_path / "logs"
    profiles_path: Path = data_path / "users"
    default_extensions_path: Path = data_path / "default_extensions"

    locales_path: Path = root_path / "src" / "locales"

    driver_name: str = "chromedriver.exe" if platform == "win32" else "chromedriver"
    chromedriver_path: Path = data_path / "chromedrivers" / driver_name
    chrome_path: str = (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if platform == "win32"
        else "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    )
