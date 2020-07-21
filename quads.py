"""
A pure Python Quadtree implementation.
"""
import math


__author__ = "Daniel Lindsley"
__license__ = "New BSD"
__version__ = (1, 0, 0, "beta")


def euclidean_compare(ref_point, check_point):
    dx = max(ref_point.x, check_point.x) - min(ref_point.x, check_point.x)
    dy = max(ref_point.y, check_point.y) - min(ref_point.y, check_point.y)
    return dx ** 2 + dy ** 2


def euclidean_distance(ref_point, check_point):
    return math.sqrt(euclidean_compare(ref_point, check_point))


class Point(object):
    def __init__(self, x, y, data=None):
        self.x = x
        self.y = y
        self.data = data

    def __repr__(self):
        return "<Point: ({}, {})>".format(self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class BoundingBox(object):
    def __init__(self, min_x, min_y, max_x, max_y):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    def __repr__(self):
        return "<BoundingBox: ({}, {}) to ({}, {})>".format(
            self.min_x, self.min_y, self.max_x, self.max_y
        )

    def contains(self, point):
        return (
            self.min_x <= point.x <= self.max_x
            and self.min_y <= point.y <= self.max_y
        )


class QuadNode(object):
    POINT_CAPACITY = 4

    def __init__(self, center, width, height, capacity=None):
        self.center = center
        self.width = width
        self.height = height
        self.points = []

        self.ul = None
        self.ur = None
        self.ll = None
        self.lr = None

        if capacity is None:
            capacity = self.POINT_CAPACITY

        self.capacity = capacity
        self.bounding_box = self._calc_bounding_box()

    def __repr__(self):
        return "<QuadNode: ({}, {}) {}x{}>".format(
            self.center.x, self.center.y, self.width, self.height
        )

    def __contains__(self, pnt):
        return self.find(pnt) is not None

    def _calc_bounding_box(self):
        half_width = self.width / 2
        half_height = self.height / 2

        min_x = self.center.x - half_width
        min_y = self.center.y - half_height
        max_x = self.center.x + half_width
        max_y = self.center.y + half_height

        return BoundingBox(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)

    def contains_point(self, pnt):
        bb = self.bounding_box

        if bb.min_x <= pnt.x < bb.max_x:
            if bb.min_y <= pnt.y < bb.max_y:
                return True

        return False

    def is_ul(self, point):
        return point.x <= self.center.x and point.y >= self.center.y

    def is_ur(self, point):
        return point.x > self.center.x and point.y >= self.center.y

    def is_ll(self, point):
        return point.x <= self.center.x and point.y < self.center.y

    def is_lr(self, point):
        return point.x > self.center.x and point.y < self.center.y

    def subdivide(self):
        half_width = self.width / 2
        half_height = self.height / 2
        quarter_width = half_width / 2
        quarter_height = half_height / 2

        ul_center = Point(
            self.center.x - quarter_width, self.center.y + quarter_height
        )
        self.ul = self.__class__(
            ul_center, half_width, half_height, capacity=self.capacity
        )

        ur_center = Point(
            self.center.x + quarter_width, self.center.y + quarter_height
        )
        self.ur = self.__class__(
            ur_center, half_width, half_height, capacity=self.capacity
        )

        ll_center = Point(
            self.center.x - quarter_width, self.center.y - quarter_height
        )
        self.ll = self.__class__(
            ll_center, half_width, half_height, capacity=self.capacity
        )

        lr_center = Point(
            self.center.x + quarter_width, self.center.y - quarter_height
        )
        self.lr = self.__class__(
            lr_center, half_width, half_height, capacity=self.capacity
        )

        # Redistribute the points.
        for pnt in self.points:
            if self.is_ul(pnt):
                self.ul.insert(pnt)
            elif self.is_ur(pnt):
                self.ur.insert(pnt)
            elif self.is_ll(pnt):
                self.ll.insert(pnt)
            else:
                self.lr.insert(pnt)

        self.points = []

    def insert(self, point):
        if not self.contains_point(point):
            raise ValueError(
                "Point {} is not within this node ({} - {}).".format(
                    point, self.center, self.bounding_box
                )
            )

        # Check to ensure we're not going to go over capacity.
        if (len(self.points) + 1) > self.capacity:
            # We're over capacity. Subdivide, then insert into the new child.
            self.subdivide()

        if self.ul is not None:
            if self.is_ul(point):
                return self.ul.insert(point)
            elif self.is_ur(point):
                return self.ur.insert(point)
            elif self.is_ll(point):
                return self.ll.insert(point)
            elif self.is_lr(point):
                return self.lr.insert(point)

        # There are no child nodes & we're under capacity. Add it to `points`.
        self.points.append(point)
        return True

    def find(self, point):
        found_node, _ = self.find_node(point)

        if found_node is None:
            return None

        # Try the points on this node first.
        for pnt in found_node.points:
            if pnt.x == point.x and pnt.y == point.y:
                return pnt

        return None

    def find_node(self, point, searched=None):
        if searched is None:
            searched = []

        if not self.contains_point(point):
            return None, searched

        searched.append(self)

        # Check the children.
        if self.is_ul(point):
            if self.ul is not None:
                return self.ul.find_node(point, searched)
        elif self.is_ur(point):
            if self.ur is not None:
                return self.ur.find_node(point, searched)
        elif self.is_ll(point):
            if self.ll is not None:
                return self.ll.find_node(point, searched)
        elif self.is_lr(point):
            if self.lr is not None:
                return self.lr.find_node(point, searched)

        # Not found in any children. Return this node.
        return self, searched

    def within_bb(self, bb):
        points = []

        # FIXME: This is inefficient, as it checks nodes that may not
        #        overlap with the bounding box.

        if self.ul is not None:
            points += self.ul.within_bb(bb)

        if self.ur is not None:
            points += self.ur.within_bb(bb)

        # Check if any of the points on this instance are within the BB.
        for pnt in self.points:
            if bb.contains(pnt):
                points.append(pnt)

        if self.ll is not None:
            points += self.ll.within_bb(bb)

        if self.lr is not None:
            points += self.lr.within_bb(bb)

        return points


class QuadTree(object):
    """
    Usage::

        >>> import quads
        >>> tree = quads.QuadTree(
        ...     (0, 0),  # The center point
        ...     10,  # The width
        ...     10,  # The height
        ... )

        >>> tree.insert((1, 2))
        True

        >>> tree.find((1, 2))
        Point(1, 2)

        >>> tree.find((4, -4))
        None
    """

    def __init__(self, center, width, height, capacity=None):
        self.width = width
        self.height = height
        self.center = self.convert_to_point(center)
        self._root = QuadNode(
            self.center, self.width, self.height, capacity=capacity
        )

    def __repr__(self):
        return "<QuadTree: ({}, {}) {}x{}>".format(
            self.center.x, self.center.y, self.width, self.height,
        )

    def convert_to_point(self, val):
        if isinstance(val, Point):
            return val
        elif isinstance(val, (tuple, list)):
            return Point(val[0], val[1])
        elif val is None:
            return Point(0, 0)
        else:
            raise ValueError(
                "Unknown data provided for point. Please use one of: "
                "quads.Point | tuple | list | None"
            )

    def __contains__(self, point):
        pnt = self.convert_to_point(point)
        return self.find(pnt) is not None

    def insert(self, point, data=None):
        pnt = self.convert_to_point(point)
        pnt.data = data
        return self._root.insert(pnt)

    def find(self, point):
        pnt = self.convert_to_point(point)
        return self._root.find(pnt)

    def within_bb(self, bb):
        return self._root.within_bb(bb)

    # FIXME: Finish this for 1.0.0!
    """
    def nearest_neighbors(self, point, num_results=10)
        pnt = self.convert_to_point(point)
    """
