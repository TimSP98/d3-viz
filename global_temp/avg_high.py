import pandas as pd
import json
import urllib.request
from tqdm import tqdm
import numpy as np

# GLOBAL CONSTANTS #
col_names = ["Date number","Year","Month","Day","Day of the Year","Temperature"]
base_high = 14.42
url = "http://berkeleyearth.lbl.gov/auto/Global/Complete_TMAX_daily.txt"

# HELPER FUNCTIONS #
def stripper(line: str) -> list:
    ls = line.split()
    ls = map(lambda x: x.strip(),ls)
    final = []
    for ele in ls:
        if ele: final.append(ele)
    assert len(final) == 6

    return final

# PARSING FILE #
table = []
infile = urllib.request.urlopen(url)
for line in tqdm(infile, desc='Data Parsing'):
    line = line.decode("UTF-8").strip()
    if line:
        if line[0] == "%":
            continue
        table.append(stripper(line))

df = pd.DataFrame(table,columns=col_names)
df.iloc[:,1:5] = df.iloc[:,1:5].astype(int)
df.iloc[:,5] = df.iloc[:,5].astype(float) + base_high
years = np.unique(df.iloc[:,1])



lines = []
# DF SUMMARY PROCESSING #
for y in years:
    tmp = {}
    mask = df["Year"] == y
    q1 =  df[mask].iloc[:,5].quantile(q=0.25)
    median = df[mask].iloc[:,5].quantile(q=0.5)
    q3 =  df[mask].iloc[:,5].quantile(q=0.75)
    interQrange = q3 - q1
    minb = max(min(df[mask].iloc[:,5]),q1-1.5*interQrange)
    maxb = min(max(df[mask].iloc[:,5]),q3+1.5*interQrange)
    tmp["year"] = y
    tmp["min"] = minb
    tmp["q1"] = q1
    tmp["median"] = median
    tmp["q3"] = q3
    tmp["max"] = maxb
    minmask = df[mask].iloc[:,5] < minb
    maxmask = df[mask].iloc[:,5] > maxb
    mino = list(df[mask][minmask].iloc[:,5])
    maxo = list(df[mask][maxmask].iloc[:,5])
    outliers = mino + maxo
    if outliers: tmp['outliers'] = outliers
    lines.append(tmp)


    
of = open("high_temps_summary.json","w")
json.dump(lines,of)
of.close()






