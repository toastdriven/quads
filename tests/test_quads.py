import unittest

from quads import (
    euclidean_compare,
    euclidean_distance,
    Point,
    BoundingBox,
    QuadNode,
    QuadTree,
)

from . import test_data


class UtilsTestCase(unittest.TestCase):
    def test_euclidean_compare(self):
        comp = euclidean_compare(Point(0, 0), Point(4, 5))
        self.assertEqual(comp, 41)

        comp = euclidean_compare(Point(-13, 7), Point(-3, -5))
        self.assertEqual(comp, 244)

    def test_euclidean_distance(self):
        dist = euclidean_distance(Point(0, 0), Point(4, 5))
        self.assertAlmostEqual(dist, 6.4031242374328485)

        dist = euclidean_distance(Point(-13, 7), Point(-3, -5))
        self.assertEqual(dist, 15.620499351813308)


class PointTestCase(unittest.TestCase):
    def test_init(self):
        # Mostly for API stability.
        pnt = Point(1, -23)
        self.assertEqual(pnt.x, 1)
        self.assertEqual(pnt.y, -23)
        self.assertEqual(pnt.data, None)

        # Samus the Corgi: https://www.instagram.com/p/CCcGNnMpmt9/
        pnt = Point(72, 13, data="Samus")
        self.assertEqual(pnt.x, 72)
        self.assertEqual(pnt.y, 13)
        self.assertEqual(pnt.data, "Samus")

    def test_str(self):
        pnt = Point(72, 13, data="Samus")
        self.assertEqual(str(pnt), "<Point: (72, 13)>")

    def test_hash(self):
        pnt_1 = Point(1, -23)
        pnt_2 = Point(1, -23, data="test")
        pnt_3 = Point(72, 13)

        self.assertEqual(hash(pnt_1), hash(pnt_2))
        self.assertNotEqual(hash(pnt_2), hash(pnt_3))

    def test_equality(self):
        pnt_1 = Point(1, -23)
        pnt_2 = Point(1, -23, data="test")
        pnt_3 = Point(72, 13)

        self.assertTrue(pnt_1 == pnt_2)
        self.assertFalse(pnt_1 == pnt_3)


class BoundingBoxTestCase(unittest.TestCase):
    def test_init(self):
        # Mostly for API stability.
        bb = BoundingBox(-10, -13, 10, 20)
        self.assertEqual(bb.min_x, -10)
        self.assertEqual(bb.min_y, -13)
        self.assertEqual(bb.max_x, 10)
        self.assertEqual(bb.max_y, 20)

        self.assertEqual(bb.width, 20)
        self.assertEqual(bb.height, 33)
        self.assertEqual(bb.center, Point(10, 16.5))

    def test_str(self):
        bb = BoundingBox(-10, -13, 10, 20)
        self.assertEqual(str(bb), "<BoundingBox: (-10, -13) to (10, 20)>")

    def test_contains(self):
        bb = BoundingBox(-10, -13, 10, 20)

        pnt_1 = Point(1, -13)
        pnt_2 = Point(72, 13, data="test")
        pnt_3 = Point(-5, -5)

        self.assertTrue(bb.contains(pnt_1))
        self.assertFalse(bb.contains(pnt_2))
        self.assertTrue(bb.contains(pnt_3))

    def test_intersects(self):
        bb_1 = BoundingBox(-10, -13, 10, 20)
        bb_2 = BoundingBox(0, 0, 30, 40)
        bb_3 = BoundingBox(-20, -30, 0, 0)

        # Partial overlap.
        self.assertTrue(bb_1.intersects(bb_2))
        self.assertTrue(bb_2.intersects(bb_1))

        self.assertTrue(bb_1.intersects(bb_3))
        self.assertTrue(bb_3.intersects(bb_1))

        # Containing box.
        bb_4 = BoundingBox(-10.0, -10.0, 10.0, 10.0)
        bb_5 = BoundingBox(-7, -7, 7, 7)
        self.assertTrue(bb_4.intersects(bb_5))
        self.assertTrue(bb_5.intersects(bb_4))

        # Non-intersecting.
        bb_6 = BoundingBox(-7, -7, -6, -6)
        bb_7 = BoundingBox(-5, -5, -4, -4)
        self.assertFalse(bb_6.intersects(bb_7))
        self.assertFalse(bb_7.intersects(bb_6))


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

    def test_str(self):
        node = QuadNode(Point(0, 0), 10, 10)
        self.assertEqual(str(node), "<QuadNode: (0, 0) 10x10>")

    def test_dunder_contains(self):
        node = QuadNode(Point(0, 0), 10, 10)
        node.points = [
            Point(1, 2),
            Point(-3, -1),
        ]
        self.assertTrue(Point(1, 2) in node)
        self.assertFalse(Point(2, 3) in node)

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

    def test_insert_fail(self):
        node = QuadNode(Point(0, 0), 20, 20)

        with self.assertRaises(ValueError):
            node.insert(Point(17, 55))

    def test_insert_ll(self):
        # Without this, a lower-left insert fails to be seen on coverage,
        # which is weird. Ensure that happens & things look right.
        node = QuadNode(Point(0, 0), 20, 20)
        node.ul = QuadNode(Point(-5, 5), 10, 10)
        node.ur = QuadNode(Point(5, 5), 10, 10)
        node.ll = QuadNode(Point(-5, -5), 10, 10)
        node.lr = QuadNode(Point(5, -5), 10, 10)
        node.insert(Point(-7, -5))
        self.assertTrue(Point(-7, -5) in node)
        self.assertTrue(Point(-7, -5) in node.ll)

    def create_simple_tree(self):
        node = QuadNode(Point(0, 0), 20, 20)
        node.insert(Point(7, 5, data="dog"))
        node.insert(Point(6, 4, data="cat"))
        node.insert(Point(-1, -2, data=True))
        node.insert(Point(9, -9, data={"hello": "world"}))
        node.insert(Point(8, 8, data=("a", "b", "c")))
        node.insert(Point(-3, 2, data=False))
        return node

    def create_medium_tree(self):
        node = QuadNode(Point(0, 0), 100, 100)

        node.insert(Point(1, 2, data=True))
        node.insert(Point(7, 5, data="dog"))
        node.insert(Point(6, 4, data="cat"))
        node.insert(Point(-1, -2, data=False))
        node.insert(Point(10, -22, data=35))
        node.insert(Point(10, -22.5, data=["a", "b"]))
        node.insert(Point(9, -17, data=89.567))
        node.insert(Point(10, 35, data="fish"))
        node.insert(Point(11, 42, data="Samus"))
        node.insert(Point(-15, 17, data={"hello": "world"}))
        node.insert(Point(-15, 9, data="whatev"))
        node.insert(Point(-13, 6, data=-69))

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

    def test_find_node(self):
        node = self.create_medium_tree()

        found, searched = node.find_node(Point(1, 2))
        self.assertIsNotNone(found)
        self.assertEqual(found.center, Point(12.5, 12.5))
        self.assertEqual(len(searched), 3)

        found, searched = node.find_node(Point(-1, -2))
        self.assertIsNotNone(found)
        self.assertEqual(found.center, Point(-25, -25))
        self.assertEqual(len(searched), 2)

        found, searched = node.find_node(Point(11, 42))
        self.assertIsNotNone(found)
        self.assertEqual(found.center, Point(12.5, 37.5))
        self.assertEqual(len(searched), 3)

        found, searched = node.find_node(Point(-15, 17))
        self.assertIsNotNone(found)
        self.assertEqual(found.center, Point(-25, 25))
        self.assertEqual(len(searched), 2)

        # And a miss.
        found, searched = node.find_node(Point(-500, 450))
        self.assertIsNone(found)

    def test_all_points_small(self):
        node = self.create_medium_tree()

        found, searched = node.find_node(Point(6, 4))
        points = found.all_points()
        self.assertEqual(
            set([pnt.data for pnt in points]), set([True, "dog", "cat"])
        )

    def test_all_points_large(self):
        node = self.create_medium_tree()

        points = node.all_points()
        sp = sorted([(pnt.x, pnt.y) for pnt in points])
        self.assertEqual(
            sp,
            [
                (-15, 9),
                (-15, 17),
                (-13, 6),
                (-1, -2),
                (1, 2),
                (6, 4),
                (7, 5),
                (9, -17),
                (10, -22.5),
                (10, -22),
                (10, 35),
                (11, 42),
            ],
        )

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

    def test_len(self):
        node = self.create_simple_tree()
        self.assertEqual(len(node), 6)

        node = self.create_medium_tree()
        self.assertEqual(len(node), 12)


class QuadTreeTestCase(unittest.TestCase):
    def test_init(self):
        tree = QuadTree((0, 0), 10, 10)
        self.assertEqual(tree.width, 10)
        self.assertEqual(tree.height, 10)
        self.assertEqual(tree.center, Point(0, 0))

    def test_str(self):
        tree = QuadTree((0, 0), 10, 10)
        self.assertEqual(str(tree), "<QuadTree: (0, 0) 10x10>")

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

    def test_dunder_contains(self):
        tree = QuadTree((0, 0), 20, 20)
        tree.insert((1, 2))
        tree.insert((7, 5))
        tree.insert((6, 4))

        self.assertTrue(Point(1, 2) in tree)
        self.assertTrue(Point(6, 4) in tree)
        self.assertFalse(Point(2, 3) in tree)

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

    def test_nearest_neighbors_tiny(self):
        tree = QuadTree((0, 0), 20, 20)

        tree.insert((1, 2), data="oof")
        tree.insert((-7, 5), data="we")
        tree.insert((-1, -2), data="are")
        tree.insert((3, -6), data="small")

        lr_pnt = Point(9, -9)
        nearby = tree.nearest_neighbors(lr_pnt, count=10)
        self.assertEqual(len(nearby), 4)
        self.assertEqual(
            [(pnt.x, pnt.y) for pnt in nearby],
            [(3, -6), (-1, -2), (1, 2), (-7, 5)],
        )
        self.assertEqual(
            [pnt.data for pnt in nearby], ["small", "are", "oof", "we"],
        )

        distances = [euclidean_distance(lr_pnt, found) for found in nearby]
        self.assertAlmostEqual(distances[0], 6.708203932499369)
        self.assertAlmostEqual(distances[-1], 21.2602916254693)

    def test_nearest_neighbors_sample(self):
        tree = self.create_sample_tree()

        ur_pnt = Point(5, 5)
        nearby = tree.nearest_neighbors(ur_pnt, count=10)
        self.assertEqual(len(nearby), 10)
        self.assertEqual(
            [(pnt.x, pnt.y) for pnt in nearby],
            [
                (6, 4),
                (7, 5),
                (1, 2),
                (10, 35),
                (11, 42),
                (-1, -2),
                (-13, 6),
                (-15, 9),
                (9, -17),
                (-15, 17),
            ],
        )
        self.assertEqual(
            [pnt.data for pnt in nearby],
            [
                "cat",
                "dog",
                True,
                "fish",
                "Samus",
                False,
                -69,
                "whatev",
                89.567,
                {"hello": "world"},
            ],
        )

        distances = [euclidean_distance(ur_pnt, found) for found in nearby]
        self.assertAlmostEqual(distances[0], 1.4142135623730951)
        self.assertAlmostEqual(distances[-1], 23.323807579381203)

    def test_nearest_neighbors_large(self):
        # Load up a "big" quadtree.
        tree = QuadTree((0, 0), 100, 100)

        for x, y in test_data.data.get("large_random", []):
            tree.insert((x, y))

        ul_pnt = Point(-35, 25)
        nearby = tree.nearest_neighbors(ul_pnt, count=10)
        self.assertEqual(len(nearby), 10)
        self.assertEqual(
            [(pnt.x, pnt.y) for pnt in nearby],
            [
                (-33, 22),
                (-36, 29),
                (-34, 21),
                (-38, 28),
                (-40, 25),
                (-35, 30),
                (-40, 26),
                (-30, 26),
                (-33, 30),
                (-31, 29),
            ],
        )

        distances = [euclidean_distance(ul_pnt, found) for found in nearby]
        self.assertAlmostEqual(distances[0], 3.605551275463989)
        self.assertAlmostEqual(distances[-1], 5.656854249492381)

    def test_nearest_neighbors_outside(self):
        tree = QuadTree((0, 0), 20, 20)

        tree.insert((1, 2), data="oof")
        tree.insert((-7, 5), data="we")
        tree.insert((-1, -2), data="are")
        tree.insert((3, -6), data="small")

        ur_pnt = Point(21, 21)
        nearby = tree.nearest_neighbors(ur_pnt, count=10)
        self.assertEqual(len(nearby), 0)

    def test_len(self):
        tree = self.create_sample_tree()
        self.assertEqual(len(tree), 12)

        # Load up a "big" quadtree.
        tree = QuadTree((0, 0), 100, 100)

        for x, y in test_data.data.get("large_random", []):
            tree.insert((x, y))

        self.assertEqual(len(tree), 1000)
