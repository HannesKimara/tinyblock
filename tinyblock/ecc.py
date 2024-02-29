from __future__ import annotations # For PEP 563 – Postponed Evaluation of Annotations
from dataclasses import dataclass
from typing import Callable, TypeVar,Union


__all__ = ['FieldElement', 'Point', 'Curve'] 


class FieldElement:
    def __init__(self, num: int, order: int):
        if num >= order or num < 0:
            raise ValueError(f'{num} not in range 0 to {order}')
        self.num = num
        self.order = order

    def __eq__(self, other: FieldElement):
        self.__assert_type(other)
        
        return self.num == other.num and self.order == other.order

    def __ne__(self, other: FieldElement):
        self.__assert_type(other)

        return not self == other

    def __add__(self, other: FieldElement):
        self.__assert_type(other)
        self.__assert_symmetry(other)

        return self.__class__((self.num + other.num) % self.order, self.order)

    def __sub__(self, other: FieldElement):
        self.__assert_type(other)
        self.__assert_symmetry(other)

        return self.__class__((self.num - other.num) % self.order, self.order)

    def __mul__(self, other: FieldElement):
        self.__assert_type(other)
        self.__assert_symmetry(other)
        
        return self.__class__((self.num * other.num) % self.order, self.order)

    def __pow__(self, exponent):
        n = exponent % (self.order - 1)
        num = pow(self.num, n, self.order)
        return self.__class__(num=num, order=self.order)

    def __truediv__(self, other: FieldElement):
        self.__assert_type(other)
        self.__assert_symmetry(other)

        num = (self.num * pow(other.num, self.order - 2, self.order)) % self.order

        return self.__class__(num, self.order)

    def __rmul__(self, coefficient: int): 
        num = (self.num * coefficient) % self.order
        return self.__class__(num, self.order)

    def __assert_type(self, other: FieldElement):
        if not isinstance(other, self.__class__):
            raise TypeError(f'{other} must be of type {self.__class__}')

    def __assert_symmetry(self, other: FieldElement):
        if self.order != other.order:
            raise ValueError(f'FieldElements must have the same order, {self.order} != {other.order}')

    def __repr__(self):
        return f'FieldElement(val={self.num}, order={self.order})'


@dataclass(frozen=True)
class Curve:
    """
    An elliptic curve of the form y**2 = x**3 + a*x + b
    """
    a: FieldElement
    b: FieldElement
    p: int # Modulo

    def __post_init__(self):
        # check for singular curves
        if (4 * self.a.num**3 + 27 * self.b.num**3) == 0:
            raise ValueError(f'Values a={self.a}, b={self.b} yield singular curve')

    def __call__(self, x: Union[int, FieldElement]) -> Union[int, FieldElement]:
        return x**3 + self.a * x + self.b


@dataclass(frozen=True)
class Point:
    x: FieldElement
    y: FieldElement
    curve: Curve

    def __post_init__(self):
        if self.x is None and self.y is None:
            return

        if self.y ** 2 != self.curve(self.x):
            raise ValueError(f'({self.x}, {self.y}(!={self.curve(self.x)}) is not in the curve {self.curve})')
    
    def __add__(self, other: Point):
        if self.curve != other.curve:
            raise TypeError(f'Points ({self}, {other}) are not on the same curve')

        # Check for Infinite points
        if self.x is None:
            return other

        if other.x is None:
            return self

        if self.x == other.x and self.y != other.y:
            return self.__class__(None, None, self.curve)

        if self.x != other.x:
            s = (other.y - self.y) / (other.x - self.x)
            x = s**2 - self.x - other.x
            y = s * (self.x - x) - self.y
            return self.__class__(x, y, self.curve)

        if self == other and self.y == 0 * self.x:
            return self.__class__(None, None, self.curve)

        # Compute addition
        # s = (other.y - self.y)/(other.x - self.x)
        # x3 = s**2 - self.x  - other.x
        # y3 = s * (self.x - x3) - self.y

        # return self.__class__(x3, y3, self.curve)

        if self == other:
            s = (3 * self.x**2 + self.curve.a) / (2 * self.y)
            x = s**2 - 2 * self.x
            y = s * (self.x - x) - self.y
            return self.__class__(x, y, self.curve)

    def __rmul__(self, coeff: int):
        coef = coeff
        curr = self
        result = self.__class__(None, None, self.curve)
        while coef:
            if coef & 1:
                result += curr
            curr += curr
            coef >>= 1

        return result
