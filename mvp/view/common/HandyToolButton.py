import wx

from core.processor import Processor
from i18n.translations import t

_HANDY_ITEMS = [
    ("handy_rdir", '{self.get_rdir()}/', True),
    ("handy_ddir", '{self.get_ddir()}/', True),
    ("handy_tdir", '{self.get_tdir()}/', True),
    ("handy_get_sdir", '{self.get_sdir()}/', True),
    ("handy_encrypt", None, False),
    None,
    ("handy_get_data", '{self.get_data("")}', False),
    ("handy_get_data_by_loop", '{self.get_data_by_loop("")}', False),
    ("handy_get_deep_data", '{self.get_deep_data(["",""])}', False),
    None,
    ("handy_str2dict", '{self.str2dict("")}', False),
    ("handy_str2list", '{self.str2list("")}', False),
    ("handy_json2dict", '{self.json2dict("")}', False),
    ("handy_json_dumps", '{json.dumps()}', False),
    ("handy_json_loads", '{json.loads("")}', False),
    ("handy_prop2dict", '{self.prop2dict("")}', False),
    ("handy_feed_tpl", '{self.feed_tpl("", {})}', False),
    None,
    ("handy_date_str", '{self.get_now_str()}', False),
    ("handy_os_sep", '{os.sep}', False),
]

_ENCRYPT_PREFIX = '{self.decrypt("'
_ENCRYPT_SUFFIX = '")}'


class HandyToolButton(wx.Button):
    """Reusable button that pops a handy-tools snippet menu.

    Constructor params:
        parent       -- wx parent window
        get_value    -- callable() -> str|None  (return current text, or None to skip)
        set_value    -- callable(str) -> None   (write back the modified text)
        on_change    -- optional callable() after any modification
        extra_items  -- optional list of (i18n_key, handler) appended after a separator
    """

    def __init__(self, parent, get_value=None, set_value=None, on_change=None, extra_items=None, **kwargs):
        kwargs.setdefault("label", t("btn_handy_tools"))
        super().__init__(parent, wx.ID_ANY, **kwargs)
        self.SetMinSize((40, 28))
        self.SetToolTip(t("tip_handy_tools"))

        self._get_value = get_value
        self._set_value = set_value
        self._on_change = on_change
        self._extra_items = extra_items or []

        self.Bind(wx.EVT_BUTTON, self._on_clicked)

    def bind_accessors(self, get_value, set_value, on_change=None, extra_items=None):
        """Wire up callbacks after construction.

        extra_items can be a list of (i18n_key, handler) or a callable that
        returns such a list (evaluated each time the menu opens).
        """
        self._get_value = get_value
        self._set_value = set_value
        if on_change is not None:
            self._on_change = on_change
        if extra_items is not None:
            self._extra_items = extra_items

    def _on_clicked(self, _evt):
        menu = wx.Menu()

        for item in _HANDY_ITEMS:
            if item is None:
                menu.AppendSeparator()
                continue
            key, snippet, put2first = item
            menu_id = wx.NewId()
            menu.Append(menu_id, t(key))
            if snippet is None:
                self.Bind(wx.EVT_MENU, self._on_encrypt_toggle, id=menu_id)
            else:
                self.Bind(wx.EVT_MENU,
                          lambda e, s=snippet, p=put2first: self._insert_snippet(s, p),
                          id=menu_id)

        extras = self._extra_items() if callable(self._extra_items) else self._extra_items
        if extras:
            menu.AppendSeparator()
            for key, handler in extras:
                menu_id = wx.NewId()
                menu.Append(menu_id, t(key))
                self.Bind(wx.EVT_MENU, handler, id=menu_id)

        self.PopupMenu(menu)
        menu.Destroy()

    def _insert_snippet(self, snippet: str, put2first: bool):
        current = self._get_value()
        if current is None:
            return
        new_val = (snippet + current) if put2first else (current + snippet)
        self._set_value(new_val)
        if self._on_change:
            self._on_change()

    def _on_encrypt_toggle(self, _evt):
        current = self._get_value()
        if current is None or not isinstance(current, str):
            return
        if current.startswith(_ENCRYPT_PREFIX) and current.endswith(_ENCRYPT_SUFFIX):
            inner = current[len(_ENCRYPT_PREFIX):-len(_ENCRYPT_SUFFIX)]
            self._set_value(Processor.decrypt_pwd(inner))
        else:
            self._set_value(_ENCRYPT_PREFIX + Processor.encrypt_pwd(current) + _ENCRYPT_SUFFIX)
        if self._on_change:
            self._on_change()


def show_handy_menu(window, get_value, set_value, extra_items=None):
    """Show the handy-tools popup menu on any wx.Window.

    Standalone function for callers that already have a button (e.g. wxGlade-managed)
    and just need the menu logic.
    """
    menu = wx.Menu()

    def _insert(snippet, put2first):
        current = get_value()
        if current is None:
            return
        new_val = (snippet + current) if put2first else (current + snippet)
        set_value(new_val)

    def _encrypt_toggle(_evt):
        current = get_value()
        if current is None or not isinstance(current, str):
            return
        if current.startswith(_ENCRYPT_PREFIX) and current.endswith(_ENCRYPT_SUFFIX):
            inner = current[len(_ENCRYPT_PREFIX):-len(_ENCRYPT_SUFFIX)]
            set_value(Processor.decrypt_pwd(inner))
        else:
            set_value(_ENCRYPT_PREFIX + Processor.encrypt_pwd(current) + _ENCRYPT_SUFFIX)

    for item in _HANDY_ITEMS:
        if item is None:
            menu.AppendSeparator()
            continue
        key, snippet, put2first = item
        menu_id = wx.NewId()
        menu.Append(menu_id, t(key))
        if snippet is None:
            window.Bind(wx.EVT_MENU, _encrypt_toggle, id=menu_id)
        else:
            window.Bind(wx.EVT_MENU,
                        lambda e, s=snippet, p=put2first: _insert(s, p),
                        id=menu_id)

    if extra_items:
        menu.AppendSeparator()
        for key, handler in extra_items:
            menu_id = wx.NewId()
            menu.Append(menu_id, t(key))
            window.Bind(wx.EVT_MENU, handler, id=menu_id)

    window.PopupMenu(menu)
    menu.Destroy()
