import os
import sys
import shutil
import datetime
from xml.etree import ElementTree as ET
from collections import Counter

# Returns arrray of [lat, lon] for the given node
def nodeGPS(node):
  return [node.attrib['lat'], node.attrib['lon']]

# Returns node with the specified id
def nodeByID(id):
  for n in nodes:
    if n.attrib['id'] == id:
      return n
  raise Exception('Requested a node that does not exist!')

# Returns lat/lon where the node with the specified id is located
def pos(id):
  return nodeGPS(nodeByID(id))

# Extract the runway data and save to the rwys array
def createRunway(w):
    tags = w.findall('tag')
    name = [t for t in tags if t.attrib['k'] == 'ref']
    nd = [pos(n.attrib['ref']) for n in w if n.tag == 'nd']
    if name:
        rwys.append({'name': name[0].attrib['v'], 'points': nd})
    else:
        raise Warning('Unable to create runway because it isn\'t named in the source data!')

# Extract the taxiway data and save to the twys array
def createTaxiway(w):
    tags = w.findall('tag')
    name = [t for t in tags if t.attrib['k'] == 'ref']
    nd = [pos(n.attrib['ref']) for n in w if n.tag == 'nd']
    if name:
        twys.append({'name': name[0].attrib['v'], 'points': nd})
    # else:
    #     raise Warning('Unable to create runway because it isn\'t named in the source data!')

#Extract the parking position data and save to the prkg array
def createParking(n):
    tags = n.findall('tag')
    name = [t for t in tags if t.attrib['k'] == 'ref']
    if name:
        prkg.append({'name':name[0].attrib['v'], 'position':pos(n.attrib['id'])})


# Generate TWRTrainer File
def writeToFile(outFile):
    # String Definitions
    autogen = '; Data generated via osm2apt from www.github.com/vZMA/utils\n'
    gendate = '{}{}{}'.format('; Generated ', datetime.datetime.now().strftime("%A, %B %d, %Y, %H:%M:%S"), '\n')
    osmattr = '; Map Data sourced from: © OpenStreetMap contributors\n'
    
    # Open the file and begin writing
    print('Writing results to file...')
    of = open(outFile, 'w')
    of.truncate()
    of.write('{}{}{}'.format(autogen, gendate, osmattr))
    of.write('\nicao=\nmagnetic variation=\nfield elevation=\npattern elevation=\npattern size=\ninitial climb props=\ninitial climb jets=\njet airlines=\nturboprop airlines=\nregistration=\n')
    
    # Write parking positions to file
    of.write('\n\n; ---------- PARKING ----------')
    for g in prkg:
        of.write('{}{}{}'.format('\n[PARKING ', g['name'], ']\n'))
        of.write('{}{}{}{}'.format(g[0], ' ', g[1], '\n'))
    
    # Write runways to file
    of.write('\n\n; ---------- RUNWAYS ----------')
    for r in rwys:
        of.write('{}{}{}'.format('\n[RUNWAY ', r['name'], ']\n'))
        of.write('displaced threshold=0/0\nturnoff=right\n')
        for p in r['points']:
            of.write('{}{}{}{}'.format(p[0], ' ', p[1], '\n'))
    
    # Write taxiways to file
    of.write('\n\n; ---------- TAXIWAYS ----------')
    for t in twys:
        of.write('{}{}{}'.format('\n[TAXIWAY ', t['name'], ']\n'))
        for p in t['points']:
            of.write('{}{}{}{}'.format(p[0], ' ', p[1], '\n'))

# Generate qGIS-importable files for resolving non-intersections
def out_for_qGIS(outDir):
    # Create the output folder structure
    outDir = os.path.join(outDir, 'qGIS_files')
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    print('Saving to \'{}\''.format(outDir))

    # Write parking positions to file
    qgis_prkg = []
    of = open(os.path.join(outDir, '~ALL_PARKING.wkt'), 'w')
    of2 = open(os.path.join(outDir, '~ALL_PARKING-qGIS.wkt'), 'w')
    for g in prkg:
        of.write('[PARKING {}]\n{} {}\n\n'.format(g['name'], g['position'][0], g['position'][1]))
        of2.write('{};POINT({} {})\n'.format(g['name'], g['position'][1], g['position'][0]))


    
    # # Write runways to file
    # qgis_rwys = []
    # for r in rmap:
    #     segments = [x for x in rwys if x['name'] == r]
    #     for idx,s in enumerate(segments):
    #         print('Exporting {} of {} segment(s) of {}.'.format(idx+1,len(segments),s['name']))
    #         of = open(os.path.join(outDir, '{}{}{}'.format(s['name'].replace('/','-'), '_{}'.format(idx) if idx>0 else '', '.wkt')), 'w')
    #         lines = []

    #         # Make line pairs out of point rows
    #         for i in range(len(s['points'])):
    #             lines.append(s['points'][i:i+2])
    #         lines.pop() # Remove line connecting end back to start

    #         # Write line pairs to file
    #         for l in lines:
    #             stuff = '{};LINESTRING({} {}, {} {})\n'.format(s['name'], l[0][1], l[0][0], l[1][1], l[1][0])
    #             qgis_rwys.append(stuff)
    #             of.write(stuff)

    #     # Write all runways to 'ALL_RUNWAYS' file
    #     of = open(os.path.join(outDir, '~ALL_RUNWAYS.wkt'), 'w')
    #     for line in qgis_rwys:
    #         of.write(line)




    # # Write taxiways to file
    # qgis_twys = []
    # for t in tmap:
    #     segments = [x for x in twys if x['name'] == t]
    #     for idx,s in enumerate(segments):
    #         print('Exporting {} of {} segment(s) of {}.'.format(idx+1,len(segments),s['name']))
    #         of = open(os.path.join(outDir, '{}{}{}'.format(s['name'].replace('/','-'), '_{}'.format(idx) if idx>0 else '', '.wkt')), 'w')
    #         lines = []

    #         # Make line pairs out of point rows
    #         for i in range(len(s['points'])):
    #             lines.append(s['points'][i:i+2])
    #         lines.pop() # Remove line connecting end back to start

    #         # Write line pairs to file
    #         for l in lines:
    #             stuff = '{};LINESTRING({} {}, {} {})\n'.format(s['name'], l[0][1], l[0][0], l[1][1], l[1][0])
    #             qgis_twys.append(stuff)
    #             of.write(stuff)

    #     # Write all runways to 'ALL_RUNWAYS' file
    #     of = open(os.path.join(outDir, '~ALL_TAXIWAYS.wkt'), 'w')
    #     for line in qgis_twys:
    #         of.write(line)




##### BODY #####
# Parse the file and build the arrays
osmFile = 'map.osm'
inFile = os.path.abspath(osmFile)
print('Parsing OSM data...')
data = ET.parse(inFile)
ways = data.findall('way')
nodes = data.findall('node')
rwys, twys, prkg = [],[],[]
rmap, tmap, pmap = {},{},{}

# Gather the data
print('Thinking...')
for w in ways:
    tags = w.findall('tag')

    # if any tags have value "runway"
    if any(t.attrib['k']=='aeroway' and t.attrib['v']=='runway'for t in tags):
        createRunway(w)

    # if any tags have value "taxiway"
    if any(t.attrib['k']=='aeroway' and t.attrib['v']=='taxiway'for t in tags):
        createTaxiway(w)

for n in nodes:
    tags = n.findall('tag')

    # if any tags have value "taxiway"
    if any(t.attrib['k']=='aeroway' and t.attrib['v']=='gate'for t in tags):
        createParking(n)

rmap, tmap, pmap = dict(Counter([i['name'] for i in rwys])), dict(Counter([i['name'] for i in twys])), dict(Counter([i['name'] for i in prkg]))



##### CLOSING #####
print('Finished!')
print('------------------------------------------------------------------------------')
print('Runways parsed  | ', len(rwys))
# shit1 = [r['name'] for r in rwys]
# shit2 = shit1.sort()
# print(type(shit1))
# print(type(shit2))
# print('shit1: {}'.format(shit1))
# print('shit2: {}'.format(shit2))
print('    --> ', ' , '.join(sorted([r['name'] for r in rwys])))
print('Taxiways parsed | ', len(twys))
print('    --> ', ' , '.join(sorted([r['name'] for r in twys])))
print('------------------------------------------------------------------------------')

##### WRITING TO FILE #####
# outputFileExtension = '.apt'
# writeToFile(os.path.abspath(osmFile.replace('.osm', outputFileExtension)))
out_for_qGIS(os.path.dirname(inFile))
print('File export complete.')