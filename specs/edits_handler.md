# edits_handler.py

## Overview
This module handles the modification of TOPAS configuration files based on user inputs. It provides functions to replace specific strings in template files, allowing dynamic configuration of simulations.

## Functions

### stringindexreplacement

**Parameters:**
- SearchString: str
- TargetList: list of str (lines of the file)
- ReplacementString: str (optional)

**Process:**
Searches for the first line in TargetList that starts with SearchString and replaces it with the ReplacementString. If ReplacementString is None, the line is removed.

**Example:**
```python
lines = ["s:Ts/G4DataDirectory = \"/path\"\n", ...]
stringindexreplacement("s:Ts/G4DataDirectory", lines, "/new/path")
```

### editor

**Parameters:**
- change_dictionary: dict (keys are GUI elements, values are user inputs)
- TargetFile: str (path to the file to edit)
- filetype: str ('main' or 'sub')

**Process:**
1. Reads the TargetFile into a list of lines.
2. Applies multiple string replacements based on the change_dictionary and filetype.
3. Writes the modified lines back to the file.

**Example:**
```python
editor(change_dict, "config.batch", "main")
```

## Usage
Used by runtime_handler.py to modify boilerplate TOPAS configuration files with user-defined parameters. Also used in the CTDI command-line interface.

## Dependencies
- Uses fieldtobladeopening from fieldtobladeopening.py
- Used by runtime_handler.py and possibly other modules that need to edit configuration files.
