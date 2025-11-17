import OSGridConverter #To convert from =SGB36 to WGS84
import pandas as pd #To use pandas for elegant data handling

class SpatialIndex:
    
    def __init__(self, resolution, sample):
        
        sample.dropna() # Get rid of problematic rows with nas
        
        for i in sample.index:
            try:
                g = OSGridConverter.latlong2grid (sample.at[i, 'lat'], sample.at[i, 'lon'], tag = 'WGS84')
                sample.at[i, 'x'] = g.E
                sample.at[i, 'y'] = g.N
            except ValueError:
                #print("Problem with a document", sample.at[i,'id'])
                sample = sample.drop(i)

        # Now we can set up the parameters for our index        
        self.resolution = resolution

        self.minx = sample['x'].min()
        self.maxx = sample['x'].max()
        self.miny = sample['y'].min()
        self.maxy = sample['y'].max()

        w = self.maxx - self.minx
        h = self.maxy - self.miny

        nc = int(w/self.resolution) + 1
        nr = int(h/self.resolution) + 1

        #print(maxx, minx, maxy, miny)
        #print(nr, nc)

        #Build the spatial index now
        self.spatialIndex = pd.DataFrame(index=range(nc),columns=range(nr))

        #Now we populate the index with document ids
        for index, row in sample.iterrows():
            i = int((row['x'] - self.minx)/self.resolution)
            j = int((row['y'] - self.miny)/self.resolution)
            id = row['id']
    
            #print(row['id'])
            #print(row['x'],row['y'],i,j)
            if pd.isnull(self.spatialIndex.at[i,j]):
                self.spatialIndex.at[i,j] = {id:(row['x'],row['y'])}
            else:
                names = self.spatialIndex.at[i,j]
                names.update({id:(row['x'],row['y'])})
                self.spatialIndex.at[i,j] = names

        
    def rangeQuery(self, dist, point):
        x1 = point[0] - dist/2
        x2 = point[0] + dist/2
        y1 = point[1] - dist/2
        y2 = point[1] + dist/2
    
        i1 = int((x1 - self.minx)/self.resolution)
        j1 = int((y1 - self.miny)/self.resolution)
        i2 = int((x2 - self.minx)/self.resolution) + 1
        j2 = int((y2 - self.miny)/self.resolution) + 1

        # Retrieve only the relevant part of the index
        result = self.spatialIndex.iloc[i1:i2, j1:j2]
        # Turn the data frame into a 1d list
        tlist = result.values.flatten()
        # Remove all the nans
        filtered = filter(lambda i:not(type(i) is float), tlist)
        
        #Rank by distance
        ranked = {}
        for item in filtered:
            for key in item:
                d = self.dist(point, item[key])
                #print(key, item[key], dist)
                ranked[key] = d    
        ranked = dict(sorted(ranked.items(), key = lambda x: x[1], reverse=False))
                
        return ranked
    
    def dist(self, p1, p2):
        #print(p1[0], p1[1], p2[0], p2[1])
        dist = (((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2)) ** 0.5
        #print(dist)
        return dist