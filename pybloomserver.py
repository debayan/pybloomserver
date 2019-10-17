#!/usr/bin/python
import json
from flask import request
from flask import Flask
from gevent.pywsgi import WSGIServer
from pybloom import ScalableBloomFilter
import sys

print("loading blooms")
try:
    f = open('./blooms/wikidatabloom1hoppredicate.pickle')
    bloom1hoppred = ScalableBloomFilter.fromfile(f)
    f.close()
    f = open('./blooms/wikidatabloom1.5hopqualifiers.pickle')
    bloomqualifier = ScalableBloomFilter.fromfile(f) # ihoppred_qualifier
    f.close()
    f = open('./blooms/wikidatabloom1hopentity.pickle')
    bloom1hopentity = ScalableBloomFilter.fromfile(f)
    f.close()
    f = open('./blooms/bloom1hoptypeofentity.pickle')
    bloom1hoptypeofentity = ScalableBloomFilter.fromfile(f)
    f.close()
except Exception,e:
    print e
    sys.exit(1)
print "Blooms loaded" 

app = Flask(__name__)

@app.route('/bloomconnections', methods=['POST'])
def bloomconnections():
    d = request.get_json(silent=True)
    connections = []
    entities = d['entities']
    relations = d['relations']
    for idx,entity in enumerate(entities):
        for relation in relations:
            for relationuri in relation['uris']:
                bloomstring = entity['uri']+':'+relationuri
                if bloomstring in bloom1hoppred:
                    connections.append({'bloomstring':bloomstring, 'connectiontype':'1hoppred'})
                if bloomstring in bloomqualifier:
                    connections.append({'bloomstring':bloomstring, 'connectiontype':'1.5hopqualifier'})
                if bloomstring in bloom1hoptypeofentity:
                    connections.append({'bloomstring':bloomstring, 'connectiontype':'1hoptypeofentity'})
        for entity2 in entities[idx+1:]:
           bloomstring = entity['uri']+':'+entity2['uri']
           if bloomstring in bloom1hoptypeofentity:
               connections.append({'bloomstring':bloomstring, 'connectiontype':'1hoptypeofentity'})
           if bloomstring in bloom1hopentity:
               connections.append({'bloomstring':bloomstring, 'connectiontype':'1hopentity'})
    print("Connections found: %d"%len(connections))
    print("Original entities and relations counts: %d and %d"%(len(entities),len(relations)))
    return json.dumps({'input':d,'bloomconnections':connections})

if __name__ == '__main__':
    #d = json.loads(open('sample.json').read())
    #res = getconnections(d)
    http_server = WSGIServer(('', int(sys.argv[1])), app)
    http_server.serve_forever()
                          
