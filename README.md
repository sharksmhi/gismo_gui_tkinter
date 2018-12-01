# GISMOtoolbox (gismo_gui_tkinter)
GISMOtoolbox is a Python 3.6 GUI application for working with in-situ data from ferrybox, fixed platforms and CTD profiles. 
Functionality includes automatic and visual flagging of data, camparison between sampling types and interactive plot exports. 
Graphics by tkinter. 

### Preparations and requirements 
Program uses basemap for showing maps. The module requires Microsoft Visual C++ for python whitch can be a bit tricky to install if you want to run the program in a viritual environment (recomended). Here follows a step by step guide on the prefered way to setup a all requirements needed to run the program on Windows (not tested for other platforms). The guide assumes the user has no prior experience of Python. 

- Download Python 3.6 based on your system here: https://www.python.org/downloads/release/python-367/. We recomend you install under C:\Pyhton36 and DONT add pyhton to PATH. 
- Create a directory where you want to install GISMOtoolbox 
- From this directory open a cmd console (you will get this option if you hold down SHIFT and right click) 
- Create a virtual environment by typing: C:\Python36\python.exe -m venv venv36 (this will create a virtual environment in the folder venv36
- Clone the GISMOtoolbox repository by typing (git can be downloaded here): git 
