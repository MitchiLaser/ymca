# Yet another Multi Channel Analyzer (YMCA)

> "It's fun to play with the YMCA!"

YMCA is a proof of concept multi channel analyzer (MCA) for the RedPitaya (RP).
It is based on the MCPHA application, written by Pavel Demin, and uses the server application he provides to retrieve the data from the analog inputs.

## Contents

- `mcpha_osc`contains the code for the testing of the oscilloscope functionality of the MCPHA application.
    - `osc.py` is the library written to interact with the oscilloscope.
- `ymca` is the YMCA application. It requires the mimoCoRB library to be installed. This implementation is currently not working !!!!!!
- `NoRB` - No Ring Buffer: An implementation of the YMCA without the use of the mimoCoRB library. (used for the testing purpose of the YMCA before mimoCoRB was working)
- `scpi_test` contains the code for the testing of the SCPI server provided by the RedPitaya manufacturer.
