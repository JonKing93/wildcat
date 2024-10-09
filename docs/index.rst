wildcat
=======

Wildcat is a software tool to assess and map post-wildfire debris-flow hazards. It provides routines to:

* Preprocess input datasets,
* Design stream segment networks
* Estimate debris-flow hazards and rainfall thresholds, and
* Export results to common GIS formats (such as Shapefiles and GeoJSON)

Wildcat can be run from the command line, or within a Python session. The package is intended for users who are interested in conducting and communicating hazard assessments. By default, wildcat implements assessments in the USGS style, but users can also configure the tool to run with modified settings.

.. tip::

    Wildcat is designed to implement a USGS hazard assessment framework. If you want to modify wildcat routines or develop new assessment frameworks, you may be interested in the `pfdf library <https://ghsc.code-pages.usgs.gov/lhp/pfdf/>`_ instead.


Installation
------------
.. admonition:: Prerequisites

    Wildcat requires `Python 3.11+ <https://www.python.org/downloads/>`_.

You can install wildcat using::

    pip install wildcat -i https://code.usgs.gov/api/v4/groups/859/-/packages/pypi/simple

and see the :doc:`installation page <install>` for additional options. 

The URL in the install command instructs `pip <https://pip.pypa.io/en/stable/>`_ to install wildcat from the official USGS package registry. This ensures that you are installing an official USGS product, and not a similarly named package from a third party. The ``859`` in the URL is the code for packages released by the `Landslide Hazards Program <https://www.usgs.gov/programs/landslide-hazards>`_.


Using these docs
----------------
These docs contain a variety of resources for wildcat users. The :doc:`User Guide </guide/index>` is designed to introduce new users to the toolbox and is usually the best place to start. After reading the guide, you should be able to implement a basic hazard assessment.

Wildcat commands are complex, multi-step processes. You can use the :doc:`Commands </commands/index>` section to find detailed overviews of the steps and settings for each command. Reading this section is not necessary for running wildcat, but users may benefit by understanding how wildcat works under the hood.

The :doc:`API </api/index>` is the complete reference guide to using wildcat. Use it to learn about the configuration settings available via config files, CLI options, and Python kwargs. Most users will find the :doc:`configuration.py API <api/config/index>` sufficient for their needs. This section provides detailed explanations of all settings available via a configuration file, including tips and best practices. The API can also be useful for troubleshooting error messages, as many wildcat error messages will reference the associated configuration file settings.

Finally, you can find links to:

* :doc:`Commonly used datasets <resources/datasets>`, 
* `The latest release <https://code.usgs.gov/ghsc/lhp/wildcat/-/releases/permalink/latest>`_, 
* :doc:`Contribution guidelines </resources/contributing>`, and 
* :doc:`Legal documents </resources/legal>`

under the *Resources* section of the navigation sidebar.


What's in a name?
-----------------
The name "wildcat" is a loose acronym of post-(wil)dfire (d)ebris-flow hazard (c)ommunication and (a)ssessment (t)ool.


Citation
--------
If you use wildcat for a publication, please consider citing it::

    King, J., 2024, wildcat - Command line tool to assess and map post-wildfire debris-flow hazard
    assessments, version 1.0.0: U.S. Geological Survey software release, https://doi.org/10.5066/P14VYAUB

BibTeX::

    @misc{king_2024,
        title = {wildcat - Command line tool to assess and map post-wildfire debris-flow hazard assessments, version 1.0.0},
        author = {King, Jonathan},
        url = {https://code.usgs.gov/ghsc/lhp},
        year = {2024},
        doi = {10.5066/P14VYAUB}
    }


.. toctree::
    :caption: Docs
    :hidden:

    Installation <install>
    User Guide <guide/index>
    Commands <commands/index>
    Advanced Topics <advanced/index>
    API <api/index>


.. toctree::
    :caption: Resources
    :hidden:

    Datasets <resources/datasets>
    Contributing <resources/contributing>
    Legal <resources/legal>
    Release Notes <resources/release-notes/index>
    Latest Release <https://code.usgs.gov/ghsc/lhp/wildcat/-/releases/permalink/latest>

