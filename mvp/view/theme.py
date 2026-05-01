from dataclasses import dataclass
from typing import Tuple

RGB = Tuple[int, int, int]


@dataclass(frozen=True)
class Theme:
    name: str

    grid_sel_bg: RGB
    grid_sel_fg: RGB

    pgrid_sel_bg: RGB
    pgrid_sel_fg: RGB

    log_bg: RGB
    log_fg: RGB

    log_search_bg: RGB
    log_search_fg: RGB

    log_match_bg: RGB
    log_match_fg: RGB

    log_current_match_bg: RGB
    log_current_match_fg: RGB

    accent: RGB
    accent_hover: RGB
    accent_pressed: RGB


THEMES: dict[str, Theme] = {
    "Forest": Theme(
        name="Forest",
        grid_sel_bg=(66, 111, 66),
        grid_sel_fg=(0, 0, 0),
        pgrid_sel_bg=(66, 111, 66),
        pgrid_sel_fg=(0, 0, 0),
        log_bg=(78, 78, 78),
        log_fg=(0, 255, 0),
        log_search_bg=(58, 58, 58),
        log_search_fg=(245, 222, 179),
        log_match_bg=(255, 255, 0),
        log_match_fg=(0, 0, 0),
        log_current_match_bg=(255, 120, 0),
        log_current_match_fg=(255, 255, 255),
        accent=(76, 175, 80),
        accent_hover=(102, 197, 106),
        accent_pressed=(46, 125, 50),
    ),
    "Ocean": Theme(
        name="Ocean",
        grid_sel_bg=(58, 107, 140),
        grid_sel_fg=(255, 255, 255),
        pgrid_sel_bg=(58, 107, 140),
        pgrid_sel_fg=(255, 255, 255),
        log_bg=(30, 45, 61),
        log_fg=(135, 206, 235),
        log_search_bg=(22, 34, 48),
        log_search_fg=(255, 215, 0),
        log_match_bg=(255, 215, 0),
        log_match_fg=(0, 0, 0),
        log_current_match_bg=(0, 150, 255),
        log_current_match_fg=(255, 255, 255),
        accent=(41, 128, 185),
        accent_hover=(52, 152, 219),
        accent_pressed=(30, 100, 150),
    ),
    "Monokai": Theme(
        name="Monokai",
        grid_sel_bg=(73, 72, 62),
        grid_sel_fg=(248, 248, 242),
        pgrid_sel_bg=(73, 72, 62),
        pgrid_sel_fg=(248, 248, 242),
        log_bg=(39, 40, 34),
        log_fg=(166, 226, 46),
        log_search_bg=(30, 31, 26),
        log_search_fg=(230, 219, 116),
        log_match_bg=(230, 219, 116),
        log_match_fg=(0, 0, 0),
        log_current_match_bg=(249, 38, 114),
        log_current_match_fg=(255, 255, 255),
        accent=(166, 226, 46),
        accent_hover=(192, 240, 88),
        accent_pressed=(130, 180, 30),
    ),
    "Solarized": Theme(
        name="Solarized",
        grid_sel_bg=(7, 54, 66),
        grid_sel_fg=(147, 161, 161),
        pgrid_sel_bg=(7, 54, 66),
        pgrid_sel_fg=(147, 161, 161),
        log_bg=(0, 43, 54),
        log_fg=(133, 153, 0),
        log_search_bg=(0, 31, 39),
        log_search_fg=(181, 137, 0),
        log_match_bg=(181, 137, 0),
        log_match_fg=(0, 0, 0),
        log_current_match_bg=(38, 139, 210),
        log_current_match_fg=(253, 246, 227),
        accent=(42, 161, 152),
        accent_hover=(56, 185, 176),
        accent_pressed=(32, 130, 122),
    ),
    "Nord": Theme(
        name="Nord",
        grid_sel_bg=(67, 76, 94),
        grid_sel_fg=(229, 233, 240),
        pgrid_sel_bg=(67, 76, 94),
        pgrid_sel_fg=(229, 233, 240),
        log_bg=(46, 52, 64),
        log_fg=(163, 190, 140),
        log_search_bg=(36, 40, 50),
        log_search_fg=(235, 203, 139),
        log_match_bg=(235, 203, 139),
        log_match_fg=(46, 52, 64),
        log_current_match_bg=(136, 192, 208),
        log_current_match_fg=(46, 52, 64),
        accent=(136, 192, 208),
        accent_hover=(143, 188, 187),
        accent_pressed=(94, 129, 172),
    ),
    "Dracula": Theme(
        name="Dracula",
        grid_sel_bg=(68, 71, 90),
        grid_sel_fg=(248, 248, 242),
        pgrid_sel_bg=(68, 71, 90),
        pgrid_sel_fg=(248, 248, 242),
        log_bg=(40, 42, 54),
        log_fg=(80, 250, 123),
        log_search_bg=(30, 31, 42),
        log_search_fg=(241, 250, 140),
        log_match_bg=(241, 250, 140),
        log_match_fg=(40, 42, 54),
        log_current_match_bg=(255, 121, 198),
        log_current_match_fg=(248, 248, 242),
        accent=(189, 147, 249),
        accent_hover=(210, 168, 255),
        accent_pressed=(139, 97, 199),
    ),
    "Sakura": Theme(
        name="Sakura",
        grid_sel_bg=(183, 110, 121),
        grid_sel_fg=(255, 255, 255),
        pgrid_sel_bg=(183, 110, 121),
        pgrid_sel_fg=(255, 255, 255),
        log_bg=(48, 38, 42),
        log_fg=(245, 189, 200),
        log_search_bg=(38, 28, 32),
        log_search_fg=(255, 218, 185),
        log_match_bg=(255, 182, 193),
        log_match_fg=(48, 38, 42),
        log_current_match_bg=(219, 112, 147),
        log_current_match_fg=(255, 255, 255),
        accent=(219, 112, 147),
        accent_hover=(238, 140, 170),
        accent_pressed=(180, 82, 117),
    ),
    "Cyberpunk": Theme(
        name="Cyberpunk",
        grid_sel_bg=(30, 0, 50),
        grid_sel_fg=(0, 255, 255),
        pgrid_sel_bg=(30, 0, 50),
        pgrid_sel_fg=(0, 255, 255),
        log_bg=(15, 5, 25),
        log_fg=(0, 255, 170),
        log_search_bg=(10, 0, 18),
        log_search_fg=(255, 0, 255),
        log_match_bg=(255, 0, 255),
        log_match_fg=(0, 0, 0),
        log_current_match_bg=(0, 255, 255),
        log_current_match_fg=(0, 0, 0),
        accent=(0, 255, 255),
        accent_hover=(80, 255, 255),
        accent_pressed=(0, 180, 180),
    ),
}

DEFAULT_THEME = "Forest"
SYSTEM_THEME_NAME = "System"

_current: Theme = THEMES[DEFAULT_THEME]
_system_mode: bool = False


def _resolve_system_theme() -> str:
    try:
        import wx
        return "Monokai" if wx.SystemSettings.GetAppearance().IsDark() else "Ocean"
    except Exception:
        return DEFAULT_THEME


def get_theme() -> Theme:
    return _current


def set_theme(name: str):
    global _current, _system_mode
    if name == SYSTEM_THEME_NAME:
        _system_mode = True
        _current = THEMES.get(_resolve_system_theme(), THEMES[DEFAULT_THEME])
    else:
        _system_mode = False
        _current = THEMES.get(name, THEMES[DEFAULT_THEME])


def is_system_theme() -> bool:
    return _system_mode


def get_theme_names() -> list[str]:
    return [SYSTEM_THEME_NAME] + list(THEMES.keys())
