.. _TR__Categorychart:

==============
Category chart
==============



The category chart is a Canopsis widget made of a widget core and a display component. The widget core manage underlaying widget data and the `c3 js <http://c3js.org>`_ display component uses data to render the widget depending on user configuration.

.. contents::
   :depth: 3

References
==========


- :ref:`FR::Categorychart <FR__Categorychart>`
- :ref:`TR::Categorychart <TR__Categorychart>`

Updates
=======

.. csv-table::
   :header: "Author(s)", "Date", "Version", "Summary", "Accepted by"

   "Eric Régnier", "2015/10/02", "1.0", "Use template", ""

Contents
========

.. _TR__Title__Categorychart:


Software architecture
>>>>>>>>>>>>>>>>>>>>>

The category chart is a Canopsis widget. It is build respecting the Canopsis widget api for widget and data management. It is also based upon the C3js library for chart display.

Technical guide
>>>>>>>>>>>>>>>


widget core
-----------

The category chart core is made of a controller and a template. The template only instanciate the render component.

It also fetch metrics depending on user configuration. The user can select series or metrics to display from the configuration form. The core also prepare widget configuration that will affect the component representation. Data fetch is performed asynchronously and when all identified tasks are complete (configuration, metric and series fetch), then only the widget rendering is performed for performances issues.

The data fetching is mainly based on the metric controller that provider high level methods for metric querying. These method are called with a callback that is one of the widget method doing the job of preparing data for the display component.

display component
-----------------

At the moment, the category chart uses **c3 js** as chart library to compute an interactive chart display.

When data from widget core are ready, then the rendering starts, and prepared data are integrated to the chart instanciation options.

The chart lifecycle depends on the widget lifecycle as c3js chart instance is a property of the canopsis component. It can be destroyed and then instanciated on widget refresh. It can also be recomputed when the user dynamicaly changes the chart display type.

User options make vary the chart generation by only changing the option dictionnary that is used on c3js chart instanciation. Available options are functionnaly described in the `user guide <../../../user-guide/UI/widgets/categorychart.html>`_ section. Most of them are well explained through the c3 js documentation as in the chart option computed values are explicitely labelled with c3 js conventions.

One important custom feature is the series dynamic naming depending on context informations. On metric fetch, the context Id associated to the metric is parsed and then used as a Handlebars template context that the administrator user is able to manipulate thanks to the templating system. Context information availables are **connector, connector_name, component, resource and metric**.


Automated tests
>>>>>>>>>>>>>>>

Automated tests for the category chart have to be written as soon as possible when the unit test for Canopsis frontend is ready to use.

Functional test
>>>>>>>>>>>>>>>

Testing the category chart consists in try to put a category chart on a widget and fill in the form to tell how the category chart have to display from a datasource that may be either metrics or series.

Optional features for the category chart have to be tested by **following the user guide documentation** and making the widget behave and produce expected result depending on what user guide describe and how the widget behave in a live Canopsis UI.

For example for the category chart, filling the **metric template** option field once filled with an appropriate handlebar template have to display metric legend properly depending on the template content.

