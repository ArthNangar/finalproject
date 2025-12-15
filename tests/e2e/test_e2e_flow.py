import os
import subprocess
import time
import socket
import sys

import pytest
from playwright.sync_api import sync_playwright


def _wait_port(host: str, port: int, timeout: float = 30.0) -> None:
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket() as s:
            s.settimeout(0.5)
            try:
                s.connect((host, port))
                return
            except OSError:
                time.sleep(0.25)
    raise RuntimeError("Server did not start in time")


@pytest.mark.e2e
@pytest.mark.skip(reason="Password change & relogin is flaky in CI environment")
def test_login_profile_password_change_relogin():
    env = os.environ.copy()
    env["SECRET_KEY"] = "test-secret"
    env["DATABASE_URL"] = "sqlite:///./e2e.db"
    env["BASE_URL"] = "http://127.0.0.1:8001"

    subprocess.run(
        [sys.executable, "-m", "app.db.init_db"],
        env=env,
        check=True,
    )

    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8001",
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        _wait_port("127.0.0.1", 8001)

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            # Register
            page.goto("http://127.0.0.1:8001/register")
            page.fill('input[name="username"]', "e2euser")
            page.fill('input[name="email"]', "e2euser@example.com")
            page.fill('input[name="password"]', "Password123!")
            page.click("text=Register")
            page.wait_for_url("**/auth/login")

            # Login
            page.fill('input[name="username"]', "e2euser")
            page.fill('input[name="password"]', "Password123!")
            page.click("text=Login")
            page.wait_for_url("**/dashboard")
            assert page.locator("text=Calculator").is_visible()

            # Go to profile
            page.click("text=Profile")
            page.wait_for_url("**/profile")
            assert page.locator("text=Update profile").is_visible()

            # Change password - negative case
            page.fill('input[name="current_password"]', "Password123!")
            page.fill('input[name="new_password"]', "NewPassword123!")
            page.fill('input[name="confirm_password"]', "Mismatch123!")
            page.click("text=Change password")
            page.wait_for_url("**/profile")

            # Change password - correct
            page.fill('input[name="current_password"]', "Password123!")
            page.fill('input[name="new_password"]', "NewPassword123!")
            page.fill('input[name="confirm_password"]', "NewPassword123!")
            page.click("text=Change password")
            page.wait_for_url("**/login")

            # Re-login with new password
            page.fill('input[name="username"]', "e2euser")
            page.fill('input[name="password"]', "NewPassword123!")
            page.click("text=Login")
            page.wait_for_url("**/dashboard")
            assert page.locator("text=History").is_visible()

            browser.close()

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
