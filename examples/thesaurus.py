
import xmldestroyer as xd
import sys

def swesaurus(infile):
    def SenseRelation(s, d, xs, ps):
        return d['targets'], ps['Sense'].attrib['id']
    return xd.iterator(**locals())

def swesaurus2(infile):
    def SenseRelation(s, d, xs, ps):
        return d['targets']
    def Sense(s, d, xs, ps):
        for target in xs:
            yield target, d['id']
    return xd.iterator(**locals())

if __name__ == '__main__':
    for target, sense in swesaurus(sys.argv[1]):
        print((target + '\t' + sense).encode('utf-8'))
