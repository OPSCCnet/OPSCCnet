# OPSCCnet
![Github Overview 1](https://github.com/OPSCCnet/OPSCCnet/blob/main/Github_overview_1.png)
Welcome to the reposiroty of OPSCCnet!
OPSCCnet is an open source tool that allows users to determine HPV-association in dedicated head and neck tumors. In its current version, OPSCCnet is built around the most used and most succesfull open-source tool for digital pathology (QuPath, at the time of commit at version 0.3.1), which has been built by Pete Bankhead from the The University of Edinburgh [Shoutout](#shoutout). 

### 📋 Table of content
 1. [Requirements](#installation-req)
 2. [Installation](#installation)
 3. [How to run OPSCCnet](#hwtrun)
 4. [Examples](#examples)
 5. [Shoutout](#shoutout)
 6. [Citing](#citation)
 7. [License](#license)
 8. [Acknowledgements](#acknowledgements)

### 🚧 Requirements <a name="installation-req"></a>
Please consider that OPSCCnet has been tested using unix based systems (MacOS and Ubuntu). A GPU is advantegous but not necessary. OPSCCnet can be run using regular clients.\
Requirements: 
- [ ] Unix based system
- [ ] QuPath 0.3.1 installed on your system
- [How to install QuPath 0.3.1](https://github.com/qupath/qupath/releases/tag/v0.3.1)
- [ ] Anaconda (recommended) / Miniconda installed on your system 
- [How to install anaconda](https://docs.anaconda.com/anaconda/install/)
- [ ] git installed / or manually downloaded the OPSCCnet repository 
- [How to install git](https://github.com/git-guides/install-git)

Clone repository
```bash
git clone https://github.com/OPSCCnet/OPSCCnet.git
```


### 🧨 Installation <a name="installation"></a>
```bash
conda create --name OPSCCnet python=3.9
conda activate OPSCCnet
pip install -r requirements.txt
```

Please open the runOPSCCnet.sh shell file using a given editor of choice and insert the QuPath directory where the actual APP is located at the second line, replacing "INSERT QUPATH DIRECTORY TO APP HERE" and save the file. For instance, change it to: QuPathApp="/home/sebastian/DeepLearning_Image/QuPath/bin/QuPath".

OPSCCnet is using [paquo](https://github.com/bayer-science-for-a-better-life/paquo) to generate project files. It is necessary for paquo to know where QuPath is installed. Please [read the docs](https://paquo.readthedocs.io/en/latest/) where to put the QuPath directory path in order to let paquo access it.

- [x] You have cloned / downloaded the OPSCCnet.git repository and installed the pip requirements
- [x] You have installed QuPath 0.3.1 on your system
- [x] You have changed the second line of the runOPSCCnet.sh shell script to your QuPath APP directory
- [x] You have put a reference of your QuPath APP to paquo (please read their docs) 

> You are ready to go
### 🎯 How to run OPSCCnet <a name="hwtrun"></a>
./runOPSCCnet has three arguments: -i should be the 'directory where the whole slide images are located'; -o 'directory of the downloaded OPSCCnet reposiroty': -p 'directory where everything will be saved as QuPath project'\

```bash
./runOPSCCnet.sh -i '/home/sebastian/directory-with-whole-slide-images' -o '/home/sebastian/OPSCCnet' -p 'home/sebastian/directory-where-QuPath-project-should-be-saved'
```
### 🎯 Examples <a name="examples"></a>
![Github Overview 2](https://github.com/OPSCCnet/OPSCCnet/blob/main/Github_overview_2.png)
### OPSCCnet has essentially three parts:
- Segmentation of viable tumor areas using a FPN with a ResNet-18 encoder
- Classification of image tiles for HPV-association using a ResNet-18
- Visualizing HPV-association on whole slide level (WSI) and giving tabular data as output for individual WSI's
![Github Gif OPSCCnet](https://github.com/OPSCCnet/OPSCCnet/blob/main/Github_gif_OPSCCnet.gif)
### Shoutout <a name="shoutout"></a>
You should visit this [page](https://forum.image.sc/tag/qupath) which is a great ressource for questions regarding QuPath. Snippets and parts from scripts have been copied from there. 
- A big shoutout to Pete Bankhead and his crew for making this available to the community
- Recently, Pete Bankhead has published a [book](https://bioimagebook.github.io/README.html), I have not had the chance to take a look, but I would recommend it either way
- A big shoutout to segmentation models for PyTorch, which has been built by Pavel Iakubovskii

### Cite our work <a name="citation"></a>
- please cite our work: currently our work is under review

### Licence <a name="licence"></a>
OPSCCnet is made for academic bodies, and its research use only. This is not a medical product.

### Acknowledgements<a name="acknowledgements"></a>
Figures were created with https://biorender.com/ and Adobe illustrator version 26.4. 