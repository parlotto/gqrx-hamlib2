# gqrx-hamlib2

gqrx-hamlib - a gqrx to Hamlib interface to keep frequency
between gqrx and a radio in sync when using gqrx as a panadaptor
using Hamlib to control the radio
#
The Hamlib daemon (rigctld) must be running, gqrx started with
the 'Remote Control via TCP' button clicked and comms to the radio
 working otherwise an error will occur when
starting this program. Ports used are the defaults for gqrx and Hamlib.

run :  python3 ./gqrx-hamlib-fldigi2.py [-f]

Test only on xubuntu 20.04 but should work on most distros.

## Authors

* **Philippe Arlotto** - 

## License

This project is licensed under the GPL licence
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

## Acknowledgments

* original code from Simon Kennedy, G0FCU, : https://github.com/g0fcu/gqrx-hamlib 




