# OPSCC.net
![Github Overview 1](https://github.com/OPSCCnet/OPSCC.net/blob/main/Github_overview_1.png)
Welcome to the reposiroty of OPSCC.net!
OPSCC.net is an open source tool that allows users to determine HPV-association in dedicated head and neck tumors. In its current version, OPSCC.net is built around the most used and most succesfull open-source tool for digital pathology (QuPath, at the time of commit at version 0.3.2), which has been built by Pete Bankhead from the The University of Edinburgh. You should visit this page if you have specific questions regarding QuPath. Actually, you should visit this page anyway because QuPath is a fantastic tool.
A big shoutout to Pete and his crew for making this available to the community.
Despite QuPath, OPSCC.net uses segmentation models for PyTorch, which has been built by Pavel Iakubovskii.
Parts of the code has been used and modified that I found 

### 📋 Table of content
 1. [Installation requirements](#installation-req)
 2. [Installation](#installation)
 3. [Examples](#examples)
 4. [Shoutout](#shoutout)
 5. [License](#license)

### 🚧 Installation requirements <a name="installation-req"></a>
Please consider that OPSCCnet has been tested using unix based systems (MacOS and Ubuntu). A GPU is advantegous but not necessary. OPSCC.net can be run using regular clients.\
[How to install anaconda](https://docs.anaconda.com/anaconda/install/)\
[How to install QuPath 0.3.1](https://github.com/qupath/qupath/releases/tag/v0.3.1)\
Once you have downloaded / cloned the OPSCC.net repository please navigate to the folder where it is located generate a conda environment, activate the environment and install the pip requirements.

### 🧨 Installation <a name="installation"></a>
```bash
conda create --name OPSCCnet python=3.9
conda activate OPSCCnet
pip install -r requirements.txt
```

### 🎯 Examples <a name="examples"></a>
Please open the runOPSCCnet.sh shell file using a given editor of choice and insert the QuPath directory where the actual APP is located at the second line, replacing "INSERT QUPATH DIRECTORY TO APP HERE" and save the file. For instance, change it to: QuPathApp="/home/sebastian/DeepLearning_Image/QuPath/bin/QuPath".

If you have already navigated yourself to the OPSCCnet directory, you are ready to go!
./runOPSCCnet has three arguments: -i should be the 'directory where the whole slide images are located'; -o 'directory of the OPSCC.net repor': -p 'directory where everything will be saved as QuPath project'
```bash
./runOPSCCnet -i '/home/sebastian/directory-with-whole-slide-images' -o '/home/sebastian/OPSCC.net' -p 'home/sebastian/directory-where-QuPath-project-should-be-saved'
```
TEXT
![Github Overview 2](https://github.com/OPSCCnet/OPSCC.net/blob/main/Github_overview_2.png)
TEXT
![Github Overview 2](https://github.com/OPSCCnet/OPSCC.net/blob/main/Github_overview_3.png)
### Shoutout <a name="shoutout"></a>