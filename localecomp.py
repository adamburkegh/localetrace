
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
        for le in self.localeExports:
            lev = self.localeExports[le]
            lr = lev['locale_record']
            for localeID in localeList:
                # This filterKey is a little hacky, another level of structure
                # would be better
                filterKey = str(le) + '__' + localeID 
                if localeID in lr:
                    if not le in result.platforms:
                        result.platforms[le] = {}
                        result.platforms[le]['platform_sig'] = lev['platform_sig']
                        result.platforms[le]['locale_exports'] = {}
                    result.platforms[le]['locale_exports'][localeID] = lr[localeID]
        return result

    def initLocaleEntry(self, diff, source, platformKey, localeKey):
        platformEntry = {}
        if not platformKey in diff.platforms:
            diff.platforms[platformKey] = {}
            diff.platforms[platformKey]['platform_sig'] = source.platforms[platformKey]['platform_sig']
            diff.platforms[platformKey]['locale_exports'] = {}
        if not localeKey in diff.platforms[platformKey]['locale_exports']:
            diff.platforms[platformKey]['locale_exports'][localeKey] = {}
        

    def diff(self,localeIDs):
        filtered = self.filter(localeIDs)
        if len(filtered.platforms) == 0:
            return filtered
        firstKey = list(filtered.platforms)[0]
        firstPlatform = filtered.platforms[firstKey]
        firstLocaleKey = list(firstPlatform['locale_exports'])[0]
        firstLR = firstPlatform['locale_exports'][firstLocaleKey]
        result  = LocaleFilter('Filtered export {} with attribute diff'.format(localeIDs),
                                'Attribute diff')
        result.localeIDs = localeIDs
        result.platforms = {}
        for attr in firstLR:
            for platformKey in filtered.platforms:
                platformRecord = filtered.platforms[platformKey]
                for le in platformRecord['locale_exports']:
                    lev = platformRecord['locale_exports'][le]
                    if firstLR[attr] != lev[attr]:
                        self.initLocaleEntry(result, filtered, platformKey, le)
                        self.initLocaleEntry(result, filtered, firstKey, 
                                                    firstLocaleKey )
                        result.platforms[platformKey]['locale_exports'][le][attr] = lev[attr]
                        result.platforms[firstKey]['locale_exports'][firstLocaleKey][attr] = firstLR[attr]
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


