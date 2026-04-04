import sys
import wx
import wx.grid


_IS_WINDOWS = sys.platform == 'win32'


class SearchableGridChoiceEditor(wx.grid.GridCellEditor):
	"""Grid editor with type-to-filter behavior for large choice lists."""

	def __init__(self, choices, allow_others=False, match_mode="contains"):
		super().__init__()
		self._all_choices = list(choices or [])
		self._allow_others = allow_others
		self._match_mode = match_mode
		self._control = None
		self._start_value = ""
		self._is_syncing = False
		self._is_selecting = False   # True while a dropdown click is being processed
		self._is_navigating = False  # True while Up/Down key navigation is in progress
		self._filter_timer = None
		self._pending_keyword = ""

	def Create(self, parent, id, evt_handler):
		self._control = wx.ComboBox(
			parent,
			id,
			value="",
			choices=self._all_choices,
			style=wx.CB_DROPDOWN,
		)
		self.SetControl(self._control)

		if evt_handler:
			self._control.PushEventHandler(evt_handler)

		self._control.Bind(wx.EVT_COMBOBOX, self._on_combobox_select)
		self._control.Bind(wx.EVT_TEXT, self._on_text)
		self._control.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
		self._control.Bind(wx.EVT_KILL_FOCUS, self._on_kill_focus)

		if _IS_WINDOWS:
			self._filter_timer = wx.Timer(self._control)
			self._control.Bind(wx.EVT_TIMER, self._on_filter_timer, self._filter_timer)

	def SetSize(self, rect):
		if self._control is not None:
			self._control.SetSize(rect.x, rect.y, rect.width, rect.height, wx.SIZE_ALLOW_MINUS_ONE)

	def BeginEdit(self, row, col, grid):
		self._start_value = grid.GetCellValue(row, col)
		self._sync_items(self._all_choices, self._start_value)
		self._control.SetFocus()
		self._control.SetInsertionPointEnd()

	def EndEdit(self, row, col, grid, old_val):
		if self._control is None:
			return None

		value = self._control.GetValue()
		if not self._allow_others and value not in self._all_choices:
			value = self._start_value

		if value != old_val:
			return value
		return None

	def ApplyEdit(self, row, col, grid):
		value = self._control.GetValue()
		if not self._allow_others and value not in self._all_choices:
			value = self._start_value
		grid.SetCellValue(row, col, value)

	def Reset(self):
		if self._control is not None:
			self._sync_items(self._all_choices, self._start_value)

	def Clone(self):
		return SearchableGridChoiceEditor(self._all_choices, self._allow_others, self._match_mode)

	def StartingClick(self):
		pass

	def Destroy(self):
		if _IS_WINDOWS and self._filter_timer is not None:
			self._filter_timer.Stop()
		if self._control is not None:
			try:
				self._control.PopEventHandler(True)
			except Exception:
				pass
		super().Destroy()

	def _on_key_down(self, evt):
		"""Handle keyboard navigation in the dropdown list."""
		keycode = evt.GetKeyCode()

		if keycode in (wx.WXK_UP, wx.WXK_DOWN):
			# Mark as navigating so _on_text won't re-filter and close the dropdown.
			if _IS_WINDOWS and self._filter_timer is not None:
				self._filter_timer.Stop()
			self._is_navigating = True
			evt.Skip()  # Let ComboBox handle native Up/Down movement.
			# Reset the flag after the ComboBox has finished processing the key.
			wx.CallAfter(self._reset_navigating)
			return

		if keycode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
			# Accept the currently highlighted value and restore the full list.
			if _IS_WINDOWS and self._filter_timer is not None:
				self._filter_timer.Stop()
			selected = self._control.GetValue()
			self._is_selecting = True
			self._sync_items(self._all_choices, selected)
			self._is_selecting = False
			# Dismiss the dropdown.
			self._control.Dismiss()
			evt.Skip()
			return

		if keycode == wx.WXK_ESCAPE:
			# Cancel: revert to the original value.
			if _IS_WINDOWS and self._filter_timer is not None:
				self._filter_timer.Stop()
			self._sync_items(self._all_choices, self._start_value)
			self._control.Dismiss()
			evt.Skip()
			return

		# Any other key: allow normal typing and filtering.
		evt.Skip()

	def _reset_navigating(self):
		"""Called via CallAfter to clear the navigation flag."""
		self._is_navigating = False

	def _on_combobox_select(self, evt):
		"""User clicked an item in the dropdown – accept the value and
		restore the full choice list without re-filtering."""
		if _IS_WINDOWS:
			if self._filter_timer is not None:
				self._filter_timer.Stop()
			# On Windows, restoring items immediately here can wipe out the
			# value just selected by the native control.
			self._is_selecting = True
			wx.CallAfter(self._deferred_select_restore)
		else:
			self._is_selecting = True
			selected = self._control.GetValue()
			# Restore full list so the next open shows everything,
			# but keep the selected value in the text field.
			self._sync_items(self._all_choices, selected)
			self._is_selecting = False
		evt.Skip()

	def _deferred_select_restore(self):
		selected = self._control.GetValue()
		if self._control.GetCount() != len(self._all_choices):
			self._sync_items(self._all_choices, selected)
		self._is_selecting = False

	def _on_text(self, evt):
		if self._is_syncing or self._is_selecting or self._is_navigating:
			evt.Skip()
			return

		if _IS_WINDOWS and self._filter_timer is not None:
			self._pending_keyword = self._control.GetValue()
			self._filter_timer.Stop()
			self._filter_timer.StartOnce(200)
			evt.Skip()
			return

		keyword = self._control.GetValue()
		filtered = self._filter_choices(keyword)
		self._sync_items(filtered, keyword)
		evt.Skip()

	def _on_filter_timer(self, _evt):
		if self._is_syncing or self._is_selecting or self._is_navigating:
			return
		keyword = self._pending_keyword
		filtered = self._filter_choices(keyword)
		self._sync_items(filtered, keyword)
		if filtered and keyword:
			wx.CallAfter(self._control.Popup)

	def _on_kill_focus(self, evt):
		# Keep existing behavior when allow_others=False: invalid input falls back to original value.
		if not self._allow_others and not self._is_selecting:
			current = self._control.GetValue()
			if current and current not in self._all_choices:
				if _IS_WINDOWS:
					self._control.ChangeValue(self._start_value)
				else:
					self._control.SetValue(self._start_value)
		evt.Skip()

	def _sync_items(self, items, value):
		self._is_syncing = True
		try:
			self._control.Freeze()
			self._control.Clear()
			self._control.AppendItems(items)
			if _IS_WINDOWS:
				self._control.ChangeValue(value)
			else:
				self._control.SetValue(value)
			self._control.SetInsertionPointEnd()
		finally:
			self._control.Thaw()
			if _IS_WINDOWS:
				wx.CallAfter(self._finish_sync)
			else:
				self._is_syncing = False

	def _finish_sync(self):
		self._is_syncing = False

	def _filter_choices(self, keyword):
		if not keyword:
			return self._all_choices

		needle = keyword.lower()
		if self._match_mode == "prefix":
			return [item for item in self._all_choices if str(item).lower().startswith(needle)]
		return [item for item in self._all_choices if needle in str(item).lower()]

