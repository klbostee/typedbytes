import cStringIO
import unittest
import time
import typedbytes
from itertools import imap


class TestSpeed(unittest.TestCase):

    def teststrings(self):
        file = cStringIO.StringIO()

        output = typedbytes.Output(file)
        t = time.time()
        output.writes(imap(str, xrange(100000)))
        print time.time() - t

        file.seek(0)

        input = typedbytes.Input(file)
        t = time.time()
        for record in input:
            pass
        print time.time() -t

        file.close()


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSpeed)
    unittest.TextTestRunner(verbosity=2).run(suite)
