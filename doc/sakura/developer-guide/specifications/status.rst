.. _dev-spec-event:

Event Status specification
==========================


Possible statuses
-----------------

* 0 - Off
* 1 - On going
* 2 - Stealthy
* 3 - Flapping
* 4 - canceled


*Off*
~~~~~

An Event is considered ``Off`` if it is stable (i.e *Criticity* stable at ``0``).

*On going*
~~~~~~~~~~

An Event is considered ``On going`` if its *Criticity* is in an alert state (> 0).

*Stealthy*
~~~~~~~~~~

An Event is considered ``Stealthy`` if its *Criticity* changed from alert to stable in a specified amount of time.
If the said Event has its *Criticity* changed again within the specified time, it is still considered ``Stealthy``.
An Event will stay ``Stealthy`` for a specified time (See *stealthy_show_time*) and will then be ``Off`` if the last state was 0, ``On Going`` if it was an alert, or ``Flapping`` if it qualifies as such.

*Flapping*
~~~~~~~~~~

An Event is considered ``Flapping`` if it has been changing from an alert state to a stable state a specific number of times on a specified period of time. (See *flapping_freq* and *flapping_time*)


*Canceled*
~~~~~~~~~~

An Event is considered ``canceled`` if the user flagged it as such from the Ux.
An Event flagged as ``canceled`` will change state if it goes from an alert state to a stable state.
Additionally, the user can specify if it should change state if its criticity changes within the various alert state or only between alert and stable states.


Workflow
--------

.. image:: ../../_static/images/dev_engines/state_flowchart.png

Additional informations
-----------------------

* ``Restore event`` : Boolean, equals ``True`` if the user wants an ``cancel`` event to change state when its criticity changes withing the various alert state, ``False`` if it changes only between alert and stable stated.
* ``alert`` : An alert is an event in an alert state (i.e. with a *Criticity* greater than 0).


Configuration
-------------

A `statusmanagement` crecord is needed for the configuration of the time intervals and frequencies, it has the following structure :


.. code-block:: json

   {
      "type": "object",
      "properties": {
         "crecord_type": {
            "enum": ["statusmanagement"],
            "required": true
         },
         "restore_event": {
            "type": "boolean",
            "required": true,
            "default": true
         },
         "flapping_time": {
            "type": "number",
            "required": true
         },
         "flapping_show": {
            "type": "number",
            "required": true
         },
         "stealthy_time": {
            "type": "number",
            "required": true
         },
         "stealthy_show": {
            "type": "number",
            "required": true
         }
      }
   }
