.. _overview:

Overview
==========

.. toctree::
   :maxdepth: 2
   :titlesonly:

.. image:: https://git.canopsis.net/canopsis/canopsis/raw/develop/doc/sakura/_static/images/overview/logo.png 
	:width: 60%

What is Canopsis ? 
------------------

`Canopsis <http://canopsis.org>`_ is an open-source `hypervisor <http://www.capensis.fr/solutions/hypervision/>`_ whose goal is to aggregate/consolidate information and events metrics of different types such as performance, availability, etc.) coming from multiple sources to create a global solution for monitoring and administrating resources.

Built to last on top of `proven Open Source technologies by and for all IT professionals <http://www.capensis.fr/solutions/supervision/>`_ . It is an event based architecture and it is modular by design. Plug your infrastructure tools like Syslog, `Nagios <https://git.canopsis.net/canopsis-connectors/connector-neb2canopsis>`_, `Shinken <https://git.canopsis.net/canopsis-connectors/connector-shinken2canopsis>`_, `others <https://git.canopsis.net/canopsis-connectors>`_ to `Canopsis <http://canopsis.org>`_ and you're ready to go.

How to try ?
------------

You can try Canopsis on demo platform:

* Master branch (stable): http://sakura.canopsis.org
* Devel branch (unstable): coming soon

How to install ?
----------------

* Easy way (on `Debian 6 & ulterior`, `CentOS 6`, `Ubuntu 12.04 & ulterior` 64Bits) : `Install from sources <https://git.canopsis.net/canopsis/canopsis/blob/master/doc/sakura/administrator-guide/setup/install-from-sources.rst>`_

* Coming soon : With Ansible playbooks


How to connect ?
----------------

Now you are ready to deal with Canopsis.

You can connect your `Nagios` (or `Icinga`, or any other Nagios like): `connector-neb2canopsis <https://git.canopsis.net/canopsis-connectors/connector-neb2canopsis>`_

Or your `Shinken <https://github.com/naparuba/shinken>`_ : `connector-shinken2canopsis <https://git.canopsis.net/canopsis-connectors/connector-shinken2canopsis>`_

Or any other source from : `Others <https://git.canopsis.net/canopsis-connectors>`_

How to use ?
------------

See `Canopsis doc section <http://www.canopsis.org/learn>`_ or `directly <https://git.canopsis.net/canopsis/canopsis/tree/master/doc/sakura>`_

Links
-----

* Doc: https://canopsis.org/learn
* Community: http://www.canopsis.org
* Forum (french) : http://forums.monitoring-fr.org/index.php?board=127.0
