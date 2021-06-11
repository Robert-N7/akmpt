# ANoobs KMP Tool (AKmpt)
This tool automates the heavy-lifting of reversing a Mario Kart Wii KMP file.
The tool reverses the checkpoints, item routes, and cpu routes.
It also rotates the starting point and respawns 180 degrees.
*It is only meant as a starting place for reversal, and further manual adjustments will be required.*

# Install
The KMP tool can be installed as a python package.
```
pip install git+https://github.com/Robert-N7/akmpt.git
```

# Usage
KMP reversal is done via command line, or through python

```
python -m akmpt reverse <kmp_file> [<destination>] [-o]
```
