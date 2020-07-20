import unittest

from quads import Point, BoundingBox, QuadNode, QuadTree


class QuadNodeTestCase(unittest.TestCase):
    def test_init(self):
        node = QuadNode(Point(0, 0), 10, 10)
        self.assertEqual(node.center.x, 0)
        self.assertEqual(node.center.y, 0)
        self.assertEqual(node.width, 10)
        self.assertEqual(node.height, 10)
        self.assertEqual(len(node.points), 0)

        self.assertIsNone(node.ul)
        self.assertIsNone(node.ur)
        self.assertIsNone(node.ll)
        self.assertIsNone(node.lr)

    def test_calc_bounding_box_basic(self):
        node = QuadNode(Point(0, 0), 10, 10)
        self.assertEqual(node.bounding_box.min_x, -5)
        self.assertEqual(node.bounding_box.min_y, -5)
        self.assertEqual(node.bounding_box.max_x, 5)
        self.assertEqual(node.bounding_box.max_y, 5)

    def test_calc_bounding_box_moderate(self):
        node = QuadNode(Point(13, 17), 50, 60)
        self.assertEqual(node.bounding_box.min_x, -12)
        self.assertEqual(node.bounding_box.min_y, -13)
        self.assertEqual(node.bounding_box.max_x, 38)
        self.assertEqual(node.bounding_box.max_y, 47)

    def test_is_ul(self):
        node = QuadNode(Point(1, 2), 10, 10)

        yes = Point(0, 3)
        self.assertTrue(node.is_ul(yes))

        no = Point(2, 4)
        self.assertFalse(node.is_ul(no))

        also_yes = Point(0, 2)
        self.assertTrue(node.is_ul(also_yes))

    def test_is_ur(self):
        node = QuadNode(Point(1, 2), 10, 10)

        yes = Point(3, 3)
        self.assertTrue(node.is_ur(yes))

        no = Point(0, 1)
        self.assertFalse(node.is_ur(no))

        also_yes = Point(3, 2)
        self.assertTrue(node.is_ur(also_yes))

    def test_is_ll(self):
        node = QuadNode(Point(1, 2), 10, 10)

        yes = Point(-1, 1)
        self.assertTrue(node.is_ll(yes))

        no = Point(2, 4)
        self.assertFalse(node.is_ll(no))

        also_no = Point(0, 2)
        self.assertFalse(node.is_ll(also_no))

    def test_is_lr(self):
        node = QuadNode(Point(1, 2), 10, 10)

        yes = Point(3, -1)
        self.assertTrue(node.is_lr(yes))

        no = Point(2, 4)
        self.assertFalse(node.is_lr(no))

        also_no = Point(2, 2)
        self.assertFalse(node.is_lr(also_no))

    def test_contains_point(self):
        node = QuadNode(Point(1, 2), 10, 10)

        yes = Point(3, -1)
        self.assertTrue(node.contains_point(yes))

        also_yes = Point(-3.9, -2.9)
        self.assertTrue(node.contains_point(also_yes))

        no = Point(12, 14)
        self.assertFalse(node.contains_point(no))

        also_no = Point(-5, 2)
        self.assertFalse(node.contains_point(also_no))

    def test_subdivide(self):
        node = QuadNode(Point(0, 0), 20, 20)
        node.points = [
            Point(1, 2),
            Point(-3, -3),
            Point(-9, 6),
            Point(7, 2),
        ]

        # Sanity check.
        self.assertIsNone(node.ul)
        self.assertIsNone(node.ur)
        self.assertIsNone(node.ll)
        self.assertIsNone(node.lr)

        node.subdivide()

        # There should now be child nodes.
        self.assertIsNotNone(node.ul)
        self.assertIsNotNone(node.ur)
        self.assertIsNotNone(node.ll)
        self.assertIsNotNone(node.lr)

        # Check the points.
        self.assertEqual(len(node.points), 0)
        self.assertEqual(len(node.ul.points), 1)
        self.assertEqual(len(node.ur.points), 2)
        self.assertEqual(len(node.ll.points), 1)

        pairs = [(pnt.x, pnt.y) for pnt in node.ur.points]
        self.assertEqual(pairs, [(1, 2), (7, 2)])

    def test_insert(self):
        node = QuadNode(Point(0, 0), 20, 20)
        node.insert(Point(7, 5))
        node.insert(Point(6, 4))
        node.insert(Point(-1, -2))
        node.insert(Point(9, -9))

        # No subdivision yet.
        self.assertEqual(len(node.points), 4)
        self.assertIsNone(node.ul)
        self.assertIsNone(node.ur)
        self.assertIsNone(node.ll)
        self.assertIsNone(node.lr)

        # Over the edge, automatically subdivide before the insert happens.
        node.insert(Point(8, 8))
        self.assertEqual(len(node.points), 0)
        self.assertIsNotNone(node.ul)
        self.assertEqual(len(node.ul.points), 0)
        self.assertIsNotNone(node.ur)
        self.assertEqual(len(node.ur.points), 3)
        self.assertIsNotNone(node.ll)
        self.assertEqual(len(node.ll.points), 1)
        self.assertIsNotNone(node.lr)
        self.assertEqual(len(node.lr.points), 1)

    def create_simple_tree(self):
        node = QuadNode(Point(0, 0), 20, 20)
        node.insert(Point(7, 5, data="dog"))
        node.insert(Point(6, 4, data="cat"))
        node.insert(Point(-1, -2, data=True))
        node.insert(Point(9, -9, data={"hello": "world"}))
        node.insert(Point(8, 8, data=("a", "b", "c")))
        node.insert(Point(-3, 2, data=False))
        return node

    def test_find(self):
        node = self.create_simple_tree()
        res = node.find(Point(7, 5))
        self.assertIsNotNone(res)
        self.assertEqual(res.x, 7)
        self.assertEqual(res.y, 5)
        self.assertEqual(res.data, "dog")

        res = node.find(Point(6, 4))
        self.assertIsNotNone(res)
        self.assertEqual(res.x, 6)
        self.assertEqual(res.y, 4)
        self.assertEqual(res.data, "cat")

        res = node.find(Point(-1, -2))
        self.assertIsNotNone(res)
        self.assertEqual(res.x, -1)
        self.assertEqual(res.y, -2)
        self.assertEqual(res.data, True)

        res = node.find(Point(9, -9))
        self.assertIsNotNone(res)
        self.assertEqual(res.x, 9)
        self.assertEqual(res.y, -9)

        self.assertEqual(res.data, {"hello": "world"})

        # And a miss.
        res = node.find(Point(2.5, 2.5))
        self.assertIsNone(res)

        # And outside the bounds.
        res = node.find(Point(250, 350))
        self.assertIsNone(res)

    def test_within_bb(self):
        node = self.create_simple_tree()
        bb = BoundingBox(-7, -7, 7, 7)

        points = node.within_bb(bb)
        pairs = [(pnt.x, pnt.y) for pnt in points]
        self.assertEqual(pairs, [(-3, 2), (7, 5), (6, 4), (-1, -2)])

    def test_within_bb_narrow(self):
        node = self.create_simple_tree()
        bb = BoundingBox(-3, -3, 3, 4)

        points = node.within_bb(bb)
        pairs = [(pnt.x, pnt.y) for pnt in points]
        self.assertEqual(pairs, [(-3, 2), (-1, -2)])


class QuadTreeTestCase(unittest.TestCase):
    def test_init(self):
        tree = QuadTree((0, 0), 10, 10)
        self.assertEqual(tree.width, 10)
        self.assertEqual(tree.height, 10)
        self.assertEqual(tree.center, Point(0, 0))

    def test_convert_to_point_already_a_point(self):
        tree = QuadTree((0, 0), 10, 10)
        pt = Point(1, 2)
        converted = tree.convert_to_point(pt)
        self.assertEqual(converted.x, pt.x)
        self.assertEqual(converted.y, pt.y)

    def test_convert_to_point_tuple(self):
        tree = QuadTree((0, 0), 10, 10)
        converted = tree.convert_to_point((5, 6))
        self.assertEqual(converted.x, 5)
        self.assertEqual(converted.y, 6)

    def test_convert_to_point_none(self):
        tree = QuadTree((0, 0), 10, 10)
        converted = tree.convert_to_point(None)
        self.assertEqual(converted.x, 0)
        self.assertEqual(converted.y, 0)

    def test_convert_to_point_nope(self):
        tree = QuadTree((0, 0), 10, 10)

        with self.assertRaises(ValueError):
            tree.convert_to_point("Samus")

    def test_insert(self):
        tree = QuadTree((0, 0), 20, 20)
        self.assertTrue(tree.insert((1, 2)))
        self.assertTrue(tree.insert((7, 5)))
        self.assertTrue(tree.insert((6, 4)))
        self.assertTrue(tree.insert((-1, -2)))
        self.assertTrue(tree.insert((9, -9)))

    def create_sample_tree(self):
        tree = QuadTree((0, 0), 100, 100)

        # Insert a wide variety of points & data values.
        tree.insert((1, 2), data=True)
        tree.insert((7, 5), data="dog")
        tree.insert((6, 4), data="cat")
        tree.insert((-1, -2), data=False)
        tree.insert((10, -22), data=35)
        tree.insert((10, -22.5), data=["a", "b"])
        tree.insert((9, -17), data=89.567)
        tree.insert((10, 35), data="fish")
        tree.insert((11, 42), data="Samus")
        tree.insert((-15, 17), data={"hello": "world"})
        tree.insert((-15, 9), data="whatev")
        tree.insert((-13, 6), data=-69)

        return tree

    def test_find(self):
        tree = self.create_sample_tree()

        res = tree.find((1, 2))
        self.assertIsNotNone(res)
        self.assertEqual(res.data, True)

        res = tree.find((-1, -2))
        self.assertIsNotNone(res)
        self.assertEqual(res.data, False)

        res = tree.find((11, 42))
        self.assertIsNotNone(res)
        self.assertEqual(res.data, "Samus")

        res = tree.find((-15, 17))
        self.assertIsNotNone(res)
        self.assertEqual(res.data, {"hello": "world"})

        # And a miss.
        res = tree.find((-50, 45))
        self.assertIsNone(res)

    def test_within_bb(self):
        tree = self.create_sample_tree()
        bb = BoundingBox(-20, -20, 20, 20)

        points = tree.within_bb(bb)
        pairs = [(pnt.x, pnt.y) for pnt in points]
        self.assertEqual(
            pairs,
            [
                (-15, 17),
                (-15, 9),
                (-13, 6),
                (1, 2),
                (7, 5),
                (6, 4),
                (-1, -2),
                (9, -17),
            ],
        )

    @unittest.skip
    def test_nearest_neighbors(self):
        pass
