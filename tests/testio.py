import os
import unittest
import typedbytes


class TestIO(unittest.TestCase):
    
    def testio(self):
        objects = [True, 1234, 12345L, 1.23, "trala",
                   (1,2,3), [1,2,3,4], {1:2,3:4}, set([1,2,3])]
        file = open("test.bin", "wb")
        output = typedbytes.Output(file)
        output.writes(objects)
        file.close()
        file = open("test.bin", "rb")
        input = typedbytes.Input(file)
        for (index, record) in enumerate(input):
            self.assertEqual(objects[index], record)
        file.close()
        os.remove("test.bin")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIO)
    unittest.TextTestRunner(verbosity=2).run(suite)
