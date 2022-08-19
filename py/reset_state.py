import badger2040
import badger_os
import os

display = badger2040.Badger2040()

for path in os.listdir("/state"):
    os.remove("/state/"+path)

badger_os.warning(display, "Device state folder reset :D")