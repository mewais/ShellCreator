#!/usr/bin/python3
##**************************************************************************##
##                               FullScaleCAD                               ##
##                                                                          ##
## Copyright (C) Mohammad Ewais - All Rights Reserved                       ##
## Unauthorized copying of this file, via any medium is strictly prohibited ##
## Proprietary and confidential                                             ##
## Written by:                                                              ##
##      Mohammad Ewais "mohammad.a.ewais@gmail.com"                         ##
##**************************************************************************##

# https://stackoverflow.com/a/59270522/2328163
def stringToNumber(string):
    if("." in string):
        try:
            res = float(string)
        except:
            raise ValueError
    elif(string.isdigit()):
        res = int(string)
    else:
        raise ValueError
    return(res)
