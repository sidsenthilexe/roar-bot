<sub>Initial fork from [augcog/ROAR_Competition](https://github.com/augcog/ROAR_Competition)</sub>
# roar-bot
## A bot to autonomously control a vehicle in the [CARLA simulator](https://carla.org/)
This program was written in Python, and is being designed to race on UC Berkeley's [Monza Map](https://roar.berkeley.edu/monza-map/), published by [Berkeley ROAR Racing](https://roar.berkeley.edu/).  

The current iteration of the bot completes 3 laps of the Monza circuit in 335.85s ([demo video](https://youtu.be/RzKoTG5Sp48))

<img width="1011" height="569" alt="Screenshot 2026-07-21 at 15 08 18" src="https://github.com/user-attachments/assets/778019be-4173-4497-88ce-99331a557bac" />

Notable features include PID control for throttle and steering, curvature calculation, and formulas for lookahead distances.

## Setup
The CARLA simulator is meant to run on Windows, as are these installation instructions

### Installing Anaconda
* Go to the [Anaconda download page](https://www.anaconda.com/download/success?reg=skipped).
* Download `Anaconda Distribution` for Windows.
* Complete the installation process

### Downloading and Running the Simulator Server
* Go to Berkeley ROAR's [Monza Map webpage](https://roar.berkeley.edu/monza-map/).
* Select the `Monza V1.1 Map File` download.
* Extract the downloaded `.zip` file to `C:\ROAR`
* Navigate to `C:\ROAR\Monza` and run `CarlaUE4.exe`.

### Installing the Bot and its Dependencies
#### First, install all dependencies for the project
* Open the `Anaconda Prompt` application and run the following
```
conda create -n roar python=3.8 -y
conda activate roar
cd C:\ROAR
git clone https://github.com/augcog/ROAR_PY.git
cd ROAR_PY
pip install -r requirements.txt
cd roar_py_core
pip install -e
cd ..\roar_py_carla
pip install -e
```
* Test if packages are installed correctly. If they are, "`packages installed correctly`" should get printed:
```
python -c "import carla, roar_py_interface, roar_py_carla; print("packages installed correctly")"
```

#### Install the Bot and run it
```
cd C:\ROAR
git clone https://github.com/sidsenthilexe/roar-bot.git
cd roar_bot\competition_code
```
To run the simulation, first ensure that `CarlaUE4.exe` is still running, and then run
```
python competition_runner.py
```
