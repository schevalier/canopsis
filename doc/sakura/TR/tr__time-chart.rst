.. _TR__Title:

==========
Time chart
==========

The timechart widget in canopsis UI allow display of metric values over time.

.. contents::
   :depth: 4

References
==========


- :ref:`FR::Time-chart <fr__time-chart>`
- :ref:`ED::Time-chart <ed__time-chart>`

Updates
=======


.. csv-table::
   :header: "Author(s)", "Date", "Version", "Summary", "Accepted by"

   "Eric Régnier", "2015/10/22", "1.0", "Template creation", ""

Contents
========

.. _TR__Time-chart:

Software architecture
>>>>>>>>>>>>>>>>>>>>>

The timechart widget is made within canopsis UI and depends on D3 js and C3 js for chart purpopses.

There are 3 main axes of developpement for this feature that are the follwing:

* Widget architecture in canopsis UI
* Data fetch (metric, events log, pbehaviors)
* Logic implementation

For each feature explained below, the developement process may concern on of the 3 points above.

As the category chart, the time chart will be made of a core widget that manage data logic and fetching and a c3 component that will handle data and represent them as a complex chart using many features of c3js and d3js.

Costing
>>>>>>>

.. csv-table::
   :header: "Feature", "Cost day/man"

   "Simple chart from series or metrics", "3"
   "Human readables values", "0.5"
   "Timewindow", "1"
   "Zoom", "0.25"
   "History view", "1"
   "Show events log", "3"
   "Stacked charts", "0.5"
   "Multiple axes X-Y", "0.5"
   "Customizable labels", "1"
   "Display downtime", "3"
   "Tooltip et shared tooltip", "0.5"
   "Threshold", "1"
   "Timewindow offset", "1"
   "Baseline", "5"
   "Display mode", "0.5"
   "Dot representation", "?"
   "Display associated pbehaviors", "3"
   "Trend lines", "5"

The zoom function does not seems to work on the current c3js release. however, we can expect that it will be fixed soon and it is still possible to zoom with the history view at the moment.

The dot representation is not supported yet in C3js. however, some experimental feature (plugins) may be included to solve this issue. It is also possible to work directly for c3 js project in order to make a valuid pull request for a proper implementation of this feature.

Functional tests
>>>>>>>>>>>>>>>>

Functional tests consists in using all options explained in the functional requirements and make them do what they are supposed to do. These features have to work together independently, and one whole testing of the time chart should cost about half an hour.

Performance
>>>>>>>>>>>

As the timechart is able technically to fetch all data for a metric in a past and fetch unlimited metric count, performance may quickly decrease in the UI if the widget is used in the edge cases.

However, It can be expected that the widget behave properly with a timewindow of many months for metric, events log and pebehavior (with filters on events log).

Another limitation is the fact that a view can contain many widget of the same type. That's why a time chart used in the edge cases and duplicated many times on a single view may quickly be performance killer.

