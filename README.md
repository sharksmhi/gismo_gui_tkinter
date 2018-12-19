# GISMOtoolbox (gismo_gui_tkinter)
GISMOtoolbox is a Python 3.6 GUI application for working with in-situ data from ferrybox and fixed platforms. 
Functionality includes automatic and visual flagging of data, camparison between sampling types and interactive plot exports. 
Graphics by tkinter. 

### Preparations and requirements 
Application uses basemap for showing maps. The module requires Microsoft Visual C++ for python which can be a bit tricky to install if you want to run the program in a viritual environment (recomended). Here follows a step by step guide on the prefered way to setup all requirements needed to run the program on Windows (not tested for other platforms). The guide assumes the user has no prior experience of Python. 

#### Download Pyhton and application
- Download Python 3.6 based on your system here: https://www.python.org/downloads/release/python-367/. We recomend you install under C:\Pyhton36 and DONT add pyhton to PATH. 
- Create a directory where you want to install GISMOtoolbox 
- From this directory open a cmd console (you will get this option if you hold down SHIFT and right click) 
- Create a virtual environment by typing (this will create a virtual environment in the folder venv36): 
      C:\Python36\python.exe -m venv venv36 
      
- Clone the GISMOtoolbox repository by typing (git can be downloaded here https://git-scm.com/downloads): 
      git clone https://github.com/sharksmhi/gismo_gui_tkinter.git 
      
- Clone the sharkpylib by typing: 
      git clone https://github.com/sharksmhi/sharkpylib.git 
      
You should now have three folders (venv36, gismo_gui_tkinter and sharkylib). 
- Copy the folder sharkpylib to gimso_gui_tkinger/libs 

#### Install required packages 
- Go to https://www.lfd.uci.edu/~gohlke/pythonlibs/ and download the following packages based on your operating system. Make sure you download packeges for python36 (should contain cp36): 
      pyproj 
      basemap 
      
- From the command line type (from the directory where you have your three folders): 
      venv36\Scripts\activate 
      
      This will activate the newly created virituell environment. 

- Now install the two packages by typing: 
      pip install <path to downloded pyproj-file>
      pip insatll <path to downloded basemap-file> 
      
- We also need to install some other required packages by typing: 
      pip install -r gismo_gui_tkinter/requirements.txt 
      
### Run GISMOtoolbox 
Run the application via he command line: 
- Activate environment: venv36\Scripts\activate 
- Run: python gismo_gui_tkinter\main.py

      
