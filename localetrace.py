'''
Show or export locale details with the identifying platform details. 
'''

import argparse
import json
import locale
import platform
import sys



class LocaleExport(object):
    def __init__(self):
        platform_sig = {}
        self.platform_sig = platform_sig
        platform_sig['python_implementation'] = platform.python_implementation()
        platform_sig['python_version'] = platform.python_version()
        platform_sig['platform'] = platform.platform() 
        self.locale_record = {}

    def recordCurrentLocale(self,localeStr):
        lc = locale.localeconv()
        self.locale_record[localeStr] = {}
        self.locale_record[localeStr] = lc
        try:
            ctlocale = locale.getlocale()
        except:
            ctlocale = "Exception"
        self.locale_record[localeStr]['getlocale()'] = ctlocale


class LocaleExporter(object):
    def export(self,localeExport):
        None


class LocaleBasicStringExport(LocaleExporter):
    def exportCurrentLocale(self,localeStr,localeExport):
        lc = localeExport.locale_record[localeStr]
        keys = sorted(lc.keys())
        result = ("**{}**\n".format(localeStr))
        for key in keys:
            try:
                result += "{:<17}:{:>13}\n".format(key,str(lc[key])) 
            except:
                result += "{:<17}:{:>13}\n".format(key,"<unprintable>") 
        return result

    def export(self,localeExport):
        result = "{} {} {}\n".format(
                localeExport.platform_sig['python_implementation'],
                localeExport.platform_sig['python_version'],
                localeExport.platform_sig['platform'])
        for localeStr in localeExport.locale_record:
            result += self.exportCurrentLocale(localeStr,localeExport)
        return result


class LocaleJsonExporter(LocaleExporter):
    def export(self,localeExport):
        return json.dumps(localeExport.__dict__, ensure_ascii=False)


def changeLocale(localeStr,localeExport):
    locale.setlocale(locale.LC_ALL,localeStr)
    localeExport.recordCurrentLocale(localeStr)

def traceLocale(locales,exporter):
    localeExport = LocaleExport()
    for localeStr in locales:
        changeLocale(localeStr, localeExport) 
    print ( exporter.export(localeExport) )


def main():
    parser = argparse.ArgumentParser("Make locale details available for review")
    parser.add_argument('localeID', nargs='+')
    parser.add_argument('--format', choices=['json','plain'], default='plain' )
    args = parser.parse_args()
    exporters = {'json': LocaleJsonExporter(),
                 'plain': LocaleBasicStringExport() }
    traceLocale( args.localeID, exporters[args.format] )


if __name__ == '__main__':
    main()

