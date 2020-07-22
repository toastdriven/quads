# `quads`

[![Documentation Status](https://readthedocs.org/projects/quads/badge/?version=latest)](https://quads.readthedocs.io/en/latest/?badge=latest)
![CI](https://github.com/toastdriven/quads/workflows/CI/badge.svg)

A pure Python Quadtree implementation.

[Quadtrees](https://en.wikipedia.org/wiki/Quadtree) are a useful data
structure for sparse datasets where the location/position of the data is
important. They're especially good for spatial indexing & image processing.

An actual visualization of a `quads.QuadTree`:

![quadtree_viz](docs/images/quadtree_visualization.png)


## Usage

Full documentation at https://quads.readthedocs.io/en/latest/

```python
>>> import quads
>>> tree = quads.QuadTree(
...     (0, 0),  # The center point
...     10,  # The width
...     10,  # The height
... )

# You can choose to simply represent points that exist.
>>> tree.insert((1, 2))
True
# ...or include extra data at those points.
>>> tree.insert(quads.Point(4, -3, data="Samus"))
True

# You can search for a given point. It returns the point if found...
>>> tree.find((1, 2))
Point(1, 2)

# Or `None` if there's no match.
>>> tree.find((4, -4))
None

# You can also find all the points within a given region.
>>> bb = quads.BoundingBox(min_x=-1, min_y=-2, max_x=2, max_y=2)
>>> tree.within_bb(bb)
[Point(1, 2)]

# You can also search to find the nearest neighbors of a point, even
# if that point doesn't have data within the quadtree.
>>> tree.nearest_neighbors((0, 1), count=2)
[
    Point(1, 2),
    Point(4, -4),
]

# And if you have `matplotlib` installed (not required!), you can visualize
# the tree.
>>> quads.visualize(tree)
```


## Installation

```
$ pip install quads
```


## Requirements

* Python 3.7+ (untested on older versions but may work)


## Running Tests

```
$ git clone https://github.com/toastdriven/quads.git
$ cd quads
$ poetry install
$ poetry shell

# Just the tests.
$ pytest .

# With coverage.
$ pytest -s --cov=quads .
# And with pretty reports.
$ pytest -s --cov=quads . && coverage html
```


## License

New BSD
