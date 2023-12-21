# OPSCCnet
![Github Overview 1](https://github.com/OPSCCnet/OPSCCnet/blob/main/Github_overview_1.png)
Welcome to the reposiroty of OPSCCnet!
OPSCCnet is an open source tool that allows users to determine HPV-association in dedicated head and neck tumors. In its current version, OPSCCnet is built around the most used and most succesfull open-source tool for digital pathology (QuPath, at the time of latest commit at version 0.4.3), which has been built by Pete Bankhead from the The University of Edinburgh [Shoutout](#shoutout). 

### 📋 Table of content
 1. [Requirements](#installation-req)
 2. [Installation](#installation_1)
 3. [Configuration of paquo](#installation_2)
 4. [How to run OPSCCnet browser](#hwtrun_1)
 5. [How to run OPSCCnet browser using command line (it seems this the way to go for MAC Systems)](#hwtrun_2)
 6. [Examples](#examples)
 7. [Shoutout](#shoutout)
 8. [Citing](#citation)
 9. [License](#license)
 10. [Acknowledgements](#acknowledgements)

### 🚧 Requirements <a name="installation-req"></a>
Please consider that OPSCCnet has been tested using unix based systems (MacOS and Ubuntu). A GPU is advantegous but not necessary. OPSCCnet can be run using regular clients.\
Requirements: 
- [ ] Unix based system
- [ ] QuPath [anything above 0.3.1 should work, tested 0.4.3 at the time of latest commit] installed on your system
- [How to install QuPath 0.4.3](https://github.com/qupath/qupath/releases/tag/v0.4.3)
- [ ] Anaconda (recommended) / Miniconda installed on your system 
- [How to install anaconda](https://docs.anaconda.com/anaconda/install/)
- [ ] git installed / or manually downloaded the OPSCCnet repository 
- [How to install git](https://github.com/git-guides/install-git)

Clone repository
```bash
git clone https://github.com/OPSCCnet/OPSCCnet.git
```

### 🧨 Installation <a name="installation_1"></a>
```bash
conda create --name OPSCCnet python=3.9
conda activate OPSCCnet
pip install -r requirements.txt
```

OPSCCnet is using [paquo](https://github.com/bayer-science-for-a-better-life/paquo) to generate project files. It is necessary for paquo to know where QuPath is installed. Please [read the docs](https://paquo.readthedocs.io/en/latest/) where to put the QuPath directory path in order to let paquo access it.

- [x] You have cloned / downloaded the OPSCCnet.git repository and installed the pip requirements
- [x] You have installed QuPath 0.4.3 (see above) on your system
- [x] You now have a directory where OPSCCnet is installeg, e.g. /media/somewhere/OPSCCnet

It appears there is some misunderstanding of how to configure paquo, I have put a description below on how to set the path.
### 🧨 Configuration of paquo <a name="installation_2"></a>
```bash
cd /media/somewhere/OPSCCnet
python -m paquo config --list --default
python -m paquo config -l -o .
nano nano .paquo.toml
```
👇
### 💁 Details on how to use nano and set up the path
- Using nano: STRG + O writes the output and STRG + X exits the file.
- Once you have opened the paquo configure file, set the QuPath dir, e.g. qupath_dir "/home/sebastian/DeepLearning_Image/QuPath043/QuPath-0.4.3-Linux/QuPath/" [Please pay attention! The QuPath dir to be set for OPSCCnet either in the browser version or the command line version would be QuPathApp="/home/sebastian/DeepLearning_Image/QuPath043/QuPath-0.4.3-Linux/QuPath/bin/QuPath"; so they differ!]
- [x] You have put a reference of your QuPath APP to paquo (please see above; read their docs) 

> You are ready to go
### 🎯 How to run OPSCCnet using a browser <a name="hwtrun_1"></a>

```bash
streamlit run OPSCCnet.py
```

### 🎯 How to run OPSCCnet using the command line <a name="hwtrun_2"></a>
### 💁 Prepare the bash script of run_OPSCCnet.sh
- set the QuPath App directory, e.g. "QuPathApp="/home/sebastian/DeepLearning_Image/QuPath043/QuPath-0.4.3-Linux/QuPath/bin/QuPath" in the run_OPSCCnet.sh
```bash
./run_OPSCCnet.sh -i '/media/sebastian/8e545a02-8515-436b-9abe-f0b9ba1489d1/WSI/test_folder/WSI' -o '/media/sebastian/b4215009-f647-4cf3-97fe-038c17c9f61e/OPSCCnet' -p '/media/sebastian/8e545a02-8515-436b-9abe-f0b9ba1489d1/WSI/test_folder/test'
```

### 🎯 Examples <a name="examples"></a>
![Github Overview 2](https://github.com/OPSCCnet/OPSCCnet/blob/main/Github_overview_2.png)
### OPSCCnet has essentially three parts:
- Segmentation of viable tumor areas using a FPN with a ResNet-18 encoder
- Classification of image tiles for HPV-association using a ResNet-18
- Visualizing HPV-association on whole slide level (WSI) and giving tabular data as output for individual WSI's

### Cite our work <a name="citation"></a>
Klein, S., Wuerdemann, N., Demers, I. et al. Predicting HPV association using deep learning and regular H&E stains allows granular stratification of oropharyngeal cancer patients. npj Digit. Med. 6, 152 (2023). 
> Please get me to the [article](https://www.nature.com/articles/s41746-023-00901-z)

### Shoutout <a name="shoutout"></a>
You should visit this [page](https://forum.image.sc/tag/qupath) which is a great ressource for questions regarding QuPath. Snippets and parts from scripts have been copied from there. 
- A big shoutout to Pete Bankhead and his crew for making this available to the community
- Recently, Pete Bankhead has published a [book](https://bioimagebook.github.io/README.html), I have not had the chance to take a look, but I would recommend it either way
- A big shoutout to segmentation models for PyTorch, which has been built by Pavel Iakubovskii


### Licence <a name="licence"></a>
OPSCCnet is made for academic bodies, and its research use only. This is not a medical product.

### Acknowledgements<a name="acknowledgements"></a>
Figures were created with https://biorender.com/ and Adobe illustrator version 26.4. 