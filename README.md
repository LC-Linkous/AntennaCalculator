# AntennaCalculator GUI

A forked GUI branch of [Dollarhyde's](https://github.com/Dollarhyde) [CLI-based AntennaCalculator](https://github.com/Dollarhyde/AntennaCalculator). This branch is a simplified version of how the AntennaCalculator is integrated into [LC-Linkous'](https://github.com/LC-Linkous) [AntennaCAT project](https://github.com/LC-Linkous/AntennaCalculationAutotuningTool). It features some matplotlib-based graphics to help visualize the antenna topologies based on user inputs. 

The calculator features the following topologies:
* Rectangular patch antenna, probe and microstrip versions
* Quarter Wave Monopole
* Half Wave Dipole



## Table of Contents
* [Requirements](#requirements)
* [Implementation](#implementation)
    * [GUI](#gui)
    * [Matplotlib](#matplotlib)
    * [Argparse](#argparse)
    * [Antenna Calculations](#antenna-calculations)
    * [AntennaCAT](#antennacat)
* [Examples](#example-implementations)
    * [Rectanglar Patch](#rectangular-patch)
      * [PNG output using `--pngoutput`](#png-output-using---pngoutput)
      * [DXF output using `--dxfoutput`](#dxf-output-using---dxfoutput)
      * [Gerber output using `--gerberoutput`](#gerber-output-using---gerberoutput)
    * [Quarter Wave Monopole](#quarter-wave-monopole)
    * [Half Wave Dipole](#half-wave-dipole)
* [References](#references)
* [Publications and Presentations](#publications-and-presentations)
    * [Papers](#papers)
    * [DEFCON 30 Presentation](#defcon-30-presentation)
      * [Presentation Recording](#presentation-recording)
      * [PDF Presentation](#pdf-presentation)



## Requirements

This project requires (list major need-to-be-installed libs). 

Use 'pip install -r requirements.txt' to install the following dependencies:

```python
ADD LIBRARIES HERE

```

## Implementation


```python
python3 antenna_calculator_gui.py 

```





### GUI

*TODO: add image

### Matplotlib

* TODO: brief explanation of matplotlib use here



### Argparse
---

The original [AntennaCalculator](https://github.com/Dollarhyde/AntennaCalculator) branch uses [argparse](https://docs.python.org/3/library/argparse.html) to take a series of arguments and output calculated values based on the equations in [1]. This functionality still exists in this branch, retained in the original antenna_calculator.py. 

In the original antenna_calculator.py, the program was run directly from the terminal such that:

Sample Input:
```
python3 antenna_calculator.py rectangular_patch -f 2.4e9 -er 4.4 -h 1.6e-3

```
Sample Output:
```
python3 antenna_calculator.py rectangular_patch -f 2.4e9 -er 4.4 -h 1.6e-3
[*] W = 38.04 millimeter
[*] L = 29.44 millimeter
[*] Ws = 3.06 millimeter
[*] y0 = 19.02 millimeter
[*] x0 = 11.32 millimeter
```

In this branch, antenna_calculator_gui.py has a wrapper to take the user input in through the GUI, format it for the argparse argument, and then process the return. This was done to 1) retain as much as the original calculator as possible for future expansion, 2) demonstrate the modular AntennaCAT integration, minus a few error checking features for CEM/CAD integration.



### Antenna Calculations
---


The rectangular patch, monopole, and dipole designs are from 'Antenna Theory: Analysis and Design' [1]. The equations featured in this book are standard for these analytical topologies. 

It is important to note that no equation or calculation will 100% represent reality.  In application, when building these antennas, the math will get you 95% of the way. The last 5% is experimentation, and a bit of tuning. For the patch antennas this usually means adjusting the width or length (smaller = higher frequency, larger = lower frequency), or shortening $x_0$ slightly to increase the gain. For monopoles and dipoles, it is very common to shorten the conductor to match the imaginary part of the impedance of the antenna to a cable or port.

This calculator has been used with the AntennaCAT project to generate 150,000+ designs (and counting) in automated validation testing, and machine learning data collection.

### AntennaCAT
---

The Antenna Calculation and Autotuning Tool ([AntennaCAT](https://github.com/LC-Linkous/AntennaCalculationAutotuningTool)) is an in-progress tool to integrate calculation, design, simulations, and automation into an easy-to-use tool for research purposes. The GUI-integrated calculator is stand-alone; however the rest of the tool relies on licensed electromagnetic (EM) simulation tools such as ANSYS HFSS, COMSOL, or FEKO in order to simulate and manipulate antenna designs. 

## Examples

### Rectangular Patch

*TODO: add GUI image


#### PNG output using `--pngoutput`

![image](https://user-images.githubusercontent.com/18094862/184426961-36c21cbd-9cff-4c4b-a275-a81e187ce86c.png)

#### DXF output using `--dxfoutput`

![image](https://user-images.githubusercontent.com/18094862/184427196-34eb8369-11e8-48cb-9426-3251ef8c7e84.png)

#### Gerber output using `--gerberoutput`
![image](https://user-images.githubusercontent.com/18094862/187831470-c8cb4801-b0c9-44e2-acc7-454ad2d03f37.png)



### Quarter Wave Monopole
*TODO: add GUI image




### Half Wave Dipole
*TODO: add GUI image





## References

[1]: C. A. Balanis, Antenna Theory: Analysis and Design. Hoboken, New Jersey Wiley, 2016.



## Publications and Presentations
### Papers

* E. Karincic, E. Topsakal, and L. Linkous.  "Patch Antenna Calculations and Fabrication Made Simple for Cyber Security Research,"  2023 ASEE Annual Conference & Exposition, Baltimore , Maryland, 2023, June.  ASEE Conferences, 2023. [Online:] https://peer.asee.org/43974 

* L. Linkous, E. Karincic, J. Lundquist and E. Topsakal, "Automated Antenna Calculation, Design and Tuning Tool for HFSS," 2023 United States National Committee of URSI National Radio Science Meeting (USNC-URSI NRSM), Boulder, CO, USA, 2023, pp. 229-230, doi: 10.23919/USNC-URSINRSM57470.2023.10043119.

* L. Linkous, J. Lundquist and E. Topsakal, "AntennaCAT: Automated Antenna Design and Tuning Tool," 2023 IEEE USNC-URSI Radio Science Meeting (Joint with AP-S Symposium), Portland, OR, USA, 2023, pp. 89-90, doi: 10.23919/USNC-URSI54200.2023.10289238.



### DEFCON 30 Presentation
#### Presentation Recording
[![DEFCON Presentation](https://i.ytimg.com/vi/7mciNPmT1KE/hqdefault.jpg)](https://www.youtube.com/watch?v=7mciNPmT1KE "DEF CON 30 RF Village - Erwin Karincic - Have a SDR? - Design and make your own antennas")

#### PDF Presentation
["DEF CON 30 RF Village - Erwin Karincic - Have a SDR? - Design and make your own antennas" PDF link](https://github.com/Dollarhyde/AntennaCalculator/blob/main/Have%20a%20Software%20Defined%20Radio%20-%20Design%20and%20make%20your%20own%20antennas.pdf)


