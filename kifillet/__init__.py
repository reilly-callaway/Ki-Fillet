try:
    # Note the relative import!
    from .kifillet_plugin import KiFilletPlugin
    KiFilletPlugin().register()
# if failed, log the error and let the user know
except Exception as e:
    # log the error
    import os
    plugin_dir = os.path.dirname(os.path.realpath(__file__))
    log_file = os.path.join(plugin_dir, 'ki_fillet_error.log')
    with open(log_file, 'w') as f:
        f.write(repr(e))
    # register dummy plugin, to let the user know of the problems
    import pcbnew
    import wx

    class KiFilletPlugin(pcbnew.ActionPlugin):
        """
        Notify user of error when initializing the plugin
        """
        def defaults(self):
            self.name = "Ki-Fillet"
            self.category = "Ki-Fillet"
            self.description = "Add fillets to board edges"

        def Run(self):
            caption = self.name
            message = "There was an error while loading plugin \n" \
                      "Please take a look in the plugin folder for ki_fillet_error.log\n" \
                      "You can raise an issue on GitHub page.\n" \
                      "Please attach the .log file"
            wx.MessageBox(message, caption, wx.OK | wx.ICON_ERROR)

    KiFilletPlugin().register()

