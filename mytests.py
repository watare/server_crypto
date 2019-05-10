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
        toto = tendance (data_volume[0],data_volume[1])
        self.assertEqual(toto[0] ^ toto[1] ^ toto[2],True)

    def test_filtreWall(self):
        

if __name__ == '__main__':
    unittest.main()
