# `quads`

A pure Python Quadtree implementation.

[Quadtrees](https://en.wikipedia.org/wiki/Quadtree) are a useful data
structure for sparse datasets where the location/position of the data is
important. They're especially good for spatial indexing & image processing.


## Usage

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
```


## Setup

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

# Just the tests.
$ pytest .

# With coverage.
$ pytest -s --cov=quads .
# And with pretty reports.
$ pytest -s --cov=quads . && coverage html
```


## License

New BSD
