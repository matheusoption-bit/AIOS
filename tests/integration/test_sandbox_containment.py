import os
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from infra.sandbox.adapter import E2BSandboxAdapter


@unittest.skipUnless(
    os.getenv("AIOS_RUN_SANDBOX_INTEGRATION") == "1" and os.getenv("E2B_API_KEY"),
    "Sandbox integration tests require AIOS_RUN_SANDBOX_INTEGRATION=1 and E2B_API_KEY.",
)
class SandboxContainmentIntegrationTests(unittest.TestCase):
    def test_default_deny_network_and_filesystem(self) -> None:
        adapter = E2BSandboxAdapter()
        create_res = adapter.create("base")
        self.assertTrue(create_res.success, create_res.error)

        try:
            net_res = adapter.run_command("curl -I --connect-timeout 2 google.com", 5.0)
            fs_res = adapter.run_command("ls /home/user/.env", 5.0)
            self.assertNotEqual(net_res.status, "SUCCESS")
            self.assertNotEqual(fs_res.status, "SUCCESS")
        finally:
            adapter.destroy()
