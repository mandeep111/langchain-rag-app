import os
import subprocess
import sys
import textwrap


def test_env_file_overrides_stale_shell_openai_key(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "OPENAI_API_KEY=from-dotenv",
                "DATABASE_URL=sqlite:///from-dotenv.db",
                "REDIS_URL=redis://dotenv:6379/0",
            ]
        ),
        encoding="utf-8",
    )

    script = textwrap.dedent(
        """
        import os
        from app.core.config import settings

        print(settings.OPENAI_API_KEY)
        print(os.environ["OPENAI_API_KEY"])
        """
    )
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = "from-shell"
    env["PYTHONPATH"] = os.getcwd()

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )

    assert result.stdout.splitlines() == ["from-dotenv", "from-dotenv"]
