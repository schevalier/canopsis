state of the art

CRUD

.. csv-table::
    :header: technology, feeding (< 1MB), feeding (>= 1MB), asynchronous feeding, retrieving (< 1 MB), retrieving (>= 1 MB), asynchronous retrieving, deleting

    graphite, API python, textual file, AMQP, API python, /, /, API python

Operators

.. csv-table::
    :header: technology, mean, delta, min, max, sum, count, derivative, integral, diff, divide, group, identity, invert, last, logarithm, product, percentile, offset, pow, scale, forecasting, retention

    graphite, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok

Benchmarks

.. csv-table::
   :header: technology, feeding (< 1MB), feeding (>= 1MB), asynchronous feeding, retrieving (< 1 MB), retrieving (>= 1 MB), asynchronous retrieving, deleting, mean, forecasting, retention

   graphite
