#!/usr/bin/env python

import pcbnew
import os, wx
import traceback
from .kifillet import filletBoard

UNITS = ["mm", "in"]

class FilletDialog(wx.Dialog):
    def __init__(self, parent=None, board=None, options=None):
        wx.Dialog.__init__(
            self, parent, title=f'Fillet board edges',
            style=(wx.DEFAULT_DIALOG_STYLE | wx.DIALOG_NO_PARENT))
        self.Bind(wx.EVT_CLOSE, self.OnClose, id=self.GetId())

        self.board = board

        self.options = options

        topBox = wx.BoxSizer(wx.VERTICAL)

        self._buildOptions(topBox)

        self._buildBottomButtons(topBox)

        self.SetSizer(topBox)

        topBox.Fit(self)
        self.Centre()

    def _buildOptions(self, parentSizer):
        cutTypeBox = wx.BoxSizer(wx.HORIZONTAL)
        
        cutTypeText = wx.StaticText(self, label="Type:")
        cutTypeBox.Add(cutTypeText, 0, wx.ALL | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 5)

        self.cutTypeSelect = wx.Choice(self, choices=["Fillet", "Chamfer"])
        self.cutTypeSelect.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.OnCutTypeChange, id=self.cutTypeSelect.GetId())
        cutTypeBox.Add(self.cutTypeSelect, 0, wx.ALL | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL | wx.EXPAND, 5)

        parentSizer.Add(cutTypeBox, 0, wx.ALL | wx.EXPAND, 10)

        unitsBox = wx.BoxSizer(wx.HORIZONTAL)

        unitsText = wx.StaticText(self, label="Units:")
        unitsBox.Add(unitsText, 0, wx.ALL | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 5)

        self.unitsSelect = wx.Choice(self, choices=UNITS, name="Units")
        self.unitsSelect.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.OnUnitsChange, id=self.unitsSelect.GetId())
        unitsBox.Add(self.unitsSelect, 0, wx.ALL | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL | wx.EXPAND, 5)
        parentSizer.Add(unitsBox, 0, wx.ALL | wx.EXPAND, 10)

        radiusBox = wx.BoxSizer(wx.HORIZONTAL)
        radiusText = wx.StaticText(self, label="Radius:")
        radiusBox.Add(radiusText, 0, wx.ALL | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 5)

        self.radiusSpinBox = wx.SpinCtrlDouble(self, value="Radius (mm)", min=0.01, max=1000.0)
        self.radiusSpinBox.SetValue(3.0)
        self.radiusSpinBox.SetDigits(2)
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.OnRadiusChange, id=self.radiusSpinBox.GetId())
        radiusBox.Add(self.radiusSpinBox, 1, wx.ALL | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL | wx.EXPAND, 5)

        parentSizer.Add(radiusBox, 0, wx.ALL | wx.EXPAND, 10)

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

    def OnUnitsChange(self, event):
        self.options["units"] = self.unitsSelect.GetString(self.unitsSelect.GetSelection())

    def OnRadiusChange(self, event):
        self.options["radius"] = self.radiusSpinBox.GetValue()

    def OnCutTypeChange(self, event):
        self.options["cut_type"] = self.cutTypeSelect.GetString(self.cutTypeSelect.GetSelection())

    def GetSelected(self):
        selected = [shape for shape in self.board.GetDrawings() if shape.IsSelected() and isinstance(shape, pcbnew.PCB_SHAPE)]

        return selected

    def OnFillet(self, event):
        try:
            progressDlg = wx.ProgressDialog(
                "Running Ki-Fillet", "Running Ki-Fillet, please wait",
                parent=self)
            progressDlg.Show()
            progressDlg.Pulse()

            radius_multiplier = 1000000
            if self.options["units"] == "in":
                radius_multiplier *= 25.4

            fillet_radius = int(self.options["radius"] * radius_multiplier)
            isFillet = self.options["cut_type"] == "Fillet"

            shapes = self.GetSelected()
            if len(shapes) == 0:
                shapes = None

            filletBoard(self.board, fillet_radius, onlySelected=(shapes != None), useFillet=isFillet)

            self.board.Save(self.board.GetFileName())
        except Exception as e:
            import os
            plugin_dir = os.path.dirname(os.path.realpath(__file__))
            log_file = os.path.join(plugin_dir, 'ki_fillet_error.log')
            with open(log_file, 'w') as f:
                f.write(repr(e))
            dlg = wx.MessageDialog(None, f"Cannot perform:\n\n{e}\n\n{traceback.format_exc()}", "Error", wx.OK)
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
        self.options = {"radius": 3.0, "units": "mm", "cut_type": "Fillet"}

    def defaults(self):
        self.name = "Ki-Fillet"
        self.category = "Ki-Fillet"
        self.description = "Add fillets to board edges"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'kifillet_icon.png')

    def Run(self):
        try:
            # TODO: Figure out how to select lines in pcbnew whilst dialog is open
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
