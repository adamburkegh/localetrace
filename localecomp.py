
import argparse
import datetime
import json
import sys



class LocaleFilter(object):
    def __init__(self,description,comparisonType):
        self.description = description
        self.comparisonType = comparisonType
        self.platforms = {}


class LocaleComparison(object):
    def __init__(self):
        self.description = 'Locale comparison including locale exports'
        self.comparisonType = 'Full export'
        self.updateTime = datetime.datetime.now().ctime()
        self.localeExports = {}

    def addLocale(self,localeExport):
        platform_key = len(self.localeExports)+1
        self.localeExports[platform_key] = localeExport.__dict__

    def addLocaleDict(self,localeExportDict):
        platform_key = len(self.localeExports)+1
        self.localeExports[platform_key] = localeExportDict

    def filter(self,localeIDs):
        result  = LocaleFilter(
                'Filtered export by locale(s) {}'.format(localeIDs), 'Filtered')
        localeList = localeIDs.split(',')
        result.localeIDs = localeIDs
        result.localeExports = {}
        for le in self.localeExports:
            lev = self.localeExports[le]
            lr = lev['locale_record']
            for localeID in localeList:
                # This filterKey is a little hacky, another level of structure
                # would be better
                filterKey = str(le) + '__' + localeID 
                if localeID in lr:
                    result.localeExports[filterKey] = {}
                    result.localeExports[filterKey]['locale_record'] = lr[localeID]
                    result.localeExports[filterKey]['platform_sig'] = lev['platform_sig']
        return result

    def initLocaleEntry(self, diff, source, key):
        localeEntry = {}
        localeEntry['platform_sig'] = \
                  source.localeExports[key]['platform_sig']
        diff.localeExports[key] = localeEntry

    def diff(self,localeIDs):
        filtered = self.filter(localeIDs)
        if len(filtered.localeExports) == 0:
            return filtered
        firstKey = list(filtered.localeExports)[0]
        firstLR = filtered.localeExports[firstKey]['locale_record']
        firstPlatform = filtered.localeExports[firstKey]['platform_sig']
        result  = LocaleFilter('Filtered export {} with attribute diff'.format(localeIDs),
                                'Attribute diff')
        result.localeIDs = localeIDs
        result.localeExports = {}
        for attr in firstLR:
            if attr == 'platform_sig':
                continue
            for le in filtered.localeExports:
                lev = filtered.localeExports[le]['locale_record']
                if firstLR[attr] != lev[attr]:
                    if not le in result.localeExports:
                        self.initLocaleEntry(result, filtered, le)
                    if not firstKey in result.localeExports:
                        self.initLocaleEntry(result, filtered, firstKey )
                    result.localeExports[le][attr] = lev[attr]
                    result.localeExports[firstKey][attr] = firstLR[attr]
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
    args = parser.parse_args()
    lc = initComparison(args.localeExport)
    if args.filter:
        if args.diff:
            pretty (lc.diff(args.filter) )
        else:
            pretty (lc.filter(args.filter) ) 
    else: 
        pretty( lc )


if __name__ == '__main__':
    main()


