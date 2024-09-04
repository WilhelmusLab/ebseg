# Paper domain

Run the ebseg pipeline on the same domains as in 
Buckley, E. M., Cañuelas, L., Timmermans, M.-L., and Wilhelmus, M. M.:
Seasonal Evolution of the Sea Ice Floe Size Distribution
from Two Decades of MODIS Data, EGUsphere [preprint],
https://doi.org/10.5194/egusphere-2024-89, 2024.

To run the `cylc` workflow with the test data, run:
```bash
cylc stop ebseg-paper-domain*/*
cylc vip . -n ebseg-paper-domain-06 --initial-cycle-point=2006-05-04 --final-cycle-point=2006-05-06
cylc vip . -n ebseg-paper-domain-08 --initial-cycle-point=2008-07-13 --final-cycle-point=2008-07-15
cylc tui
```