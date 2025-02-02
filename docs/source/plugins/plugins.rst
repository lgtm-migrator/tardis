.. _ref_plugins:

=======
Plugins
=======

.. container:: left-col

    All plugins are configured within the `plugins` section of the TARDIS configuration. Using multiple plugins is
    supported by using a separate MappingNode per plugin.

.. container:: content-tabs right-col

    .. code-block:: yaml

        Plugins:
            Plugin_1:
                option_1: my_option_1
            Plugin_2:
                option_123: my_option_123

SQLite Registry
---------------

.. content-tabs:: left-col

    The :py:class:`~tardis.plugins.sqliteregistry.SqliteRegistry` implements a persistent storage of all Drone states in a
    SQLite database. The usage of this module is recommended in order to recover the last state of TARDIS in case the
    service has to be restarted.

Available configuration options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. content-tabs:: left-col

    +----------------+-----------------------------------+-----------------+
    | Option         | Short Description                 | Requirement     |
    +================+===================================+=================+
    | db_file        | Location of the SQLite database.  |  **Required**   |
    +----------------+-----------------------------------+-----------------+

.. content-tabs:: right-col

    .. rubric:: Example configuration

    .. code-block:: yaml

        Plugins:
          SqliteRegistry:
            db_file: drone_registry.db

Telegraf Monitoring
-------------------

.. content-tabs:: left-col

    The :py:class:`~tardis.plugins.telegrafmonitoring.TelegrafMonitoring` implements an interface to monitor state changes
    of the Drones in a telegraf service running a UDP input module.

.. content-tabs:: right-col

    .. Note::
        By default the machine name of the host running tardis is added as default tag. It can be overwritten by adding
        `tardis_machine_name: 'something_else'` as `default_tag` in the configuration.

Available configuration options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. content-tabs:: left-col

    +----------------+---------------------------------------------------------------------------+-----------------+
    | Option         | Short Description                                                         | Requirement     |
    +================+===========================================================================+=================+
    | host           | Hostname or IP address the telegraf UDP input module is listening to.     |  **Required**   |
    +----------------+---------------------------------------------------------------------------+-----------------+
    | port           | Port the telegraf UDP input module is listening on.                       |  **Required**   |
    +----------------+---------------------------------------------------------------------------+-----------------+
    | default_tags   | Tags that should be included by default for all entries sent to telegraf. |  **Optional**   |
    +----------------+---------------------------------------------------------------------------+-----------------+

.. content-tabs:: right-col

    .. rubric:: Example configuration

    .. code-block:: yaml

        Plugins:
          TelegrafMonitoring:
            host: der_telegraf.foo.bar
            port: 8092
            default_tags:
              something_default: 'The Default Tag'

Prometheus Monitoring
---------------------

.. content-tabs:: left-col

    The :py:class:`~tardis.plugins.prometheusmonitoring.PrometheusMonitoring` implements an interface to monitor the
    number of drones in the states ``Booting``, ``Running``, ``Stopped``, ``Deleted``, and ``Error``.

Available configuration options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. content-tabs:: left-col

    +----------------+---------------------------------------------------------------------------+-----------------+
    | Option         | Short Description                                                         | Requirement     |
    +================+===========================================================================+=================+
    | addr           | Address on which the metrics are served on for Prometheus                 |  **Required**   |
    +----------------+---------------------------------------------------------------------------+-----------------+
    | port           | Port on which the metrics are served on for Prometheus                    |  **Required**   |
    +----------------+---------------------------------------------------------------------------+-----------------+

.. content-tabs:: right-col

    .. rubric:: Example configuration

    .. code-block:: yaml

        Plugins:
          PrometheusMonitoring:
            addr: 127.0.0.1
            port: 8080

ElasticSearch Monitoring
------------------------

.. content-tabs:: left-col

    The :py:class:`~tardis.plugins.elastisearchmonitoring.ElasticsearchMonitoring` implements an interface to push
    the done state to an Elasticsearch instance at every state change.

Available configuration options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. content-tabs:: left-col

    +----------------+---------------------------------------------------------------------------+-----------------+
    | Option         | Short Description                                                         | Requirement     |
    +================+===========================================================================+=================+
    | host           | Hostname or IP address of the Elasticsearch instance.                     |  **Required**   |
    +----------------+---------------------------------------------------------------------------+-----------------+
    | port           | Port the Elasticsearch instance is listening on.                          |  **Required**   |
    +----------------+---------------------------------------------------------------------------+-----------------+
    | index          | Target index in the Elasticsearch instance                                |  **Required**   |
    +----------------+---------------------------------------------------------------------------+-----------------+
    | meta           | Additional meta data (can be used to distinguish TARDIS instances).       |  **Optional**   |
    +----------------+---------------------------------------------------------------------------+-----------------+

.. content-tabs:: right-col

    .. rubric:: Example configuration

    .. code-block:: yaml

        Plugins:
          ElasticsearchMonitoring:
            host: elasticsearch.foo.bar
            port: 9200
            index: cobald_tardis
            meta: instance1

Auditor Accounting
------------------

.. content-tabs:: left-col

    The :py:class:`~tardis.plugins.auditor.Auditor` implements an interface to push
    information from the drones relevant for accounting to an `Auditor <https://alu-schumacher.github.io/AUDITOR/>`_ instance.
    The plugin extracts the components to be accounted for from the ``MachineMetaData`` in the configuration. 
    Scores which help relating resources of the same kind with different performance to each other can be configured as well.
    Scores are configured for each ``MachineType`` individually and multiple scores per ``MachineType`` are possible.
    An Auditor record requires a ``site_id``, a ``user_id`` and a ``group_id``. The latter two can be configured in the
    ``Auditor`` plugin configuration (and default to ``tardis`` if omitted). The ``site_id`` is taken from the ``Sites`` in
    the TARDIS config.

Available configuration options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. content-tabs:: left-col

    +----------------+--------------------------------------------------------------------------------------------------+-----------------+
    | Option     | Short Description                                                                                    | Requirement     |
    +============+======================================================================================================+=================+
    | host       | Hostname or IP address of the Auditor instance.                                                      |  **Required**   |
    +----------------+--------------------------------------------------------------------------------------------------+-----------------+
    | port       | Port on which the Auditor instance is listening on.                                                  |  **Required**   |
    +----------------+--------------------------------------------------------------------------------------------------+-----------------+
    | user       | User name added to the record. Defaults to ``tardis``.                                               |  **Optional**   |
    +----------------+--------------------------------------------------------------------------------------------------+-----------------+
    | group      | Group name added to the record. Defaults to ``tardis``.                                              |  **Optional**   |
    +----------------+--------------------------------------------------------------------------------------------------+-----------------+
    | components | Configuration of the components per ``MachineType``. Used to attach scores to individual components. |  **Optional**   |
    +----------------+--------------------------------------------------------------------------------------------------+-----------------+

.. content-tabs:: right-col

    .. rubric:: Example configuration

    .. code-block:: yaml

        Plugins:
          Auditor:
            host: "127.0.0.1"
            port: 8000
            user: "some-user"
            group: "some-group"
            components:
              machinetype_1:
                Cores:
                  HEPSPEC06: 1.2
                  OTHERBENCHMARK: 1.4
              machinetype_2:
                Cores:
                  HEPSPEC06: 1.0
                Memory:
                  PRECIOUSMEMORY: 2.0

.. content-tabs:: left-col

    Your favorite monitoring is currently not supported?
    Please, have a look at
    :ref:`how to contribute.<ref_contribute_plugin>`
