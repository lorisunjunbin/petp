import wx


# This code is a wxPython dialog for advanced text input, allowing multi-line and basic rich text input.
class AdvancedInputDialog(wx.Dialog):
	def __init__(self, parent, title, message, default_value=""):
		super().__init__(parent, title=title)
		self.value = default_value

		# Top-level sizer for the dialog
		dialog_sizer = wx.BoxSizer(wx.VERTICAL)

		# Panel for message and text input
		content_panel = wx.Panel(self)  # Parent is the dialog
		panel_sizer = wx.BoxSizer(wx.VERTICAL)

		# Message
		msg_label = wx.StaticText(content_panel, label=message)  # Parent is content_panel
		panel_sizer.Add(msg_label, 0, wx.ALL | wx.EXPAND, 10)

		# Text Input - Enhanced for multi-line and basic rich text
		self.text_ctrl = wx.TextCtrl(content_panel, value=default_value,
									 style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.HSCROLL)  # Parent is content_panel
		# Give it a default size and make it expandable
		self.text_ctrl.SetMinSize(wx.Size(350, 150))  # Width, Height
		panel_sizer.Add(self.text_ctrl, 1, wx.ALL | wx.EXPAND, 10)  # Proportion set to 1 to allow expansion
		self.text_ctrl.SetFocus()  # Set focus to the text input
		self.text_ctrl.SelectAll()  # Select all text by default

		content_panel.SetSizer(panel_sizer)  # Set sizer for the content_panel

		dialog_sizer.Add(content_panel, 1, wx.EXPAND | wx.ALL, 5)  # Add panel to dialog's sizer, panel proportion 1

		# Buttons - parented to the dialog (self) by CreateStdDialogButtonSizer
		button_sizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
		dialog_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)  # Add button_sizer to dialog's sizer

		self.SetSizer(dialog_sizer)  # Set the main sizer for the dialog
		dialog_sizer.Fit(self)  # Fit the dialog to the sizer's content
		self.SetMinSize(self.GetSize())
		self.CentreOnParent()

		# Bind OK button event to store value
		ok_button = self.FindWindowById(wx.ID_OK)
		if ok_button:
			ok_button.Bind(wx.EVT_BUTTON, self.on_ok)

	def on_ok(self, event):
		self.value = self.text_ctrl.GetValue()
		self.EndModal(wx.ID_OK)

	def GetValue(self):
		return self.value
