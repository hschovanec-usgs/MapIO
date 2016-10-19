#!/usr/bin/env python

from __future__ import print_function

#stdlib imports
import os.path
import sys

import numpy as np

#hack the path so that I can debug these functions if I need to
homedir = os.path.dirname(os.path.abspath(__file__)) #where is this script?
mapiodir = os.path.abspath(os.path.join(homedir,'..'))
sys.path.insert(0,mapiodir) #put this at the front of the system path, ignoring any installed mapio stuff

from mapio.dataset import DataSetException
from mapio.geodict import GeoDict

def test():
    #these values taken from the shakemap header of: 
    #http://earthquake.usgs.gov/realtime/product/shakemap/ak12496371/ak/1453829475592/download/grid.xml

    print('Testing various dictionaries for consistency...')
    
    print('Testing consistent dictionary...')
    #this should pass, and will serve as the comparison from now on
    gdict = {'xmin':-160.340600,'xmax':-146.340600,
             'ymin':54.104700,'ymax':65.104700,
             'dx':0.025000,'dy':0.025000,
             'ny':441,'nx':561}
    gd = GeoDict(gdict,adjust=None)
    print('Consistent dictionary passed.')

    print('Testing dictionary with inconsistent dimensions...')
    #this should pass
    gdict = {'xmin':-160.340600,'xmax':-146.340600,
             'ymin':54.104700,'ymax':65.104700,
             'dx':0.026000,'dy':0.026000,
             'ny':441,'nx':561}
    gd3 = GeoDict(gdict,adjust='res')
    assert gd3 == gd
    print('Dimensions modification passed.')

    print('Testing dictionary with inconsistent lower right corner...')
    #this should pass
    gdict = {'xmin':-160.340600,'xmax':-146.350600,
             'ymin':54.103700,'ymax':65.104700,
             'dx':0.025000,'dy':0.025000,
             'ny':441,'nx':561}
    gd4 = GeoDict(gdict,adjust='bounds')
    assert gd4 == gd
    print('Corner modification passed.')

    print('Testing to make sure lat/lon and row/col calculations are correct...')
    #make sure the lat/lon row/col calculations are correct
    ndec = int(np.abs(np.log10(GeoDict.EPS)))
    lat,lon = gd.getLatLon(0,0)
    dlat = np.abs(lat-gd.ymax)
    dlon = np.abs(lon-gd.xmin)
    assert dlat < GeoDict.EPS and dlon < GeoDict.EPS
    row,col = gd.getRowCol(lat,lon)
    assert row == 0 and col == 0

    lat,lon = gd.getLatLon(gd.ny-1,gd.nx-1)
    dlat = np.abs(lat-gd.ymin)
    dlon = np.abs(lon-gd.xmax)
    assert dlat < GeoDict.EPS and dlon < GeoDict.EPS
    row,col = gd.getRowCol(lat,lon)
    assert row == (gd.ny-1) and col == (gd.nx-1)
    print('lat/lon and row/col calculations are correct.')

    print('Testing a dictionary for a global grid...')
    #this is the file geodict for Landscan - should pass muster
    globaldict = {'nx': 43200,
                  'ny': 20880,
                  'dx': 0.00833333333333,
                  'xmax': 179.99583333318935,
                  'xmin': -179.99583333333334,
                  'dy': 0.00833333333333,
                  'ymax': 83.99583333326376,
                  'ymin': -89.99583333333334}
    gd5 = GeoDict(globaldict)
    lat,lon = gd5.getLatLon(gd5.ny-1,gd5.nx-1)
    dlat = np.abs(lat-gd5.ymin)
    dlon = np.abs(lon-gd5.xmax)
    assert dlat < GeoDict.EPS and dlon < GeoDict.EPS
    print('Global grid is internally consistent.')

    #Test class methods for creating a GeoDict
    print('Testing whether GeoDict creator class methods work...')
    xmin = -121.05333277776235
    xmax = -116.03833388890432
    ymin = 32.138334444506171
    ymax = 36.286665555493826
    dx = 0.0083333333333333332
    dy = 0.0083333333333333332
    gd6 = GeoDict.createDictFromBox(xmin,xmax,ymin,ymax,dx,dy,inside=False)
    assert gd6.xmax > xmax
    assert gd6.ymin < ymin
    print('Created dictionary (outside) is correct.')
    gd7 = GeoDict.createDictFromBox(xmin,xmax,ymin,ymax,dx,dy,inside=True)
    assert gd7.xmax < xmax
    assert gd7.ymin > ymin
    print('Created dictionary (inside) is correct.')
    xspan = 2.5
    yspan = 2.5
    gd8 = GeoDict.createDictFromCenter(xmin,ymin,dx,dy,xspan,yspan)
    print('Created dictionary (from center point) is valid.')

    print('Testing a geodict with dx/dy values that are NOT the same...')
    xmin,xmax,ymin,ymax = (-121.06166611109568, -116.03000055557099, 32.130001111172838, 36.294998888827159)
    dx,dy = (0.009999722214505959, 0.009999444413578534)
    td = GeoDict.createDictFromBox(xmin,xmax,ymin,ymax,dx,dy)
    print('Passed testing a geodict with dx/dy values that are NOT the same...')

    #test getBoundsWithin
    #use global grid, and then a shakemap grid that we can get
    print('Testing getBoundsWithin...')
    grussia = {'xmin':155.506400,'xmax':161.506400,
               'ymin':52.243000,'ymax':55.771000,
               'dx':0.016667,'dy':0.016642,
               'nx':361,'ny':213}
    gdrussia = GeoDict(grussia,adjust='res')
    sampledict = gd5.getBoundsWithin(gdrussia)
    xSmaller = sampledict.xmin > grussia['xmin'] and sampledict.xmax < grussia['xmax']
    ySmaller = sampledict.ymin > grussia['ymin'] and sampledict.ymax < grussia['ymax']
    assert xSmaller and ySmaller
    assert gd5.isAligned(sampledict)
    print('getBoundsWithin returned correct result.')

    print('Testing isAligned() method...')
    gd = GeoDict({'xmin':0.5,'xmax':3.5,
                  'ymin':0.5,'ymax':3.5,
                  'dx':1.0,'dy':1.0,
                  'nx':4,'ny':4})

    inside_aligned = GeoDict({'xmin':1.5,'xmax':2.5,
                              'ymin':1.5,'ymax':2.5,
                              'dx':1.0,'dy':1.0,
                              'nx':2,'ny':2})
    inside_not_aligned = GeoDict({'xmin':2.0,'xmax':3.0,
                                  'ymin':2.0,'ymax':3.0,
                                  'dx':1.0,'dy':1.0,
                                  'nx':2,'ny':2})
    assert gd.isAligned(inside_aligned)
    assert not gd.isAligned(inside_not_aligned)
    print('Passed isAligned() method...')

    print('Testing getAligned method...')
    popdict = GeoDict({'dx': 0.00833333333333,
                       'dy': 0.00833333333333,
                       'nx': 43200,
                       'ny': 20880,
                       'xmax': 179.99583333318935,
                       'xmin': -179.99583333333334,
                       'ymax': 83.99583333326376,
                       'ymin': -89.99583333333334})
    sampledict = GeoDict({'dx': 0.008333333333333333,
                          'dy': 0.008336693548387094,
                          'nx': 601,
                          'ny': 497,
                          'xmax': -116.046,
                          'xmin': -121.046,
                          'ymax': 36.2785,
                          'ymin': 32.1435})
    aligndict = popdict.getAligned(sampledict)
    assert popdict.isAligned(aligndict)
    
    print('Testing geodict intersects method...')
    gd1 = GeoDict({'xmin':0.5,'xmax':3.5,
                   'ymin':0.5,'ymax':3.5,
                   'dx':1.0,'dy':1.0,
                   'nx':4,'ny':4})

    print('Testing geodict intersects method...')
    gd2 = GeoDict({'xmin':2.5,'xmax':5.5,
                   'ymin':2.5,'ymax':5.5,
                   'dx':1.0,'dy':1.0,
                   'nx':4,'ny':4})
    gd3 = GeoDict({'xmin':4.5,'xmax':7.5,
                   'ymin':4.5,'ymax':7.5,
                   'dx':1.0,'dy':1.0,
                   'nx':4,'ny':4})
    gd4 = GeoDict({'xmin':1.5,'xmax':2.5,
                   'ymin':1.5,'ymax':2.5,
                   'dx':1.0,'dy':1.0,
                   'nx':2,'ny':2})
    assert gd1.intersects(gd2)
    assert not gd1.intersects(gd3)
    print('Passed intersects method...')

    print('Testing geodict intersects method with real geographic data...')
    gda = GeoDict({'ymax': 83.62083333333263, 'nx': 43201, 
                   'ny': 20835, 'dx': 0.00833333333333, 
                   'dy': 0.00833333333333, 'xmin': -179.99583333333334, 
                   'ymin': -89.99583333326461, 'xmax': -179.99583333347732})
    gdb = GeoDict({'ymax': 28.729166666619193, 'nx': 300, 
                   'ny': 264, 'dx': 0.00833333333333, 
                   'dy': 0.00833333333333, 'xmin': 84.08749999989436, 
                   'ymin': 26.537499999953404, 'xmax': 86.57916666656007})
    assert gda.intersects(gdb)
    print('Passed geodict intersects method with real geographic data.')

    print('Testing geodict doesNotContain method...')
    assert gd1.doesNotContain(gd3)
    assert not gd1.doesNotContain(gd4)
    
    print('Passed doesNotContain method...')

    print('Testing geodict contains method...')
    
    assert gd1.contains(gd4)
    assert not gd1.contains(gd3)
    print('Passed contains method...')

    # print('Testing to see if getIntersection() method works...')
    # gd5 = GeoDict({'xmin':0.5,'xmax':6.5,
    #                'ymin':0.5,'ymax':8.5,
    #                'dx':1.0,'dy':1.0,
    #                'nx':7,'ny':9})
    # gd6 = GeoDict({'xmin':3.0,'xmax':8.0,
    #                'ymin':5.0,'ymax':10.0,
    #                'dx':1.0,'dy':1.0,
    #                'nx':6,'ny':6})
    # print('Passed test of getIntersection() method')

def test_bounds_within_meridian():
    host = GeoDict({'xmin':-180,
                    'xmax':150,
                    'ymin':-90,
                    'ymax':90,
                    'dx':30,
                    'dy':45,
                    'nx':12,
                    'ny':5})
    sample = GeoDict({'xmin':75,
                       'xmax':-135,
                       'ymin':-67.5,
                       'ymax':67.5,
                       'dx':30,
                       'dy':45,
                       'nx':6,
                       'ny':4})

    result = GeoDict({'xmin':90,
                      'xmax':-150,
                      'ymin':-45,
                      'ymax':45,
                      'dx':30,
                      'dy':45,
                      'nx':5,
                      'ny':3})
    
    inside = host.getBoundsWithin(sample)
    assert inside == result

def test_intersection():
    fxmin,fxmax = (178.311, -179.189)
    fymin,fymax = (50.616, 52.176)
    fdx,fdy = (0.025, 0.02516129032258068)
    fnx,fny = (101, 63)
    host = GeoDict({'xmin':fxmin,
                    'xmax':fxmax,
                    'ymin':fymin,
                    'ymax':fymax,
                    'dx':fdx,
                    'dy':fdy,
                    'nx':fnx,
                    'ny':fny})
    sxmin,sxmax = (178.31249999999858, -179.19583333333335)
    symin,symax = (50.62083333333279, 52.17083333333278)
    sdx,sdy = (0.0083333333333333, 0.0083333333333333)
    snx,sny = (300, 187)
    sample = GeoDict({'xmin':sxmin,
                      'xmax':sxmax,
                      'ymin':symin,
                      'ymax':symax,
                      'dx':sdx,
                      'dy':sdy,
                      'nx':snx,
                      'ny':sny})
    #result = GeoDict()
    ixmin,ixmax = (178.31249999999858, -179.19583333333478)
    iymin,iymax = (50.62083333333278, 52.17083333333278)
    idx,idy = (0.0083333333333333, 0.0083333333333333)
    inx,iny = (300, 187)
    result = GeoDict({'xmin':ixmin,
                      'xmax':ixmax,
                      'ymin':iymin,
                      'ymax':iymax,
                      'dx':idx,
                      'dy':idy,
                      'nx':inx,
                      'ny':iny})
    intersection = host.getIntersection(sample)
    assert intersection == result
    
def test_bounds_within():
    host = GeoDict({'xmin':-180,
                    'xmax':150,
                    'ymin':-90,
                    'ymax':90,
                    'dx':30,
                    'dy':45,
                    'nx':12,
                    'ny':5})
    sample = GeoDict({'xmin':-75,
                       'xmax':45,
                       'ymin':-67.5,
                       'ymax':67.5,
                       'dx':30,
                       'dy':45,
                       'nx':5,
                       'ny':4})

    result = GeoDict({'xmin':-60,
                      'xmax':30,
                      'ymin':-45,
                      'ymax':45,
                      'dx':30,
                      'dy':45,
                      'nx':4,
                      'ny':3})
    
    inside = host.getBoundsWithin(sample)
    assert inside == result

def test_real():
    fxmin,fxmax,fymin,fymax = (-179.99583333333334, 179.99583333333192, -89.99583333333331, 83.99583333333266)
    fdx,fdy = (0.0083333333333333, 0.0083333333333333)
    fnx,fny = (43200, 20880)

    host = GeoDict({'xmin':fxmin,
                    'xmax':fxmax,
                    'ymin':fymin,
                    'ymax':fymax,
                    'dx':fdx,
                    'dy':fdy,
                    'nx':fnx,
                    'ny':fny})
    
    xmin,xmax,ymin,ymax = (178.311, -179.189, 50.616, 52.176)
    dx,dy = (0.025, 0.02516129032258068)
    nx,ny = (101, 63)

    sample = GeoDict({'xmin':xmin,
                      'xmax':xmax,
                      'ymin':ymin,
                      'ymax':ymax,
                      'dx':dx,
                      'dy':dy,
                      'nx':nx,
                      'ny':ny})
    # sample = GeoDict({'xmin':179.8967,
    #                   'xmax':-179.9283,
    #                   'ymin':30.0,
    #                   'ymax':31.0,
    #                   'dx':0.025,
    #                   'dy':1.0,
    #                   'nx':8,
    #                   'ny':2})

    inside = host.getBoundsWithin(sample)
    # assert inside == result
    
# def test2():
#     host = GeoDict({'xmin':-180,
#                     'xmax':120,
#                     'ymin':-60,
#                     'ymax':60,
#                     'dx':60,
#                     'dy':30,
#                     'nx':6,
#                     'ny':5})
#     sample = GeoDict({'xmin':30.0,
#                       'xmax':-90,
#                       'ymin':-52.5,
#                       'ymax':52.5,
#                       'dx':30,
#                       'dy':15,
#                       'nx':9,
#                       'ny':8})
#     result = GeoDict({'xmin':60,
#                       'xmax':-120,
#                       'ymin':-30,
#                       'ymax':30,
#                       'dx':60,
#                       'dy':30,
#                       'nx':4,
#                       'ny':3})
#     inside = host.getBoundsWithin(sample)
#     assert inside == result
    
if __name__ == '__main__':
    test_intersection()
    #test2()
    test_bounds_within()
    test_bounds_within_meridian()
    test()


        

        
