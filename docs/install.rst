Install Wildcat
===============

.. note:: 

    These instructions are for wildcat users. If you plan to develop wildcat, you should do a :ref:`developer installation <dev-install>` instead.

.. admonition:: Prerequisites

    Wildcat requires `Python 3.11 or 3.12 <https://www.python.org/downloads/>`_.


Quick Install
-------------

You can install the latest release using::

    pip install wildcat -i https://code.usgs.gov/api/v4/groups/859/-/packages/pypi/simple

The URL in this command instructs `pip <https://pip.pypa.io/en/stable/>`_ to install wildcat from the official USGS package registry. This ensures that you are installing an official USGS product, and not a similarly named package from a third party. The ``859`` in the URL is the code for packages released by the `Landslide Hazards Program <https://www.usgs.gov/programs/landslide-hazards>`_.


Advanced Install
----------------

You can use standard `pip <https://pip.pypa.io/en/stable/>`_ notation to install wildcat releases. For example, to install a specific release use::

    pip install wildcat==X.Y.Z -i https://code.usgs.gov/api/v4/groups/859/-/packages/pypi/simple

where ``X.Y.Z`` is the release tag.

----

You can also install the most recent development from the main branch using::

    pip install git+https://code.usgs.gov/ghsc/lhp/wildcat@main

However, be warned that active development is not stable, so may change at any time without warning. 

.. note::
    
    This option also requires `git <https://git-scm.com/downloads>`_ as a prerequisite.






