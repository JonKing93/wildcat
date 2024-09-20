wildcat export
==============

.. highlight:: bash


Synopsis
--------

**wildcat export** [project] [options]


Description
-----------
Exports hazard assessment results to :ref:`GIS file formats <vector-formats>`. Includes options to select, order, and rename exported properies. Please see the :doc:`Property Guide </guide/properties>` and :doc:`Export Overview </commands/export>` for more details. 

.. note:: 
    
    The options presented on this page will override any associated settings in ``configuration.py``.


Options
-------

.. program:: export

Folders
+++++++
Folders in which to search for input files and save exported results.

.. option:: project

    The project folder in which to export results. If not provided, interprets the current folder as the project folder. If the project folder contains a ``configuration.py`` file, then the config file will be used to configure the export.

    Examples::

        # Export results
        wildcat export my-project

        # Export project in current folder
        wildcat export


.. option:: -i PATH, --assessment PATH

    The folder in which to search for saved assessment results.

    Example::

        # Export results in a different assessment folder
        wildcat export --assessment my-other-assessment

    *Overrides setting:* :confval:`assessment`


.. option:: -o PATH, --exports PATH

    The folder in which to save exported results.

    Example::

        # Save exports to a specific subfolder
        wildcat export --exports my-other-exports

    *Overrides setting:* :confval:`exports`


Output Files
++++++++++++
Options affecting the names and formats of the exported files.

.. option:: --format FORMAT

    The GIS file format of the exported files. The :ref:`Vector Format Guide <vector-formats>` lists the supported format options in the first column. Format names are case-insensitive.

    Example::

        # Export results to Shapefile
        wildcat export --format Shapefile

    *Overrides setting:* :confval:`format`


.. option:: --prefix PREFIX

    Prepends the indicated string to the beginning of exported file names. The string must only contain ASCII letters, numbers, hyphens ``-``, and underscores ``_``.

    Example::

        # Add "fire-id" to the beginning of file names
        wildcat export --prefix fire-id

    *Overrides setting:* :confval:`prefix`


.. option:: --suffix SUFFIX

    Appends the indicated string to the end of exported file names. The string must only contain ASCII letters, numbers, hyphens ``-``, and underscores ``_``.

    Example::

        # Add "YYYY-MM-DD" to the end of file names
        wildcat export --suffix YYYY-MM-DD

    *Overrides setting:* :confval:`suffix`


Properties
++++++++++
Options that :ref:`select exported properties <select-props>`.

.. option:: --properties PROPERTY...

    Properties that should be included in the exported files. May include property names, result prefixes, and/or property groups.

    Examples::

        # Export several properties
        wildcat export --properties Segment_ID Area_km2 BurnRatio

        # Export volumes and CIs using prefixes
        wildcat export --properties V Vmin Vmax

        # Export property groups
        wildcat export --properties watershed results

    *Overrides setting:* :confval:`properties`


.. option:: --exclude-properties

    Properties that should be removed from the base property list. May include property names, result prefixes, and/or property groups.

    Example::

        # Export watershed variables, except for Segment_ID
        wildcat export --properties watershed --exclude-properties Segment_ID

    *Overrides setting:* :confval:`exclude_properties`


.. option:: --include-properties

    Properties that should be added to the property list, after excluded properties have been removed. May include property names, result prefixes, and property groups.

    Example::

        # Export default fields, but exclude watershed variables (except for Segment_ID)
        wildcat export --exclude-properties watershed --include-properties Segment_ID

    *Overrides setting:* :confval:`include_properties`


Property Order
++++++++++++++

.. option:: --no-order-properties

    Do not :ref:`reorder <reorder>` exported properties. Properties will be exported in the order they are listed in.

    *Overrides setting:* :confval:`order_properties`


Renaming
++++++++
Settings used to :ref:`rename <rename>` the exported properties.

.. option:: --no-clean-names

    Do not rename result properties. Exported result properties will retain the index naming scheme.

    *Overrides setting:* :confval:`clean_names`


.. option:: --rename FROM TO

    Rename an exported property or prefix. Can be used multiple times to rename multiple properties/prefixes.

    .. tip::

        It's usually easier to use ``configuration.py`` to rename properties. Please see the :ref:`Renaming Guide <rename>` for more details.

    Examples::

        # Rename "Segment_ID" to "SID"
        wildcat export --rename Segment_ID SID

        # Rename the "H" prefix to "hazard"
        wildcat export --rename H hazard

        # Rename a specific result field
        wildcat export --rename H_0 Hazard_Legend

        # Rename multiple properties
        wildcat export --rename Segment_ID SID --rename Area_km2 catchment-size

    *Overrides setting:* :confval:`rename`


.. option:: --rename-parameter PARAMETER RENAME...

    Rename the values associated with a hazard modeling parameter. The PARAMETER input should be the name of the parameter whose values are being renamed. This should be followed by one name per modeled parameter. May be used multiple times to rename multiple modeling parameters.

    .. tip::

        It's usually easier to use ``configuration.py`` to rename properties. Please see the :ref:`Renaming Guide <rename>` for more details.

    Examples:

    .. code:: python

        # Given the following values in configuration.py
        I15_mm_hr = [16, 20, 24]
        probabilities = [0.5, 0.75]

    ::

        # Rename a parameter
        wildcat export --rename-parameter probabilities p50 p75

        # Rename multiple parameters
        wildcat export --rename-parameter I15_mm_hr 16mm_hr 20mmh_hr 24mm_hr --rename-parameter probabilities p50 p75


Logging
+++++++

.. option:: -q, --quiet

    Does not print progress messages to the console. Warnings and errors will still be printed.

.. option:: -v, --verbose

    Print detailed progress messages to the console. Useful for debugging.

.. option:: --log PATH

    Prints a `DEBUG level`_ log record to the indicated file. If the file does not exists, creates the file. If the file already exists, appends the log record to the end.

    Example::

        wildcat assess --log my-log.txt

.. _DEBUG level: https://docs.python.org/3/library/logging.html#logging.DEBUG


Traceback
+++++++++

.. option:: -t, --traceback

    Prints the full error traceback to the console when an error occurs (useful for debugging). If this option is not provided, then only the final error message is printed. 
