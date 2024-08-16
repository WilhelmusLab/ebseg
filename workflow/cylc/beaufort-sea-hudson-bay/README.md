## Cylc
To run the `cylc` workflow with the test data, run:
```bash
cylc stop beaufort-sea-hudson-bay/*       # stops any currently running workflows
cylc validate .                           # check the cylc configuration
cylc install . -n beaufort-sea-hudson-bay # installs the current version of the workflow
cylc play beaufort-sea-hudson-bay         # runs the workflow
cylc tui beaufort-sea-hudson-bay          # opens the text user interface
```

or on one line:
```bash
cylc stop beaufort-sea-hudson-bay/* ; cylc validate . & cylc install . && cylc play beaufort-sea-hudson-bay && cylc tui beaufort-sea-hudson-bay
```

In some cases, if the installation fails, you might need to run `cylc clean` before reinstalling: 
```bash
cylc stop ebseg/*; cylc validate . & cylc clean ebseg/*; cylc install . && cylc play ebseg && cylc tui ebseg
```