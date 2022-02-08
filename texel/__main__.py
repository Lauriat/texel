import os
from .texel import main

os.environ.setdefault("ESCDELAY", "100")
os.environ["TERM"] = "xterm-256color"

main()
