# Float Tuna

CLI tool for tuning ATR's *Amps to Accel Ratio* in [Float Pkg](https://github.com/surfdado/vesc_pkg/tree/main/float) from logged ride data.

## Data Acquisition

In VESC Tool, log a ride. Ideally on flat ground, but representable of your normal riding with a variety of accelerations and decelerations. If not, at least stop the recording at the same location/elevation as you started, so the ups and downs average out. Few seconds is NOT enough.

## Installation

- Install [Python](https://www.python.org/downloads/), make sure it's in your path.
- Get this repository.
- In your terminal, navigate to the project directory.
- pip install prerequisites (*scipy*, *matplotlib*):
 

```
pip install -r requirements.txt
```

## Usage

Place your recorded .csv log file into the project directory.

In your terminal, navigate to the project folder and run:

```
python accel_ratio.py -hz 800
```

<!-- | Argument | Description |
| -------- | ----------- |
| dfa | Description | -->

The `-hz`/`--loop_hertz` argument should match your controller's frequency (Float Pkg > Specs > Loop Hertz). Defaults to 800 Hz, which is what the ADV runs at. Another common value is 832/833 Hz.

Use `-p`/`--plot` flag to plot recorded data along with the predicted curve.

With `-r`/`--ref_ratio` you can specify your current Accel. Ratio for comparison.

TODO image

## Interpreting the Results
Default Accel. Ratio is 9.0, Torque Offset is hard coded to 8 A. The predicted values should be close enough to that. As a rule of thumb, heavier riders should get higher recommended Accel. Ratio, since in the code, higher ratios would lower the expected acceleration.

For reference, here are my values:
- ADV with v1 motor + bearing covers (which add friction)
- weight: 60kg / 130 lbs
- suggested Accel Ratio: 7.9
- suggested Torque Offset: 9.0 A

Higher correlation means there is stronger relation between the predicted and measured acceleration. 0.0 means completely random, 1.0 would be perfect correlation. You should get no less than 0.5. Recording the log in a more controlled manner should yield in better correlation.

## Acknowledgements

Thanks Dado Mista and Nico Aleman for your work on ATR and your VESC knowledge.