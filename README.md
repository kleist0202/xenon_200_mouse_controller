# xenon_200_mouse_controller
Driver app for Xenon 200 mouse. It uses ```pysub``` to send requests and ```PyQt``` for graphical interface.
## Installation
### Using virtual environment
Create virtual environment:
```
python -m venv env
```
Activate virtual environment:
```
source env/bin/activate
```
Install package:
```
pip install -e .
```
Now you can run it from this virtual environment:
```
./env/bin/xenon_driver
```

### System wide installation
You can install this package system wide using ***pipx***. Just run command below in root package directory:
```
pipx install .
```

It will most probably be installed in *~/.local/bin*, so make sure it is in your *$PATH*.
