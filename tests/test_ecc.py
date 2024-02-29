from unittest import TestCase

from tinyblock.ecc import FieldElement, Curve, Point

class ECCTest(TestCase):
    def test_point_add(self):
        order = 223
        a = FieldElement(0, order)
        b = FieldElement(7, order)

        x1 = FieldElement(192, order)
        y1 = FieldElement(105, order)

        x2 = FieldElement(17, order)
        y2 = FieldElement(56, order)

        btc_curve = Curve(a, b, 1)
        p1 = Point(x1, y1, btc_curve)
        p2 = Point(x2, y2, btc_curve)

        expect = Point(FieldElement(170, order), FieldElement(142, order), btc_curve)

        self.assertEqual(p1 + p2, expect)
