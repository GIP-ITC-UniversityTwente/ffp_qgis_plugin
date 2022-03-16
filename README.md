# FFP Editing Tools

©2021 Javier Morales - <a href="mailto:j.morales@utwente.nl">j.morales@utwente.nl</a>

Editing functions of the FFP methodology
QGIS Plugin

### Changelog:

	0.7.0   [16-03-2022]
		* Renamed all the pg functions to use the new 'ffp_' prefix
		* Added functions to simplify and delete spatialunits
		* Added a simpler function to project points
		* fixed a bug with the mergeline function
	0.6.2	[25-05-2021]
		* Solved the error caused when the attribute table window is closed
	0.6.1	[02-04-2021]
		* Moved error reporting from the console to the main interface
		* Fixed database parameteres search issue in the layer source object
	0.6.0	[01-04-2021]
		* Added the "Merge Boundaries" action
		* Modified the format of the message windows
		* Added support to prevent some types of undesired use of actions
		* Fixed error preventing editing after saving changes within a session.
	0.5.0	[10-03-2021]
		* First release


### Requirements:

* QGIS Version 3.0
* PostgreSQL
* FFP data model v9.2


### Setup:


1. Start QGIS
1. From the menu select: '_Settings_' -> '_User Profiles_' -> '_Open Active Profile Folder_'
1. Navigate to '_./python/plugins_'
1. Create the '_ffp_tools_' folder
1. Paste the plugin files inside the '_ffp_tools_' folder
1. Close the File Explorer
1. Restart QGIS
1. Follow the instructions in the <a href="https://docs.google.com/document/d/1JRn8NUwioPwa_Xr4G7B67nflTcfu2Z1MwoCtT20ydoE">FFP Post-Processing Manual</a>
