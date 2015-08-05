from sys import argv
from scopefinder.app import ngApp

path = argv[1]
app = ngApp(path)
app.run()
