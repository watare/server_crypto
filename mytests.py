import unittest
import numpy as np
from walldetection import *

class MyFirstTests(unittest.TestCase):
    data = dataquisition("data_poloniex.json")

    def test_dataAquisition(self):
        self.assertEqual(set(['value','bidsvolume']).issubset(self.data[0].columns),True)
        self.assertEqual(set(['value','asksvolume']).issubset(self.data[1].columns),True)

    def test_calculVolumeGlobal(self):
        data_volume = calculVolumeGlobal (self.data[0],self.data[1])

        self.assertEqual(type(data_volume[0]) == np.float64 ,True)
        self.assertEqual(type(data_volume[1]) == np.float64 ,True)

    def test_tendance(self):
        data_volume = calculVolumeGlobal (self.data[0],self.data[1])
        _tendance = tendance (data_volume[0],data_volume[1])

        self.assertEqual(_tendance in [1,2,3],True)

    def test_filtreWall(self):
        pass

    def test_placement_ordre(self):
        #aquisition des donnees
        [dfb,dfa] = dataquisition("data_poloniex.json")
        #ajout des wall
        [atotal,btotal] = calculVolumeGlobal(dfb,dfa)

        _tendance = tendance(bidstotal,askstotal,50,50)

        [atotal,btotal] = calculVolumeGlobal(dfb,dfa)
        for _tendance in [1,2,3]:
            self.assertEqual( type(placement_ordre(_tendance,dfb,dfa)[1]) == float,True)

if __name__ == '__main__':
    unittest.main()
