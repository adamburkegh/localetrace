'''
Compare locale summary files exported in JSON format by localetrace.
'''

import argparse
import datetime
import json
import sys



class LocaleFilter(object):
    def __init__(self,description,comparisonType):
        self.description = description
        self.comparisonType = comparisonType
        self.platforms = {}


class LocaleDiff(object):
    def __init__(self,description,comparisonType,localeIDs):
        LocaleFilter.__init__(self,description,comparisonType)
        self.localeIDs = localeIDs
        self.platforms = {}

    def initLocaleEntry(self, source, platformKey, localeKey):
        None

    def addDiffEntry(self, source, plk1, plk2, lkey1, lkey2, attr, 
                            entry1, entry2):
        None

# This goes into a bit of ugly dictionary-oriented programming, showing its
# history as an overgrown debug script
class LocaleDiffByPlatform(LocaleDiff):
    def initLocaleEntry(self, source, platformKey, localeKey):
        if not platformKey in self.platforms:
            self.platforms[platformKey] = {}
            self.platforms[platformKey]['platform_sig'] = source.platforms[platformKey]['platform_sig']
            self.platforms[platformKey]['locale_exports'] = {}
        if not localeKey in self.platforms[platformKey]['locale_exports']:
            self.platforms[platformKey]['locale_exports'][localeKey] = {}

    def addDiffEntry(self, source, plk1, plk2, lkey1, lkey2, attr, 
                            entry1, entry2):
        self.initLocaleEntry(source, plk1, lkey1)
        self.initLocaleEntry(source, plk2, lkey2 )
        self.platforms[plk1]['locale_exports'][lkey1][attr] = entry1
        self.platforms[plk2]['locale_exports'][lkey2][attr] = entry2


class LocaleDiffByAttr(LocaleDiff):
    def __init__(self,description,comparisonType,localeIDs):
        LocaleDiff.__init__(self,description,comparisonType,localeIDs)
        self.attrs = {}

    def addHalfDiff(self, attr, plk, lkey, entry, source):
        es = str(entry)
        if not es in self.attrs[attr]:
            self.attrs[attr][es] = {}
        if not lkey in self.attrs[attr][es]:
            self.attrs[attr][es][lkey] = []
        ct_use = self.attrs[attr][es][lkey]
        if not plk in ct_use:
            ct_use += [plk]
            self.attrs[attr][es][lkey] = ct_use
        if not plk in self.platforms:
            self.platforms[plk] = source.platforms[plk]['platform_sig']

    def addDiffEntry(self, source, plk1, plk2, lkey1, lkey2, attr, 
                            entry1, entry2):
        if not attr in self.attrs:
            self.attrs[attr] = {}
        self.addHalfDiff(attr, plk1, lkey1, entry1, source )
        self.addHalfDiff(attr, plk2, lkey2, entry2, source )


class LocaleComparison(object):
    def __init__(self):
        self.description = 'Locale comparison including locale exports'
        self.comparisonType = 'Full export'
        self.updateTime = datetime.datetime.now().ctime()
        self.localeExports = {}

    def addLocaleDict(self,localeExportDict):
        # platform_key = len(self.localeExports)+1
        platform_sig = localeExportDict['platform_sig'] 
        platform_key = "{}~{}~{}".format( platform_sig['platform'][:7], 
                                          platform_sig['python_implementation'],
                                          platform_sig['python_version'][:3] ) 
        self.localeExports[platform_key] = localeExportDict

    def filter(self,localeIDs):
        result  = LocaleFilter(
                'Filtered export by locale(s) {}'.format(localeIDs), 'Filtered')
        localeList = localeIDs.split(',')
        result.localeIDs = localeIDs
        for le in self.localeExports:
            lev = self.localeExports[le]
            lr = lev['locale_record']
            for localeID in localeList:
                if localeID in lr:
                    if not le in result.platforms:
                        result.platforms[le] = {}
                        result.platforms[le]['platform_sig'] = lev['platform_sig']
                        result.platforms[le]['locale_exports'] = {}
                    result.platforms[le]['locale_exports'][localeID] = lr[localeID]
        return result

    def diff(self,localeIDs,diffOrder):
        filtered = self.filter(localeIDs)
        if len(filtered.platforms) == 0:
            return filtered
        firstKey = list(filtered.platforms)[0]
        firstPlatform = filtered.platforms[firstKey]
        firstLocaleKey = list(firstPlatform['locale_exports'])[0]
        firstLR = firstPlatform['locale_exports'][firstLocaleKey]
        result  = diffOrder(
                    'Filtered export {} with attribute diff'.format(localeIDs),
                    'Attribute diff',
                    localeIDs)
        for attr in firstLR:
            for platformKey in filtered.platforms:
                platformRecord = filtered.platforms[platformKey]
                for le in platformRecord['locale_exports']:
                    lev = platformRecord['locale_exports'][le]
                    if firstLR[attr] != lev[attr]:
                        result.addDiffEntry(filtered, platformKey, firstKey, 
                                            le, firstLocaleKey, attr,
                                            lev[attr], firstLR[attr] )
        return result





def initComparison( localeExportFiles ):
    lc = LocaleComparison()
    for leFile in localeExportFiles:
        f = open( leFile )
        le = json.load( f )
        lc.addLocaleDict(le)
    return lc

def pretty(obj):
    print (json.dumps( obj.__dict__ , sort_keys=True, indent=4 ) )


def main():
    parser = argparse.ArgumentParser("Compare locales held in locale export files")
    parser.add_argument('localeExport',nargs='*')
    parser.add_argument('--filter', help='Filter by comma-separated locale strings')
    parser.add_argument('--diff', action='store_true', help='Display only differences. Assumes --filter')
    parser.add_argument('--order', choices=['platform','attribute'], 
                    default='attribute', help='Difference order')
    parser.add_argument('--format', choices=['plain','json'], 
                    default='json', help='Output format')
    args = parser.parse_args()
    lc = initComparison(args.localeExport)
    formatter = pretty
    if args.filter:
        if args.diff:
            diffOrder = {'platform': LocaleDiffByPlatform,
                        'attribute': LocaleDiffByAttr }
            formatter (lc.diff(args.filter, diffOrder[args.order]) )
        else:
            formatter (lc.filter(args.filter) ) 
    else: 
        pretty( lc )


if __name__ == '__main__':
    main()


