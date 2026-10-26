import numpy as np
from typing import Union
import numbers

class Vector2D:
    """
    Class that represents a two-dimensional vector.
    """

    def __init__(self, x: int, y: int):
        """
        Initialize the Vector2D object.

        Parameters:
        -----------
        x : int
            The x-coordinate of the vector.
        y : int
            The y-coordinate of the vector.

        Returns:
        --------
        None
        """
        self._x = x
        self._y = y

    @property
    def x(self):
        """
        Get the x-coordinate of the vector.

        Parameters:
        -----------
        None

        Returns:
        --------
        float
            The x-coordinate of the vector.
        """
        return float(self._x)

    @property
    def y(self):
        """
        Get the y-coordinate of the vector.

        Parameters:
        -----------
        None

        Returns:
        --------
        float
            The y-coordinate of the vector.
        """
        return float(self._y)

    @x.setter
    def x(self, value: numbers.Real):
        """
        Set the x-coordinate of the vector.

        Parameters:
        -----------
        value : numbers.Real
            The new x-coordinate. Must be a real number.

        Returns:
        --------
        None

        Raises:
        -------
        ValueError
            If value is not a real number.
        """
        if isinstance(value, numbers.Real):
            self._x = value
        else:
            raise ValueError(f"value={value} must be a real")

    @y.setter
    def y(self, value: numbers.Real):
        """
        Set the y-coordinate of the vector.

        Parameters:
        -----------
        value : numbers.Real
            The new y-coordinate. Must be a real number.

        Returns:
        --------
        None

        Raises:
        -------
        ValueError
            If value is not a real number.
        """
        if isinstance(value, numbers.Real):
            self._y = value
        else:
            raise ValueError(f"value='{value}' must be a real")

    def __repr__(self):
        """
        Return the official string representation of the vector.

        Parameters:
        -----------
        None

        Returns:
        --------
        str
            A string containing the x- and y-coordinates.
        """
        return f"{self._x},{self._y}"

    def __str__(self):
        """
        Return a human-readable string representation of the vector.

        Parameters:
        -----------
        None

        Returns:
        --------
        str
            A formatted string describing the vector.
        """
        return f"Vector2D: x = {self._x}, y = {self._y}"

    def __eq__(self, other: "Vector2D"):
        """
        Compare two vectors for equality.

        Parameters:
        -----------
        other : Vector2D
            The vector to compare with the current vector.

        Returns:
        --------
        bool
            True if both vectors have identical coordinates,
            False otherwise.
        """
        return self._x == other._x and self._y == other._y

    def __add__(self, other: Union[list[int], "Vector2D"]):
        """
        Add another vector or a list of coordinates to the vector.

        Parameters:
        -----------
        other : list[int] or Vector2D
            The vector or list of two coordinates to add.

        Returns:
        --------
        Vector2D
            A new vector containing the sum of the coordinates.
        """
        if isinstance(other, list):
            return Vector2D(self._x + other[0], self._y + other[1])
        else:
            return Vector2D(self._x + other._x, self._y + other._y)

    def __sub__(self, other: Union[list[int], "Vector2D"]):
        """
        Subtract another vector or a list of coordinates.

        Parameters:
        -----------
        other : list[int] or Vector2D
            The vector or list of two coordinates to subtract
            from the current vector.

        Returns:
        --------
        Vector2D
            A new vector containing the difference of the coordinates.
        """
        if isinstance(other, list):
            return Vector2D(self._x - other[0], self._y - other[1])
        else:
            return Vector2D(self._x - other._x, self._y - other._y)

    def __mul__(self, other: Union[list[int], "Vector2D", numbers.Real]):
        """
        Multiply the vector by another vector, a list of coordinates,
        or a real number.

        Parameters:
        -----------
        other : list[int], Vector2D or numbers.Real
            The operand used for multiplication. A real number scales
            both coordinates; a vector or list multiplies the
            corresponding coordinates element-wise.

        Returns:
        --------
        Vector2D
            A new vector containing the resulting coordinates.
        """
        if isinstance(other, list):
            return Vector2D(self._x * other[0], self._y * other[1])
        elif isinstance(other, numbers.Real):
            return Vector2D(self._x * other, self._y * other)
        else:
            return Vector2D(self._x * other._x, self._y * other._y)

    def __iadd__(self, other: Union[list[int], "Vector2D"]):
        """
        Implement the in-place addition operator +=.

        Parameters:
        -----------
        other : list[int] or Vector2D
            The vector or list of coordinates to add.

        Returns:
        --------
        Vector2D
            A new vector containing the sum of the coordinates.
        """
        return self.__add__(other)

    def __abs__(self):
        """
        Compute the Euclidean norm of the vector.

        Parameters:
        -----------
        None

        Returns:
        --------
        float
            The magnitude of the vector, calculated as
            sqrt(x**2 + y**2).
        """
        return np.sqrt(self._x**2 + self._y**2)

    def __radd__(self, other: Union[list[int], "Vector2D"]):
        """
        Implement reflected addition when the vector is the
        right-hand operand of the + operator.

        Parameters:
        -----------
        other : list[int] or Vector2D
            The left-hand operand.

        Returns:
        --------
        Vector2D
            A new vector containing the sum of the coordinates.
        """
        return self.__add__(other)

    def __rsub__(self, other: Union[list[int], "Vector2D"]):
        """
        Implement reflected subtraction when the vector is the
        right-hand operand of the - operator.

        Parameters:
        -----------
        other : list[int] or Vector2D
            The left-hand operand.

        Returns:
        --------
        Vector2D
            A new vector containing the coordinate differences
            as calculated by the current implementation.
        """
        if isinstance(other, list):
            return Vector2D(-self._x + other[0], -self._y + other[1])
        else:
            return Vector2D(-self._x + other._x, -self._y + other._y)

    def __neg__(self):
        """
        Return the additive inverse of the vector.

        Parameters:
        -----------
        None

        Returns:
        --------
        Vector2D
            A new vector with both coordinates negated.
        """
        return Vector2D(-self._x, -self._y)
