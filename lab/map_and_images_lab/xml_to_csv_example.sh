#!/bin/bash

# xmlstrlet is an XML manager and handler for the *nix command line
# See: http://xmlstar.sourceforge.net/docs.php

xmlstarlet sel -T -q -t -m "//p:RefDataSet/RefDataValue" -v Name -o "|" -v Code -o "|" -v Description -o "|" -v SortOrder -o "|" -v ReviewDate -o "|" -v EffectiveDate -o "|" -v Properties/Property[1] -o "|" -v Properties/Property[2] -o "|" -v Properties/Property[3] -o "|" -v Properties/Property[4] -n Chapter_3_Entity_Type_IRS.xml > Chapter_3_Entity_Type_IRS.csv

xmlstarlet sel -T -q -t -m "//p:RefDataSet/RefDataValue" -v Name -o "|" -v Code -o "|" -v Description -o "|" -v SortOrder -o "|" -v ReviewDate -o "|" -v EffectiveDate -o "|" -v Properties/Property[1] -o "|" -v Properties/Property[2] -o "|" -v Properties/Property[3] -o "|" -v Properties/Property[4] -n Chapter_4_FATCA_Status_IRS.xml > Chapter_4_FATCA_Status_IRS.csv

return 0

