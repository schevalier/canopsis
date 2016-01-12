.. _FR__Selector:

================================
Alarm aggregation with Selectors
================================

This document describes the alarm aggregation process, named Selector.

.. contents::
   :depth: 3

References
==========

List of referenced functional requirements:

 - :ref:`FR::Context <FR__Context>`
 - :ref:`FR::Event <FR__Event>`
 - :ref:`FR::Alarm <FR__Alarm>`

Updates
=======

.. csv-table::
   :header: "Author(s)", "Date", "Version", "Summary", "Accepted by"

   "David Delassus", "2016/01/12", "0.1", "Document creation", ""

Contents
========

.. _FR__Selector__Desc:

Description
-----------

A selector is an object used to aggregate :ref:`entities <FR__Context__Entity>` state:

 * the aggregated state is produced as a :ref:`selector event <FR__Event__Selector>` ;
 * entities state is retrieved via their associated :ref:`alarms <FR__Alarm__Desc>` ;
 * aggregation method is specified amongst the following algorithms:
    * worst state ;
    * best state ;
    * ``a`` if ``condition`` else ``b``, with ``condition`` being one of those algorithms:
       * at least ``x`` in state ``y`` ;
       * no more than ``x`` in state ``y`` ;
       * all in state ``x`` ;
       * none in state ``x``.
