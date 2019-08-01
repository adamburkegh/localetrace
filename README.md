# Localetrace

Basic explorer scripts for comparing locale behaviour on different versions of Python, with different underlying platforms. 

This can be useful as it's often not possible to run all possible variants from the one process, or even the one computer.

## localetrace

Expose and export locale details using python locale module interface. See help for details.


## localecomp

Compare differences in locale using JSON files exported. See help for details.


# Example uses

## Quick visual scan of two locales

Quickly look at the contents of two locales. The default format is --plain.

```
$ python2 localetrace.py en_AU sv_FI 
CPython 2.7.14 CYGWIN_NT-10.0-2.11.2-0.329-5-3-x86_64-64bit
**sv_FI**
currency_symbol  :         EUR
decimal_point    :            ,
frac_digits      :            2
getlocale()      :('sv_FI', 'ISO8859-1')
grouping         :       [3, 0]
int_curr_symbol  :         EUR
int_frac_digits  :            2
mon_decimal_point:            ,
mon_grouping     :       [3, 0]
mon_thousands_sep:            ▒
n_cs_precedes    :            0
n_sep_by_space   :            1
n_sign_posn      :            1
negative_sign    :            -
p_cs_precedes    :            0
p_sep_by_space   :            1
p_sign_posn      :            1
positive_sign    :
thousands_sep    :            ▒
**en_AU**
currency_symbol  :            $
decimal_point    :            .
frac_digits      :            2
getlocale()      :('en_AU', 'ISO8859-1')
grouping         :       [3, 0]
int_curr_symbol  :         AUD
int_frac_digits  :            2
mon_decimal_point:            .
mon_grouping     :       [3, 0]
mon_thousands_sep:            ,
n_cs_precedes    :            1
n_sep_by_space   :            0
n_sign_posn      :            3
negative_sign    :            -
p_cs_precedes    :            1
p_sep_by_space   :            0
p_sign_posn      :            3
positive_sign    :
thousands_sep    :            ,
```

## Export some locales to JSON

```
$ python2 localetrace.py en_AU en_GB zh_CN sv_SE sv_FI en_US --format json > cygwinpy2.json
```



## Underscore and dash comparison for en_GB

Differences between en_GB and en-GB behaviour on Windows and cygwin. Shows wacky currency symbol variation and includes bonus exception on `getlocale()`.

```
> python localecomp.py winpy3.json cygwinpy2.json cygwinpy3.json jy.json  --filter en_GB,en-GB  --diff --order attribute
{
    "attrs": {
        "currency_symbol": {
            "$": {
                "en_GB": [
                    "Windows~CPython~3.5"
                ]
            },
            "\u00a3": {
                "en-GB": [
                    "Windows~CPython~3.5"
                ]
            },
            "\u00c2\u00a3": {
                "en-GB": [
                    "Java-11~Jython~2.7"
                ],
                "en_GB": [
                    "Java-11~Jython~2.7"
                ]
            }
        },
        "getlocale()": {
            "Exception": {
                "en-GB": [
                    "Windows~CPython~3.5"
                ]
            },
            "['en_GB', 'ISO8859-1']": {
                "en_GB": [
                    "Windows~CPython~3.5",
                    "CYGWIN_~CPython~2.7",
                    "CYGWIN_~CPython~3.6"
                ]
...
    "comparisonType": "Attribute diff",
    "description": "Filtered export en_GB,en-GB with attribute diff",
    "localeIDs": "en_GB,en-GB",
    "platforms": {
        "CYGWIN_~CPython~2.7": {
            "platform": "CYGWIN_NT-10.0-2.11.2-0.329-5-3-x86_64-64bit",
            "python_implementation": "CPython",
            "python_version": "2.7.14"
        },
...
```


# Limitations or extensions

Dealing with character encodings is usually part of the fun of dealing with locales, but this isn't a parameter in these scripts.


# Sample export files

Some basic export files are included in the project for comparison convenience. They do not attempt a comprehensive export of the locale databases. 


