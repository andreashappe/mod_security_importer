# mod\_security Log Importer [![Build Status](https://api.travis-ci.org/andreashappe/mod_security_importer.svg?branch=master)](https://travis-ci.org/andreashappe/mod_security_importer.svg?branch=master)


This tool is intended to import mod\_security's incident logs into one or more
database. Multiple simple analysis tool will try to extract data to support
ongoing support work on the deployed mod\_security rule set.

I haven't written Python code in a couple of months, so please cope with
included rubyisms.

# setup

1. repository auschecken
2. virtualenv env
3. source env/bin/activate
4. python setup.py install

(requirements are mostly down to sqlalchemy and noste)

# run tests

~~~ bash
(env)[~/workspace/testproject]$ nosetests                                           
Ran 15 tests in 0.201s
OK
~~~

# import data

~~~ bash
(env)[~/workspace/testproject]$ bin/import
usage: import [-h] [--import-parts] database File [File ...]
import: error: too few arguments
 
(env)[~/workspace/testproject]$ bin/import --import-parts testme.sqlite /home/andy/Downloads/Mod_Security_Logs/*
also adding parts!
parsing /home/andy/Downloads/Mod_Security_Logs/20150330-230822-VRm7Rgr5AlMAACss5wwAAABE.txt
adding /home/andy/Downloads/Mod_Security_Logs/20150330-230822-VRm7Rgr5AlMAACss5wwAAABE.txt to db
parsing /home/andy/Downloads/Mod_Security_Logs/20150330-231038-VRm7zgr5AlMAAClwIZoAAAAU.txt
adding /home/andy/Downloads/Mod_Security_Logs/20150330-231038-VRm7zgr5AlMAAClwIZoAAAAU.txt to db
parsing /home/andy/Downloads/Mod_Security_Logs/20150509-175403-VU4tmwr5AlMAABZIdvcAAAEW.txt
adding /home/andy/Downloads/Mod_Security_Logs/20150509-175403-VU4tmwr5AlMAABZIdvcAAAEW.txt to db
parsing /home/andy/Downloads/Mod_Security_Logs/20150509-175413-VU4tpQr5AlMAABOvDLQAAAJM.txt
adding /home/andy/Downloads/Mod_Security_Logs/20150509-175413-VU4tpQr5AlMAABOvDLQAAAJM.txt to db
~~~

# Create a simple data listing

* bin/analyze_destinations
* bin/analyze_simple
