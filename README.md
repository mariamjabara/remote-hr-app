# remote-hr-app

### Install notes:

 1) Download and install Anaconda.
For Windows, the following link can be used (link found from https://www.anaconda.com/products/individual#windows , bottom of the page):
https://repo.anaconda.com/archive/Anaconda3-2020.07-Windows-x86_64.exe (Oct. 29, 2020)
2) On Windows, using the Windows search tool, find "Anaconda Prompt" and select Run as Administrator. 
   Or open a console on a Mac/Linux OS. 
3) In the Anaconda prompt, perform the following instructions:
conda update -n base conda -c defaults     
conda create -n HeartRateExtractionApp python=3.7 
conda activate HeartRateExtractionApp
conda install anaconda
conda install --channel conda-forge opencv

Note: from the above commands, only the command "conda activate HeartRateExtractionApp"  will be required in later executions.  

4) Download HandbrakeCLI.exe using one of the multi-platform links available at https://handbrake.fr/downloads2.php .
For Windows: https://github.com/HandBrake/HandBrake/releases/download/1.3.3/HandBrakeCLI-1.3.3-win-x86_64.zip (Oct. 29, 2020).
Extract the .exe file and copy it in the same directory as this python script (e.g. "HR_App_Final_V12.py").
 
### To start execution on Windows, :
- from the Anaconda prompt, navigate (change drive and directory) to the directory where this python script is located.
- type:  python HR_App_Final_V12.py 
- At run time, it is a good practice to position the python GUI window on the computer screen so that both the GUI window and the conda console can be displayed. This helps to follow the execution of the program (text displayed on console while processing, etc.)

### Known issues:
- On Windows, if the code is started from within the Spyder IDE platform (not required), the GUI controls do not execute properly. 
But the code runs fine from a Windows Anaconda prompt. On a Mac, the code runs fine from the Spyder IDE. 

### Additional notes:
- The code currently does not perform face or skin tracking. 
- To speed up execution, the conversion to constant fps could be computed for only the desired video frames, instead of for the whole video file
(ex. using --start-at --stop-at (in sec.) https://handbrake.fr/docs/en/latest/cli/command-line-reference.html).
#But since we only compute this once and then we save the resulting video with constant fps, this is less critical,
especially if the user wants to try different time ranges.
