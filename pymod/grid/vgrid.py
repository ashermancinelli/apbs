from point import Point
from vtypes import *
from typing import List, Optional
import numpy as np
import math

import sys
sys.path.insert('..')

'''

Likely never used. Ported for no reason...

'''

class CurvatureFlag:
    ReducedMaximalCurvature = 0
    MeanCurvature = 1
    GaussCurvature = 2
    TrueMaximalCurvature = 3


class Grid:
    '''
    Pulled over from src/mg/vgrid.(h|c)

    Attributes:
        dims       : Number of grid points in a given direction. Previously nx, ny, nz.
        spaces     : Grid spacing in a given direction. Previously hx, hy, hz.
        mins       : Minimums in a given direction. Previously xmin, ymin, zmin.
        maxs       : Maximums in a given direction. Previously xmax, ymax, zmax.
        data       : nx*ny*nz array of data 
    '''

    eps = 1e-6

    def __init__(self, dims, spaces, mins, maxs, data: Optional[FloatVec]):
        '''Grid constructor

        Parameters
            dims:   Initializes member variable with the same name.
            spaces: Initializes member variable with the same name.
            mins:   Initializes member variable with the same name.
            maxs:   Initializes member variable with the same name.
            data:   Optionally sets the data for the grid (may leave None if will be set later)
        '''
        self.dims:   Point[int] = dims
        self.spaces: Point[int] = spaces
        self.mins:   Point[int] = mins
        self.maxs:   Point[int] = maxs
        self.data:   Optional[FloatVec] = data

    def value(self, pt: Point[float]) -> float:
        '''Get potential value (from mesh or approximation) at a point

        :note: Previously returned by pointer, using return code as an error code.
                This has been replaced by returning the value and raising an
                exception on error.

        :param   x    : Point at which to evaluate potential
        :returns      : value of grid
        '''

        if self.data is None:
            raise RuntimeError("No data available.")

        ret_value = float(0)

        tmp = Point(
            (pt.x - mins.x)/spaces.x,
            (pt.y - mins.y)/spaces.y,
            (pt.z - mins.z)/spaces.z,
        )

        hi = Point(
            int(math.ceil(tmp.x))
            int(math.ceil(tmp.y))
            int(math.ceil(tmp.z))
        )
        lo = Point(
            int(math.floor(tmp.x))
            int(math.floor(tmp.y))
            int(math.floor(tmp.z))
        )

        hi.x = dims.x-1 if abs(pt.x - maxs.x) < eps else hi.x
        hi.y = dims.y-1 if abs(pt.y - maxs.y) < eps else hi.y
        hi.z = dims.z-1 if abs(pt.z - maxs.z) < eps else hi.z

        lo.x = 0 if abs(pt.x - mins.x) < eps else lo.x
        lo.y = 0 if abs(pt.y - mins.y) < eps else lo.y
        lo.z = 0 if abs(pt.z - mins.z) < eps else lo.z

        if hi < dims:
            dx, dy, dz = tmp.x - lo.x, tmp.y - lo.y, tmp.z - lo.z
            ret_value = list()
            ret_value[0] = float(dx * dy * dz * self.data[hi.x, hi.y, hi.z])
            ret_value[1] = float(dx * (1.0-dy)*dz *
                                 self.data[hi.x, lo.y, hi.z])
            ret_value[2] = float(dx * dy * (1.0-dz) *
                                 self.data[hi.x, hi.y, lo.z])
            ret_value[3] = float(dx * (1.0-dy)*(1.0-dz) *
                                 self.data[hi.x, lo.y, lo.z])
            ret_value[4] = float((1.0-dx)*dy * dz *
                                 self.data[lo.x, hi.y, hi.z])
            ret_value[5] = float((1.0-dx)*(1.0-dy)*dz *
                                 self.data[lo.x, lo.y, hi.z])
            ret_value[6] = float((1.0-dx)*dy * (1.0-dz) *
                                 self.data[lo.x, hi.y, lo.z])
            ret_value[7] = float((1.0-dx)*(1.0-dy)*(1.0-dz)
                                 * self.data[lo.x, lo.y, lo.z])

            ret_value = sum(ret_value)

            if ret_value == math.nan:
                # TODO: Add a more descriptive error
                raise RuntimeError('Value routine failed to converge with the following coordinates:\n'
                                   f'\tLow: {lo}\n'
                                   f'\tHigh: {hi}\n'
                                   f'\tPoint: {pt}\n')

        return ret_value

    def curvature(self, pt: Point[float], cflag: CurvatureFlag):
        '''Get second derivative values at a point

        :param   pt   : Location to evaluate second derivative
        :param   cflag: Curvature method
        :param   curv : Specified curvature value
        :returns      : 1 if successful, 0 if off grid
        '''
        ...

    def gradient(self, pt: Point[float], grad: FloatVec):
        '''Get first derivative values at a point

        :param   pt  : Location to evaluate gradient
        :param   grad: Gradient
        :returns     : 1 if successful, 0 if off grid
        '''
        ...

    def integrate(self) -> float:
        '''Get the integral of the data
        '''
        ...

    def norml1(self) -> float:
        '''Get the \f$L_1\f$ norm of the data.  This returns the integral:
            \f[ \| u \|_{L_1} = \int_\Omega | u(x) | dx  \f]
        '''
        ...

    def norml2(self) -> float:
        '''Computes the \f$L_2\f$ norm of the data.
        '''
        ...

    def normlInf(self) -> float:
        '''Computes the \f$L_\infty\f$ norm of the data.
        '''
        ...

    def seminormH1(self) -> float:
        '''Get the \f$H_1\f$ semi-norm of the data.
        This returns the integral:
          \f[ | u |_{H_1} = \left( \int_\Omega |\nabla u(x)|^2 dx \right)^{1/2} \f]
        '''

    def normH1(self) -> float:
        '''Integral of data
        Get the \f$H_1\f$ norm (or energy norm) of the data.
        This returns the integral:
          \f[ \| u \|_{H_1} = \left( \int_\Omega |\nabla u(x)|^2 dx
                            +        \int_\Omega |u(x)|^2 dx \right)^{1/2} \f]
        '''

    def read_dx(self, fn: str) -> None:
        lines = open(fn, 'r').readlines()
        self.data = list()
        for l in lines:
            l = l.lower().strip()

            # skip comments
            if l[0] == '#':
                continue
            l = l.split(' ')

            # TODO: figure out what all these options mean
            if l[0] in ('object', 'attribute', 'component'):
                continue

            assert len(
                l) == 3, 'Found an unknown option or found line with values != 3'

            self.data.append([
                float(l[0]),
                float(l[1]),
                float(l[2]),
            ])
