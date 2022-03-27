import pcbnew
import os
import wx
from kifillet import filletBoard

class FilletDialog(wx.Dialog):
    def __init__(self, parent=None, board=None, options=None):
        wx.Dialog.__init__(
            self, parent, title=f'Fillet board edges',
            style=wx.DEFAULT_DIALOG_STYLE)
        self.Bind(wx.EVT_CLOSE, self.OnClose, id=self.GetId())

        self.board = board

        self.options = options

        topBox = wx.BoxSizer(wx.VERTICAL)

        self._buildOptions(topBox)

        self._buildBottomButtons(topBox)

        self.SetSizer(topBox)

        topBox.Fit(self)
        self.Centre()
        # self.OnResize()

    def _buildOptions(self, parentSizer):
        radiusBox = wx.BoxSizer(wx.HORIZONTAL)
        radiusText = wx.StaticText(self, label="Radius:")
        radiusBox.Add(radiusText, 0, wx.ALL |wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 5)

        self.radiusSpinBox = wx.SpinCtrlDouble(self, value="Radius (mm)", min=0.01, max=1000.0)
        self.radiusSpinBox.SetValue(3.0)
        self.radiusSpinBox.SetDigits(2)
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.OnRadiusChange, id=self.radiusSpinBox.GetId())
        radiusBox.Add(self.radiusSpinBox, 1, wx.ALL | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL | wx.EXPAND, 5)

        self.generateNewBoardCheckBox = wx.CheckBox(self, label = "Generate new file")
        self.Bind(wx.EVT_CHECKBOX, self.OnNewBoardCheckBoxChange, id=self.generateNewBoardCheckBox.GetId())

        newBoardBox = wx.BoxSizer(wx.HORIZONTAL)

        self.newBoardText = wx.StaticText(self, label="New filename:")
        self.newBoardText.Disable()
        newBoardBox.Add(self.newBoardText, 0, wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 5)

        self.newFileNameTextBox = wx.TextCtrl(self, value=self.board.GetFileName(), size=wx.Size(300, -1))
        self.newFileNameTextBox.Disable()
        self.Bind(wx.EVT_TEXT, self.OnNewFileNameChange, id=self.newFileNameTextBox.GetId())
        newBoardBox.Add(self.newFileNameTextBox, 1, wx.RIGHT | wx.EXPAND, 5)


        parentSizer.Add(radiusBox, 0, wx.ALL | wx.EXPAND, 10)

        parentSizer.Add(self.generateNewBoardCheckBox, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)

        parentSizer.Add(newBoardBox, 0, wx.ALL | wx.EXPAND, 10)

    def _buildBottomButtons(self, parentSizer):
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        closeButton = wx.Button(self, label='Close')
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=closeButton.GetId())
        button_box.Add(closeButton, 1, wx.RIGHT, 10)
        self.okButton = wx.Button(self, label='Fillet')
        self.Bind(wx.EVT_BUTTON, self.OnFillet, id=self.okButton.GetId())
        button_box.Add(self.okButton, 1)

        parentSizer.Add(button_box, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM | wx.ALL, 10)

    def OnClose(self, event):
        self.EndModal(0)

    def OnRadiusChange(self, event):
        self.options["radius"] = self.radiusSpinBox.GetValue()
    
    def OnNewBoardCheckBoxChange(self, event):
        self.options["newBoard"] = self.generateNewBoardCheckBox.GetValue()
        if self.generateNewBoardCheckBox.GetValue():
            self.newFileNameTextBox.Enable()
            self.newBoardText.Enable()

        else:
            self.newFileNameTextBox.Disable()
            self.newBoardText.Disable()

    def OnNewFileNameChange(self, event):
        self.options["newFileName"] = self.newFileNameTextBox.GetValue()

    def OnFillet(self, event):
        try:
            progressDlg = wx.ProgressDialog(
                "Running Ki-Fillet", "Running Ki-Fillet, please wait",
                parent=self)
            progressDlg.Show()
            progressDlg.Pulse()

            # Work-around
            # self.board = pcbnew.LoadBoard(pcbnew.GetBoard().GetFileName())

            if (self.options["newBoard"]):
                self.board = pcbnew.BOARD(self.board)
                # self.newBoard.SetFileName(self.options["newFileName"])

                # self.board = self.newBoard

            fillet_radius = int(self.options["radius"] * 1000000)
            filletBoard(self.board, fillet_radius)
            if (self.options["newBoard"]):

                self.board.Save(self.options["newFileName"])
            # else:
                # self.board.Save(self.board.GetFileName())

        except Exception as e:
            dlg = wx.MessageDialog(
                None, f"Cannot perform:\n\n{e}", "Error", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
        finally:
            progressDlg.Hide()
            progressDlg.Destroy()
        pcbnew.Refresh()
        self.OnClose(None)

class KiFilletPlugin(pcbnew.ActionPlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: Store and load options
        self.options = {"radius": 3.0, "newBoard": False}

    def defaults(self):
        self.name = "Ki-Fillet"
        self.category = "Ki-Fillet"
        self.description = "Add fillets to board edges"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon_24x24.png')

    def Run(self):
        try:
            dialog = FilletDialog(None, pcbnew.GetBoard(), self.options)
            dialog.ShowModal()
        except Exception as e:
            dlg = wx.MessageDialog(
                None, f"Cannot perform: {e}", "Error", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
        finally:
            if "dialog" in locals():
                dialog.Destroy()

plugin = KiFilletPlugin()

# KiFilletPlugin().register() # Instantiate and register to Pcbnew