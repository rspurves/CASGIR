# Feature codes in gazetteer are as follows:
# A Antiquity (non-Roman)
# F Forest or wood
# FM Farm
# H Hill or mountain
# R Antiquity (Roman)
# C City
# T Town
# O Other
# W Water feature
# X All other features
from pathlib import Path
import pandas as pd

class Gazetteer:
    
    def __init__(self):
        self.gaz = dict()
        self.offset = {'C': 2000, 'T':500, 'H':250, 'F':500}
        # Read in gazetteer data
        data_folder = Path('./data')
        fn1 = data_folder / '50kgaz2012.txt'
        os_50k = pd.read_csv(fn1,sep=':', encoding='utf8', header=None)
        os_trimmed = os_50k.drop([0,1,3,4,5,6,7,10,11,12,15,16,17,18,19], axis = 1)
        os_trimmed.columns = ['name','y','x','county','type']
        for index, row in os_trimmed.iterrows():
            name = row['name']
            entry = os_trimmed.iloc[index].values 
            # Store gazetteer in a dictionary of unique names
            if name in self.gaz:
                entries = self.gaz[name]
                entries.append(entry)
                self.gaz[name] = entries
            else:
                self.gaz[name] = [entry]
            
    def getLocation(self, name):
        if (name in self.gaz) == False:
            return('Name not found in gazetteer')

        if len(self.gaz[name]) > 1:
            # We let the user disambiguate
            i = 0
            print("This place name is ambiguous - choose an entry")
            for entry in self.gaz[name]:
                print(f'{i}: {name}, {entry[3]}')
                i = i + 1
            index = int(input("Choose a value:"))
            entry = self.gaz[name][index]
        else:
            entry = self.gaz[name][0]
            
        print(entry)
        x = entry[2]
        y = entry[1]
            
        if entry[4] in self.offset:
            diff = self.offset[entry[4]]
            return (x,y,x-diff, y-diff, x + diff, y + diff)
        else:
            return(x,y)
                                    
    def gazDump(self):
        for name in self.gaz:
            print(name)
            print(self.gaz[name])
            