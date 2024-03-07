# Float Tuna

CLI tool for tuning ATR's *Amps to Accel Ratio* in [Float Pkg](https://github.com/surfdado/vesc_pkg/tree/main/float) from logged ride data.

## Data Acquisition

In VESC Tool, log a ride. Ideally on flat ground, but representable of your normal riding with a variety of accelerations and decelerations. At least stop the recording at the same location or elevation as you started.

## Installation

Get this repository, make sure you have Python installed, pip install prerequisites:

```
pip install -r requirements.txt
```

## Usage

Place your recorded .csv log file into the project directory.

In your terminal, navigate to the project folder and run:

```
python accel_ratio.py -hz 800
```

The `-hz`/`--loop_hertz` argument should match your controller's frequency (Float Pkg > Specs > Loop Hertz). Defaults to 800 Hz, which is what the ADV runs at. I believe other common values are 832/833 and 1000 Hz.

Use `-p`/`--plot` flag to plot recorded data along with the predicted curve.

TODO image

## Interpreting the Results
The predicted Accel Ratio shouldn't be too far from the default 9.0. For a reference, as a lighter rider I got around 8.0.

Torque Offset is hard coded to 8 A, so you can't change it, but again the predicted value should be close enough.

The R Value is indicating how much correlation there is between the measured and predicted acceleration. 1.0 would be perfect correlation, hopefully no less than 0.5.

As a sanity check, here are my values:
- ADV with v1 motor and bearing covers
- weight: 60kg / 130 lbs
- suggested Accel Ratio: 7.9
- suggested Torque Offset: 9.0 A

In the code, higher ratios would lower the expected acceleration, so as a rule of thumb, heavier riders should get higher recommended Accel Ratio.

## Acknowledgements

Thanks Dado Mista and Nico Aleman for your work on ATR and your VESC knowledge.