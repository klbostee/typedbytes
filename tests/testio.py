import os
import unittest
import decimal
import datetime
import typedbytes


class TestIO(unittest.TestCase):

    objects = [True, 1234, 3000000000, 12345L, 1.23, "trala", u'trala',
                (1,2,3), [1,2,3,4], {1:2,3:4}, set([1,2,3]),
                decimal.Decimal("123.456"), datetime.datetime.now(),
                typedbytes.Bytes("abc123\x01")]

    def testio(self):
        objects = TestIO.objects
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

    def testpairio(self):
        objects = TestIO.objects
        file = open("test.bin", "wb")
        output = typedbytes.PairedOutput(file)
        output.writes(enumerate(objects))
        file.close()
        file = open("test.bin", "rb")
        input = typedbytes.PairedInput(file)
        for index, record in input:
            self.assertEqual(objects[index], record)
        file.close()
        os.remove("test.bin")

    def testpickle(self):
        file = open("test.bin", "wb")
        output = typedbytes.Output(file)
        output.write("123")
        output.write(MyClass())
        file.close()
        file = open("test.bin", "rb")
        input = typedbytes.Input(file)
        self.assertEqual("123", input.read())
        self.assertEqual(234, input.read().attr)
        file.close()
        os.remove("test.bin")


class MyClass:
    attr = 234


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIO)
    unittest.TextTestRunner(verbosity=2).run(suite)
