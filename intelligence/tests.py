import unittest

import numpy as np

from intelligence.optimize import seller_optimizer


class TestOptimizer(unittest.TestCase):
    def test_seller_optimizer(self):
        """ Tests the optimizer for a seller bot """

        # Example1:
        # unit price      [1000, 500, 200, 100]
        # owner           [40000, 0, 0, 0]
        # ex_rates        [1, 2, 5, 10]
        # caps are big enough
        # result should be: (10, [0, 5000, 2000, 1000])
        owner = np.asarray([40000, 0, 0, 0])
        unit_price = np.asarray([1000, 500, 200, 100])
        ex_rate = np.asarray([1, 2, 5, 10])
        market_cap = np.asarray([0, 10000, 10000, 10000])
        capacity_cap = 20

        result = seller_optimizer(owner, unit_price, ex_rate, capacity_cap, market_cap)

        self.assertEqual(result[0], 10)
        self.assertEqual(list(result[1]), [0, 5000, 2000, 1000])

        # Example2:
        # changed the capacity_cap    6
        # result should be: (6, [0, 3000, 1200, 600])
        capacity_cap = 6

        result = seller_optimizer(owner, unit_price, ex_rate, capacity_cap, market_cap)

        self.assertEqual(result[0], 6)
        self.assertEqual(list(result[1]), [0, 3000, 1200, 600])

        # Example3:
        # changed the market_cap to limited energy [0, 2000, 10000, 10000]
        # result should be: (4, [0, 2000, 800, 400])
        market_cap = np.asarray([0, 2000, 10000, 10000])

        result = seller_optimizer(owner, unit_price, ex_rate, capacity_cap, market_cap)

        self.assertEqual(result[0], 4)
        self.assertEqual(list(result[1]), [0, 2000, 800, 400])

        # Example4:
        # changed the market_cap to limited energy [0, 2123, 10000, 10000]
        # buy everything of limited resource
        # result should be: (4, [0, 2123, 800, 400])
        market_cap = np.asarray([0, 2123, 10000, 10000])

        result = seller_optimizer(owner, unit_price, ex_rate, capacity_cap, market_cap)

        self.assertEqual(result[0], 4)
        self.assertEqual(list(result[1]), [0, 2123, 800, 400])

        # Example5:
        # changed the market_cap to limited energy [0, 450, 10000, 10000]
        # buy everything of limited resource
        # result should be: (0, [0, 450, 800, 400])
        market_cap = np.asarray([0, 450, 10000, 10000])

        result = seller_optimizer(owner, unit_price, ex_rate, capacity_cap, market_cap)

        self.assertEqual(result[0], 0)
        self.assertEqual(list(result[1]), [0, 450, 0, 0])

        # Example6:
        # unit doesnt require all resources anymore
        # reset other values to example1
        owner = np.asarray([40000, 0, 0, 0])
        unit_price = np.asarray([1000, 500, 0, 100])
        ex_rate = np.asarray([1, 2, 5, 10])
        market_cap = np.asarray([0, 10000, 10000, 10000])
        capacity_cap = 100

        result = seller_optimizer(owner, unit_price, ex_rate, capacity_cap, market_cap)

        self.assertEqual(result[0], 13)
        self.assertEqual(list(result[1]), [0, 6500, 0, 1300])

        # Example7:
        # owner has some left over resources not required by the unit
        owner = np.asarray([40000, 0, 1337, 0])

        result = seller_optimizer(owner, unit_price, ex_rate, capacity_cap, market_cap)

        self.assertEqual(result[0], 13)
        self.assertEqual(list(result[1]), [0, 6500, 0, 1300])

        # Example8:
        # owner has some left over resources required by the unit
        # thus only one resource needs to be bought [0, 0, 0, 3000]
        owner = np.asarray([60000, 20000, 0, 0])

        result = seller_optimizer(owner, unit_price, ex_rate, capacity_cap, market_cap)

        self.assertEqual(result[0], 30)
        self.assertEqual(list(result[1]), [0, 0, 0, 3000])

        # Example9:
        # owner has some left over resources required by the unit
        # thus only one resource needs to be bought [0, 0, 0, 3000]
        owner = np.asarray([60000, 2314, 0, 6543])

        result = seller_optimizer(owner, unit_price, ex_rate, capacity_cap, market_cap)

        self.assertEqual(result[0], 24)
        self.assertEqual(list(result[1]), [0, 10000, 0, 0])

        # Example9:
        # trivial example
        result = seller_optimizer(owner, unit_price, ex_rate, 0, market_cap)
        self.assertEqual(result[0], 0)
        self.assertEqual(list(result[1]), [0, 0, 0, 0])

        # Example10:
        # trivial example
        owner = np.asarray([60000, 0, 0, 6543])
        market_cap = np.asarray([0, 450, 10000, 10000])

        result = seller_optimizer(owner, unit_price, ex_rate, capacity_cap, market_cap)

        self.assertEqual(result[0], 0)
        self.assertEqual(list(result[1]), [0, 450, 0, 0])

        # Example11:
        # real prices / exchange rates
        ex_rate = np.asarray([1, 1.1, 6.8, 16.0])
        unit_price = np.asarray([0, 700, 240, 96])
        market_cap = np.asarray([0, ])

        owner = np.asarray([0, 1874, 74, 48133])

        result = seller_optimizer()


if __name__ == '__main__':
    unittest.main()