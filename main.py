# main.py
import argparse
import configparser
import sys
from typing import Optional

import logger
import streamClasses
import tools
import wget  # Keep this here for the CLI mode


def main() -> None:
    """
    Main function to run the M3U to STRM conversion.

    Processes command-line arguments, sets up logging, and either runs the
    UI or processes the M3U file directly in CLI mode.
    """
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Set up logging
    log_level_str: str = config.get(
        "settings", "log_level", fallback="INFO").upper()
    log_level: int = getattr(
        logger.LogLevel,
        log_level_str,
        logger.LogLevel.INFO)
    log = logger.Logger(__file__, log_level=log_level)
    log.write_to_log(f"Log level set to: {log_level_str}")
    log.ui_emitter.log_signal.connect(
        lambda msg: None
    )  # Do nothing, ui.py handles this

    parser = argparse.ArgumentParser(
        description="Process M3U files to create STRM files."
    )
    parser.add_argument(
        "--no-ui", action="store_true", help="Disable UI and run in CLI mode"
    )
    args: argparse.Namespace = parser.parse_args()
    log.write_to_log(f"Command-line arguments: {args}")

    if not args.no_ui:
        from PyQt6.QtWidgets import QApplication
        from ui import (
            MainWindow,
        )  # Import here to avoid issues if PyQt6 is not installed

        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        # ipttvurl = r"C:\Users\000\Desktop\iptmovies.m3u" #replace url with your link, or comment this line out and put the filename in the streamlist below.
        # print(wget.download(iptmovieurl, ('m3u/iptmovies.m3u'))) #if not
        # downloading comment out this line.
        input_m3u: str = config.get("paths", "input_m3u")
        if input_m3u.startswith("http"):
            log.write_to_log(f"Downloading M3U from {input_m3u}...")
            try:
                local_m3u_path: str = "m3u/downloaded.m3u"  # Temporary local path
                wget.download(input_m3u, local_m3u_path)
                log.write_to_log("Download complete.")
                input_m3u = local_m3u_path  # Use the local file
            except Exception as e:
                log.write_to_log(f"Error downloading M3U: {e}")
                return
        elif not input_m3u.startswith("/") and not input_m3u.startswith("C:\\"):
            input_m3u = f"m3u/{input_m3u}"
        apollomovies = streamClasses.rawStreamList(config, log_level=log_level)
        apollomovies.delete_downloaded_m3u()


if __name__ == "__main__":
    main()
