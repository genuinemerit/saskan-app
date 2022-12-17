import os
LF = "\n"

for dirname, dirnames, filenames in os.walk('.'):
    for filename in filenames:
        if '.csv' in filename.lower():
            print (LF, filename)
            rn = 0
            fcsv = open(os.path.join(dirname, filename), "rt", encoding="utf-8")
            fcsv.close
            # chop line feeds
            fcsv = [line[:-1] for line in fcsv]
            fdata = []
            for row in fcsv:
                rn += 1
                if rn == 1:
                    hdrs = row.split(",")
                    print (hdrs)
                else:
                    fdata.append(row.split(","))
            print (fdata)
            del fdata
