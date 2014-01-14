#!/usr/bin/env python

from monomotapa import app
if __name__ == "__main__": 
    app.debug = True   # for dev purposes only, never production
    app.run()
