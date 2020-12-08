from tests.utilities.utilities import async_return
from tests.utilities.utilities import run_async
from tardis.adapters.batchsystems.slurm import SlurmAdapter
from tardis.utilities.attributedict import AttributeDict

from tardis.adapters.batchsystems.slurm import slurm_status_updater
from tardis.interfaces.batchsystemadapter import MachineStatus

from tardis.exceptions.executorexceptions import CommandExecutionFailure

from functools import partial
from unittest.mock import MagicMock, patch
from unittest import TestCase


class TestSlurmAdapter(TestCase):
    mock_config_patcher = None
    mock_async_run_command_patcher = None

    @classmethod
    def setUpClass(cls):
        cls.mock_config_patcher = patch(
            "tardis.adapters.batchsystems.slurm.Configuration"
        )
        cls.mock_async_run_command_patcher = patch(
            "tardis.adapters.batchsystems.slurm.async_run_command", new=MagicMock()
        )
        cls.mock_config = cls.mock_config_patcher.start()
        cls.mock_async_run_command = cls.mock_async_run_command_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.mock_config_patcher.stop()
        cls.mock_async_run_command_patcher.stop()

    def setUp(self):
        self.cpu_ratio = 0.5
        self.memory_ratio = 0.25

        self.command = 'sinfo --Format="statelong,cpusstate,allocmem,memory,features,nodehost" -e --noheader -r --partition=test_part'  # noqa B950

        self.command_wo_options = 'sinfo --Format="statelong,cpusstate,allocmem,memory,features,nodehost" -e --noheader -r'  # noqa B950

        return_value = "\n".join(
            [
                "mixed      2/2/0/4   6000    24000   VM-1   host-10-18-1-1",
                "mixed      3/1/0/4   15853   22011   VM-2   host-10-18-1-2",
                "mixed      1/3/0/4   18268   22011   VM-3   host-10-18-1-4",
                "mixed      3/1/0/4   17803   22011   VM-4   host-10-18-1-7",
                "draining   0/4/0/4   17803   22011   draining_m   draining_m",
                "idle       0/4/0/4   17803   22011   idle_m   idle_m",
                "drained    0/4/0/4   17803   22011   drained_m   drained_m",
                "powerup    0/4/0/4   17803   22011   pwr_up_m   pwr_up_m",
            ]
        )

        self.mock_async_run_command.return_value = async_return(
            return_value=return_value
        )

        self.setup_config_mock(
            options=AttributeDict({"long": {"partition": "test_part"}})
        )

        self.slurm_adapter = SlurmAdapter()

    def tearDown(self):
        self.mock_async_run_command.reset_mock()

    def setup_config_mock(self, options=None):
        self.config = self.mock_config.return_value
        self.config.BatchSystem.max_age = 10
        if options:
            self.config.BatchSystem.options = options
        else:
            self.config.BatchSystem.options = {}

    def test_disintegrate_machine(self):
        self.assertIsNone(
            run_async(self.slurm_adapter.disintegrate_machine, drone_uuid="test")
        )

    def test_drain_machine(self):
        run_async(self.slurm_adapter.drain_machine, drone_uuid="VM-1")
        self.mock_async_run_command.assert_called_with(
            "scontrol update NodeName=host-10-18-1-1 State=DRAIN Reason='COBalD/TARDIS'"
        )

        self.mock_async_run_command.reset_mock()

        self.assertIsNone(
            run_async(self.slurm_adapter.drain_machine, drone_uuid="not_exists")
        )
        self.mock_async_run_command.side_effect = CommandExecutionFailure(
            message="Does not exists", exit_code=1, stderr="Does not exists"
        )
        with self.assertRaises(CommandExecutionFailure):
            self.assertIsNone(
                run_async(self.slurm_adapter.drain_machine, drone_uuid="idle_m")
            )

        self.mock_async_run_command.side_effect = None

    def test_drain_machine_without_options(self):
        self.setup_config_mock()
        self.slurm_adapter = SlurmAdapter()

        run_async(self.slurm_adapter.drain_machine, drone_uuid="VM-1")
        self.mock_async_run_command.assert_called_with(
            "scontrol update NodeName=host-10-18-1-1 State=DRAIN Reason='COBalD/TARDIS'"
        )

    def test_integrate_machine(self):
        self.assertIsNone(
            run_async(self.slurm_adapter.integrate_machine, drone_uuid="VM-1")
        )

    def test_get_resource_ratios(self):
        self.assertEqual(
            list(run_async(self.slurm_adapter.get_resource_ratios, drone_uuid="VM-1")),
            [self.cpu_ratio, self.memory_ratio],
        )
        self.mock_async_run_command.assert_called_with(self.command)

        self.assertEqual(
            run_async(self.slurm_adapter.get_resource_ratios, drone_uuid="not_exists"),
            {},
        )

    def test_get_resource_ratios_without_options(self):
        self.setup_config_mock()
        del self.config.BatchSystem.options
        self.slurm_adapter = SlurmAdapter()

        self.assertEqual(
            list(run_async(self.slurm_adapter.get_resource_ratios, drone_uuid="VM-1")),
            [self.cpu_ratio, self.memory_ratio],
        )

        self.mock_async_run_command.assert_called_with(self.command_wo_options)

    def test_get_allocation(self):
        self.assertEqual(
            run_async(self.slurm_adapter.get_allocation, drone_uuid="VM-1"),
            max([self.cpu_ratio, self.memory_ratio]),
        )
        self.mock_async_run_command.assert_called_with(self.command)

        self.assertEqual(
            run_async(self.slurm_adapter.get_allocation, drone_uuid="not_exists"),
            0.0,
        )

    def test_get_machine_status(self):
        state_mapping = {
            "VM-1": MachineStatus.Available,
            "not_exists": MachineStatus.NotAvailable,
            "draining_m": MachineStatus.Draining,
            "idle_m": MachineStatus.Available,
            "drained_m": MachineStatus.NotAvailable,
            "pwr_up_m": MachineStatus.NotAvailable,
        }

        for machine, state in state_mapping.items():
            self.assertEqual(
                run_async(self.slurm_adapter.get_machine_status, drone_uuid=machine),
                state,
            )

        self.mock_async_run_command.reset_mock()

        self.mock_async_run_command.side_effect = CommandExecutionFailure(
            message="Test", exit_code=123, stderr="Test"
        )
        with self.assertLogs(level="WARN"):
            with self.assertRaises(CommandExecutionFailure):
                attributes = {
                    "Machine": "Machine",
                    "State": "State",
                    "Activity": "Activity",
                    "TardisDroneUuid": "TardisDroneUuid",
                }
                run_async(
                    partial(
                        slurm_status_updater,
                        self.config.BatchSystem.options,
                        attributes,
                    )
                )
                self.mock_async_run_command.assert_called_with(self.command)

        self.mock_async_run_command.side_effect = None

    def test_get_utilisation(self):
        self.assertEqual(
            run_async(self.slurm_adapter.get_utilisation, drone_uuid="VM-1"),
            min([self.cpu_ratio, self.memory_ratio]),
        )
        self.mock_async_run_command.assert_called_with(self.command)

        self.assertEqual(
            run_async(self.slurm_adapter.get_utilisation, drone_uuid="not_exists"),
            0.0,
        )

    def test_machine_meta_data_translation(self):
        self.assertEqual(
            {"Cores": 1, "Memory": 1000, "Disk": 1000},
            self.slurm_adapter.machine_meta_data_translation_mapping,
        )
