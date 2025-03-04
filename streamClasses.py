# streamClasses.py
import asyncio
import asyncio
import logger
import os
import requests
import re
import tools
from typing import Optional, List, Dict
from PyQt6.QtCore import QObject, pyqtSignal


class Movie:
    """A class used to construct the Movie filename."""

    def __init__(
        self,
        title: str,
        url: str,
        year: Optional[str] = None,
        resolution: Optional[str] = None,
        language: Optional[str] = None,
        output_dir: str = "streams",
        movie_output_dir: str = "movies",
        tvshow_output_dir: str = "tvshows",
        file_permissions: int = 0o644,
        dir_permissions: int = 0o755,
    ) -> None:
        """Initializes Movie object."""
        self.title: str = title.strip()
        self.url: str = url
        self.year: Optional[str] = year
        self.resolution: Optional[str] = resolution
        self.language: Optional[str] = language
        self.output_dir: str = output_dir
        self.movie_output_dir: str = movie_output_dir
        self.tvshow_output_dir: str = tvshow_output_dir
        self.file_permissions: int = file_permissions
        self.dir_permissions: int = dir_permissions

    def getFilename(self) -> str:
        """Getter to get the filename for the stream file.

        Returns:
            str: Fully constructed filename for the stream file.
        """
        filestring: list[str] = [tools.sanitize_filename(self.title)]
        if self.year:
            if not self.year.startswith("("):  # Correctly format year
                self.year: str = f"({self.year})"
            filestring.append(self.year)

        if self.resolution:
            filestring.append(self.resolution)

        # Build the full path using os.path.join
        return os.path.join(
            self.output_dir,
            self.movie_output_dir,
            f"{tools.sanitize_filename(self.title)}{' - ' + self.year if self.year else ''}",
            f"{' - '.join(filestring)}.strm",
        )

    def makeStream(self) -> str:
        """Creates the stream file."""
        filename: str = self.getFilename()
        directory: str = os.path.dirname(filename)  # Get the directory part

        tools.makeDirectory(directory)  # Create directory with permissions
        os.chmod(directory, self.dir_permissions)  # Ensure correct permissions

        tools.makeStrm(filename, self.url)
        os.chmod(filename, self.file_permissions)  # Set file permissions
        return filename


class TVEpisode:
    """A class used to construct the TV filename."""

    def __init__(
        self,
        showtitle: str,
        url: str,
        seasonnumber: Optional[str] = None,
        episodenumber: Optional[str] = None,
        resolution: Optional[str] = None,
        language: Optional[str] = None,
        episodename: Optional[str] = None,
        airdate: Optional[str] = None,
        output_dir: str = "streams",
        movie_output_dir: str = "movies",
        tvshow_output_dir: str = "tvshows",
        file_permissions: int = 0o644,
        dir_permissions: int = 0o755,
    ) -> None:
        """Initializes TVEpisode object."""
        self.showtitle: str = showtitle
        self.episodenumber: Optional[str] = episodenumber
        self.seasonnumber: Optional[str] = seasonnumber
        self.episodenumber: Optional[str] = episodenumber  # Corrected typo here, was reassigned
        self.url: str = url
        self.resolution: Optional[str] = resolution
        self.language: Optional[str] = language
        self.episodename: Optional[str] = episodename
        self.airdate: Optional[str] = airdate
        self.sXXeXX: str = f"S{self.seasonnumber}E{self.episodenumber}"
        self.output_dir: str = output_dir
        self.movie_output_dir: str = movie_output_dir
        self.tvshow_output_dir: str = tvshow_output_dir
        self.file_permissions: int = file_permissions
        self.dir_permissions: int = dir_permissions

    def getFilename(self) -> str:
        """Getter to get the filename for the stream file

        :returns: the fully constructed filename with type directory ea. "tvshows/Star Trek the Next Generation - Season 02/Star Trek the Next Generation - S02E07 - The Borgs kill Picard - 1080p.strm"
        :rtype: str
        """
        filestring: list[str] = [tools.sanitize_filename(self.showtitle)]
        if self.airdate:
            filestring.append(self.airdate.strip())
        else:
            filestring.append(self.sXXeXX.strip())
        if self.episodename:
            filestring.append(self.episodename.strip())
        if self.language:
            filestring.append(self.language.strip())
        if self.resolution:
            filestring.append(self.resolution.strip())

        season_dir: str = ""
        if self.seasonnumber:
            season_dir = f"{tools.sanitize_filename(self.showtitle)} - Season {self.seasonnumber.strip()}"

        return os.path.join(
            self.output_dir,
            self.tvshow_output_dir,
            tools.sanitize_filename(self.showtitle),
            season_dir,
            f"{' - '.join(filestring).replace(':', '-').replace('*', '_')}.strm",  # Corrected f-string formatting
        )

    def makeStream(self) -> str:
        """Creates the stream file for TV episodes."""
        filename: str = self.getFilename()
        directory: str = os.path.dirname(filename)

        tools.makeDirectory(directory)  # Create directory
        os.chmod(directory, self.dir_permissions)  # Ensure correct permissions

        tools.makeStrm(filename, self.url)
        os.chmod(directory, self.dir_permissions)  # Ensure correct permissions
        return filename


class rawStreamList(QObject):  # Inherit from QObject for signals
    progress_total = pyqtSignal(int)
    progress_update = pyqtSignal(int)

    def __init__(self, config, log_level: logger.LogLevel) -> None:  # Use logger.LogLevel
        super().__init__()  # Initialize QObject
        self.log = logger.Logger(__file__, log_level=log_level)
        self.streams: Dict[str, str] = {}  # Add type hint for streams
        self.filename: str = config["paths"]["input_m3u"]
        self.output_dir: str = config.get("paths", "output_dir", fallback="streams")
        self.movie_output_dir: str = config.get(
            "output_paths", "movie_output_dir", fallback="movies"
        )
        self.tvshow_output_dir: str = config.get(
            "output_paths", "tvshow_output_dir", fallback="tvshows"
        )
        file_permissions_str: str = config.get("output_paths", "file_permissions", fallback="644")
        dir_permissions_str: str = config.get("output_paths", "dir_permissions", fallback="755")
        self.file_permissions: int = int(file_permissions_str, 8)  # Convert to octal
        self.dir_permissions: int = int(dir_permissions_str, 8)  # Convert to octal
        self.lines: List[str] = []  # Initialize lines as an empty list
        self.read_lines()
        self.parse_line()

    def delete_downloaded_m3u(self) -> None:
        """Deletes the downloaded M3U file if it was downloaded from a URL."""
        if self.filename.startswith("http"):
            downloaded_m3u_path = "m3u/downloaded.m3u"
            if os.path.exists(downloaded_m3u_path):
                try:
                    os.remove(downloaded_m3u_path)
                    self.log.write_to_log(f"Deleted downloaded M3U file: {downloaded_m3u_path}")
                except Exception as e:
                    self.log.write_to_log(f"Error deleting downloaded M3U file: {e}")
            else:
                self.log.write_to_log(f"Downloaded M3U file not found at: {downloaded_m3u_path}")
        else:
            self.log.write_to_log("Input M3U was not downloaded from URL, skipping deletion.")


    def read_lines(self) -> int:
        """Reads lines from the M3U file."""
        try:
            if self.filename.startswith("http://") or self.filename.startswith(
                "https://"
            ):
                response = requests.get(self.filename, timeout=10)  # Add timeout
                response.raise_for_status()  # Raise an exception for bad status codes
                self.lines = response.text.splitlines()
            else:
                with open(self.filename, "r", encoding="utf8") as f:  # Explicitly open in text mode
                    self.lines = [line.rstrip("\n") for line in f]
        except requests.exceptions.RequestException as e:
            self.log.write_to_log(f"Error fetching URL: {e}")
            self.lines = []  # Set lines to an empty list to avoid further processing
        except FileNotFoundError:
            self.log.write_to_log(f"File not found: {self.filename}")
            self.lines = []  # Set lines to an empty list to avoid further processing
        except Exception as e:  # Catch other exceptions like timeout
            self.log.write_to_log(f"An unexpected error occurred during read_lines: {e}")
            self.lines = []

        self.progress_total.emit(len(self.lines))  # Emit total lines
        return len(self.lines)

    def parse_line(self) -> Optional[List[str]]:  # Expecting to return a list of filenames
        """Parses each line from the M3U file to create stream files."""
        linenumber: int = 0
        results: List[str] = []
        numlines: int = len(self.lines)
        while linenumber < numlines:  # Use while loop for clarity
            thisline: str = self.lines[linenumber]
            nextline: Optional[str] = self.lines[linenumber + 1] if linenumber + 1 < numlines else None  # Check boundary
            if not nextline:
                linenumber += 1
                continue

            if re.search("EXTM3U", thisline, re.IGNORECASE):
                linenumber += 1
                continue

            if thisline.startswith("#") and nextline.startswith("#"):
                if tools.verifyURL(self.lines[linenumber + 2]):
                    log_message = f"raw stream found: {linenumber}\\n{'\\n'.join([thisline, nextline])}\\n{self.lines[linenumber + 2]}"
                    self.log.write_to_log(msg=log_message)
                    result = self.parseStream(
                        " ".join([thisline, nextline]), self.lines[linenumber + 2]
                    )
                    if result:
                        results.append(result)
                    linenumber += 3
                else:
                    error_message = f"Error finding raw stream in linenumber: {linenumber}\\n{'\\n'.join(self.lines[linenumber:linenumber + 2])}"
                    self.log.write_to_log(msg=error_message)
                    linenumber += 1
            elif tools.verifyURL(nextline):
                log_message = f"raw stream found: {linenumber}\\n{'\\n'.join([thisline, nextline])}"
                self.log.write_to_log(msg=log_message)
                result = self.parseStream(thisline, nextline)
                if result:
                    results.append(result)
                linenumber += 2
            else:
                linenumber += 1  # Increment linenumber even if no stream is found
            self.progress_update.emit(linenumber)  # Emit current line number
        return results

    def parse_stream_type(self, streaminfo: str) -> str:
        """Parses the stream type from stream info."""
        self.log.write_to_log(f"Parsing stream type for: {streaminfo}")
        if tools.ufcwweMatch(streaminfo):
            return "live"
        if tools.sxxExxMatch(streaminfo) or tools.airDateMatch(streaminfo):  # Combine conditions
            return "vod_tv"
        return "vod_movie"  # Default to vodMovie

    def parseStream(self, streaminfo: str, streamURL: str) -> Optional[str]:
        """Parses a stream and delegates to specific parsers based on stream type."""
        self.log.write_to_log(f"Parsing stream: {streaminfo}, URL: {streamURL}")
        streamtype: str = self.parse_stream_type(streaminfo)
        self.log.write_to_log(f"Stream type: {streamtype}")
        if streamtype == "vod_tv":
            return self.parseVodTv(streaminfo, streamURL)
        if streamtype == "vod_movie":
            return self.parseVodMovie(streaminfo, streamURL)
        return self.parseLiveStream(streaminfo, streamURL)  # No need for elif, only 3 types

    def parseVodTv(self, streaminfo: str, streamURL: str) -> Optional[str]:  # Could return None
        """Parses VOD TV stream info and creates a TVEpisode object."""
        self.log.write_to_log(f"Parsing VOD TV: {streaminfo}, URL: {streamURL}")
        title_match = tools.infoMatch(streaminfo)  # More descriptive variable name
        title: Optional[str] = tools.parseMovieInfo(title_match.group()) if title_match else None  # Use ternary and handle None
        resolution_match = tools.resolutionMatch(streaminfo)  # More descriptive variable name
        resolution: Optional[str] = tools.parseResolution(resolution_match) if resolution_match else None  # Use ternary and handle None
        if title and resolution:  # Only strip resolution if both title and resolution are found
            title = tools.stripResolution(title)
        episodeinfo: Optional[list[Optional[str]]] = tools.parseEpisode(title) # Add type hint

        if episodeinfo and len(episodeinfo) >= 3:  # Check if episodeinfo is valid and has enough elements
            showtitle: Optional[str] = episodeinfo[0]
            episodename: Optional[str] = episodeinfo[1]
            airdate: Optional[str] = episodeinfo[2] if len(episodeinfo) == 3 else None  # Handle airdate or season/episode
            seasonnumber: Optional[str] = episodeinfo[2] if len(episodeinfo) > 3 else None  # Handle season number
            episodenumber: Optional[str] = episodeinfo[3] if len(episodeinfo) > 3 else None  # Handle episode number
            language: Optional[str] = episodeinfo[4] if len(episodeinfo) > 4 else None  # Handle language

            episode = TVEpisode(
                showtitle=showtitle,
                url=streamURL,
                resolution=resolution,
                episodename=episodename,
                airdate=airdate,
                seasonnumber=seasonnumber,
                episodenumber=episodenumber,
                language=language,
                output_dir=self.output_dir,
                movie_output_dir=self.movie_output_dir,
                tvshow_output_dir=self.tvshow_output_dir,
                file_permissions=self.file_permissions,
                dir_permissions=self.dir_permissions,
            )
            self.log.write_to_log(f"TVEpisode object: {episode.__dict__}")
            filename: str = episode.getFilename() # Add type hint
            self.log.write_to_log(f"TVEpisode filename: {filename}")
            created_file = episode.makeStream()
            self.streams[created_file] = created_file
            return created_file

        return None  # Return None if no file created or parsing fails

    def parseLiveStream(
        self, streaminfo: str, streamURL: str
    ) -> Optional[str]:
        """Parses Live stream info (currently does nothing)."""
        self.log.write_to_log(f"Parsing Live Stream: {streaminfo}, URL: {streamURL}")
        return None

    def parseVodMovie(self, streaminfo: str, streamURL: str) -> Optional[str]:  # Could return None
        """Parses VOD Movie stream info and creates a Movie object."""
        self.log.write_to_log(f"Parsing VOD Movie: {streaminfo}, URL: {streamURL}")
        title: Optional[str] = tools.parseMovieInfo(streaminfo)
        resolution_match = tools.resolutionMatch(streaminfo)  # More descriptive variable name
        resolution: Optional[str] = tools.parseResolution(resolution_match) if resolution_match else None  # Use ternary and handle None
        year_match = tools.yearMatch(streaminfo)  # More descriptive variable name
        year: Optional[str] = year_match.group().strip() if year_match else None  # Use ternary and handle None
        if year and title:  # Only strip year if both year and title are found
            title = tools.stripYear(title)

        language_match = tools.languageMatch(title)
        language: Optional[str] = language_match.group().strip() if language_match else None
        if language and title:
            title = tools.stripLanguage(title)

        moviestream = Movie(
            title=title,
            url=streamURL,
            year=year,
            resolution=resolution,
            language=language,
            output_dir=self.output_dir,
            movie_output_dir=self.movie_output_dir,
            tvshow_output_dir=self.tvshow_output_dir,
            file_permissions=self.file_permissions,
            dir_permissions=self.dir_permissions,
        )
        self.log.write_to_log(f"Movie object: {moviestream.__dict__}")
        filename: str = moviestream.getFilename() # Add type hint
        self.log.write_to_log(f"Movie filename: {filename}")
        created_file: str = moviestream.makeStream() # Add type hint
        self.streams[created_file] = created_file
        return created_file
