# ANoobs KMP Tool (AKmpt)
This tool automates the heavy-lifting of reversing a Mario Kart Wii KMP file.
The tool reverses the checkpoints, item routes, and cpu routes.
It also rotates the starting point around the start line and respawns around their area.
*It is only meant as a starting place for reversal, and further manual adjustments will be required.*

# Install
Download compiled [releases](https://github.com/Robert-N7/akmpt/releases) from the release page.

The KMP tool can also be installed as a python package.
```
pip install git+https://github.com/Robert-N7/akmpt.git
```

# Usage
KMP reversal is done via command line, or through python
# Reversal
KMP reversal is done via command line.

```
akmpt reverse <kmp_file> [<destination> route=<base_10_index> -o]
```
The following command reverses kmp in place:
```
akmpt reverse course.kmp -o
```
Since it is unclear if routes should be reversed, that is left to the user. This command would reverse the 10th route.

```
akmpt reverse course.kmp --route=10 -o
```

#Rotation
Rotation is also left to the user on objects, as some may not need rotation.
```
akmpt rotate <filename> [<destination> group=<group> item=<item> rotation=<rotation> direction=<direction> -o]
```

Item may be a string, or a base-10 index.

```
akmpt rotate course.kmp --item=sanbo
```
* `Group` may be one of the kmp groups that are rotate-able. The default used is game_objects.
* `Rotation` is in degrees and defaults to 180.
* The rotation `direction` may be x, y, or z. The default is y.
