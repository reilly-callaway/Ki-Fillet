# KiCAD 7.0 now impliments this. Create your shapes on edge cuts -> Right click -> Fillet lines
This plugin does still offer some additional functionality, such as the CLI, chamfers and unit conversion. The plugin is no longer worthwhile maintaining.

# ~Ki-Fillet~
![Ki-Fillet Logo](https://github.com/reilly-callaway/ki-fillet/raw/master/resources/icon.png)

KiCAD PcbNew Plugin and CLI to automatically apply a rounded fillet of a given radius to all board edges of a PCB.

![Ki-Fillet example](https://github.com/reilly-callaway/ki-fillet/raw/master/resources/example.png)

## Installation
The plugin can be installed by downloading the latest [release](https://github.com/reilly-callaway/Ki-Fillet/releases/) and installing with the KiCAD Package Content Manager (PCM) with `Install from file` option.

## CLI
Ki-Fillet also offers a Command-Line Interface (CLI) to perform filleting actions. You should clone this repository and use the standlone script `kifillet.py` to access the CLI (PyPi package coming soon!).

You can view the help of the interface by calling `python PATH/TO/kifillet/kifillet.py --help`.
