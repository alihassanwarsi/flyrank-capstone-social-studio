import subprocess
import sys
import time


def run_command(command: list[str]) -> None:
    result = subprocess.run(command)

    if result.returncode != 0:
        raise SystemExit(
            f"Command failed: {' '.join(command)}"
        )


def main():
    print("Starting PostgreSQL...")
    run_command(
        ["docker", "compose", "up", "-d"]
    )

    print("Running migrations...")
    run_command(
        [
            sys.executable,
            "-m",
            "app.db.migrations",
        ]
    )

    print("Starting API and worker...")

    api_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ]
    )

    worker_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "app.worker",
        ]
    )

    try:
        while True:
            if api_process.poll() is not None:
                raise RuntimeError(
                    "API process stopped."
                )

            if worker_process.poll() is not None:
                raise RuntimeError(
                    "Worker process stopped."
                )

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping services...")

    finally:
        api_process.terminate()
        worker_process.terminate()

        api_process.wait()
        worker_process.wait()


if __name__ == "__main__":
    main()