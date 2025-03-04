# tools.py
import re
import os
from typing import Optional, List, Match


# Pre-compile regular expressions
_COMPILED_REGEX = {
    "verify_url": re.compile("://"),
    "tvg_type": re.compile('tvg-type="(.*?)"', re.IGNORECASE),
    "ufc_wwe": re.compile("[U][f][c]|[w][w][e]|[r][i][d][i][c][u][l]", re.IGNORECASE),
    "air_date": re.compile(
        "[1-2][0-9][0-9][0-9][ ][0-3][0-9][ ][0-1][0-9]|[1-2][0-9][0-9][0-9][ ][0-1][0-9][ ][0-3][0-9]"
    ),
    "tvg_name": re.compile('tvg-name="(.*?)"', re.IGNORECASE),
    "tvg_id": re.compile('tvg-ID="(.*?)"', re.IGNORECASE),
    "tvg_logo": re.compile('tvg-logo="(.*?)"', re.IGNORECASE),
    "tvg_group": re.compile('group-title="(.*?)"', re.IGNORECASE),
    "info": re.compile("[,](?!.*[,])(.*?)$", re.IGNORECASE),
    "sxx_exx": re.compile(
        "[s][0-9][0-9][e][0-9][0-9]|[0-9][0-9][x][0-9][0-9][ ][-][ ]|[s][0-9][0-9][ ][e][0-9][0-9]|[0-9][0-9][x][0-9][0-9]",
        re.IGNORECASE,
    ),
    "tvg_channel": re.compile('tvg-chno="(.*?)"', re.IGNORECASE),
    "year": re.compile("[(][1-2][0-9][0-9][0-9][)]"),
    "resolution": re.compile("HD|SD|720p WEB x264-XLF|WEB x264-XLF"),
    "episode": re.compile("[e][0-9][0-9]|[0-9][0-9][x][0-9][0-9]", re.IGNORECASE),
    "season": re.compile("[s][0-9][0-9]", re.IGNORECASE),
    "imdb": re.compile("[t][t][0-9][0-9][0-9]"),
    "language": re.compile("[|][A-Z][A-Z][|]", re.IGNORECASE),
}


def verifyURL(line: str) -> bool:
    """Checks if a line contains a URL."""
    return bool(_COMPILED_REGEX["verify_url"].search(line))


def _extract_value(line: str, pattern_name: str) -> Optional[Match[str]]:
    """Extracts a value enclosed in double quotes after a specific tag."""
    match: Optional[Match[str]] = _COMPILED_REGEX[pattern_name].search(line)
    return match


def tvgTypeMatch(line: str) -> Optional[Match[str]]:
    """Matches tvg-type."""
    return _extract_value(line, "tvg_type")


def ufcwweMatch(line: str) -> Optional[Match[str]]:
    """Matches UFC/WWE."""
    return _COMPILED_REGEX["ufc_wwe"].search(line)


def airDateMatch(line: str) -> Optional[Match[str]]:
    """Matches air date."""
    return _COMPILED_REGEX["air_date"].search(line)


def tvgNameMatch(line: str) -> Optional[Match[str]]:
    """Matches tvg-name."""
    return _extract_value(line, "tvg_name")


def tvidmatch(line: str) -> Optional[Match[str]]:
    """Matches tvg-ID."""
    return _extract_value(line, "tvg_id")


def tvgLogoMatch(line: str) -> Optional[Match[str]]:
    """Matches tvg-logo."""
    return _extract_value(line, "tvg_logo")


def tvgGroupMatch(line: str) -> Optional[Match[str]]:
    """Matches group-title."""
    return _extract_value(line, "tvg_group")


def infoMatch(line: str) -> Optional[Match[str]]:
    """Matches info."""
    return _COMPILED_REGEX["info"].search(line)


def getResult(re_match: Match[str]) -> Optional[str]:
    """Extracts the matched string from a regular expression match."""
    if re_match:
        return re_match.group().split('"')[1]
    return None


def sxxExxMatch(line: str) -> Optional[Match[str]]:
    """Matches SxxExx."""
    tvshowmatch: Optional[Match[str]] = _COMPILED_REGEX["sxx_exx"].search(line)
    if tvshowmatch:
        return tvshowmatch
    tvshowmatch = seasonMatch2(line)
    if tvshowmatch:
        return tvshowmatch
    tvshowmatch = episodeMatch2(line)
    if tvshowmatch:
        return tvshowmatch
    return None


def tvgChannelMatch(line: str) -> Optional[Match[str]]:
    """Matches tvg-chno."""
    return _extract_value(line, "tvg_channel")


def yearMatch(line: str) -> Optional[Match[str]]:
    """Matches year."""
    return _COMPILED_REGEX["year"].search(line)


def resolutionMatch(line: str) -> Optional[Match[str]]:
    """Matches resolution."""
    return _COMPILED_REGEX["resolution"].search(line)


def episodeMatch(line: str) -> Optional[str]:
    """Matches episode."""
    episodematch: Optional[Match[str]] = _COMPILED_REGEX["episode"].search(line)
    if episodematch:
        if episodematch.end() - episodematch.start() > 3:
            episodenumber: str = episodematch.group()[3:]
        else:
            episodenumber: str = episodematch.group()[1:]
        return episodenumber
    return None


def episodeMatch2(line: str) -> Optional[Match[str]]:
    """Matches episode (alternative)."""
    return _COMPILED_REGEX["episode"].search(line)


def seasonMatch2(line: str) -> Optional[Match[str]]:
    """Matches season (alternative)."""
    return _COMPILED_REGEX["season"].search(line)


def seasonMatch(line: str) -> Optional[str]:
    """Matches season."""
    seasonmatch: Optional[Match[str]] = _COMPILED_REGEX["season"].search(line)
    if seasonmatch:
        if seasonmatch.end() - seasonmatch.start() > 3:
            seasonnumber: str = seasonmatch.group()[:3]
        else:
            seasonnumber: str = seasonmatch.group()[1:]
        return seasonnumber
    return None


def imdbCheck(line: str) -> Optional[Match[str]]:
    """Matches IMDb ID."""
    return _COMPILED_REGEX["imdb"].search(line)


def parseMovieInfo(info: str) -> str:
    """Parses movie information."""
    if "," in info:
        info = info.split(",")
    if info[0] == "":
        del info[0]
    info: str = info[-1]
    if "#" in info:
        info = info.split("#")[0]
    if ":" in info:
        info = info.split(":")
        if resolutionMatch(info[0]):
            info = info[1]
        else:
            info: str = ":".join(info)
    return info.strip()


def parseResolution(match: Match[str]) -> Optional[str]:
    """Parses resolution."""
    resolutionmatch: str = match.group().strip()
    if resolutionmatch == "HD" or resolutionmatch == "720p WEB x264-XLF":
        return "720p"
    elif resolutionmatch == "SD" or resolutionmatch == "WEB x264-XLF":
        return "480p"
    return None


def makeStrm(filename: str, url: str) -> None:
    """Creates a .strm file."""
    if not os.path.exists(filename):
        with open(filename, "w+", encoding="utf-8") as streamfile:
            streamfile.write(url)
        print(f"strm file created: {filename}")
    else:
        print(f"Strm file already exists: {filename}")


def makeDirectory(directory: str) -> None:
    """Creates a directory."""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"directory created: {directory}")
    else:
        print(f"directory found: {directory}")


def sanitize_filename(filename: str) -> str:
    """Sanitizes a filename by replacing invalid characters."""
    return filename.replace(":", "-").replace("*", "_").replace("/", "_").replace("?", "").replace("#", "")


def stripYear(title: str) -> str:
    """Strips year from title."""
    yearmatch: str = re.sub(
        "[(][1-2][0-9][0-9][0-9][)]|[1-2][0-9][0-9][0-9]", "", title
    )
    if yearmatch:
        return yearmatch.strip()
    return title.strip()


def languageMatch(line: str) -> Optional[Match[str]]:
    """Matches language."""
    return _COMPILED_REGEX["language"].search(line)


def stripLanguage(title: str) -> str:
    """Strips language from title."""
    languagematch: str = re.sub("[|][A-Z][A-Z][|]", "", title, flags=re.IGNORECASE)
    if languagematch:
        return languagematch.strip()
    return title.strip()


def stripResolution(title: str) -> str:
    """Strips resolution from title."""
    resolutionmatch: str = re.sub("HD|SD|720p WEB x264-XLF|WEB x264-XLF", "", title)
    if resolutionmatch:
        return resolutionmatch.strip()
    return title.strip()


def stripSxxExx(title: str) -> str:
    """Strips SxxExx from title."""
    sxxexxmatch: str = re.sub(
        "[s][0-9][0-9][e][0-9][0-9]|[0-9][0-9][x][0-9][0-9][ ][-][ ]|[0-9][0-9][x][0-9][0-9]|[s][0-9][0-9][ ][e][0-9][0-9]",
        "",
        title,
        flags=re.IGNORECASE,
    )
    if sxxexxmatch:
        return sxxexxmatch.strip()
    return title.strip()


def parseEpisode(title: str) -> Optional[List[Optional[str]]]:
    """Parses episode information."""
    airdate: Optional[Match[str]] = airDateMatch(title)
    titlelen: int = len(title)
    showtitle: Optional[str] = None
    episodetitle: Optional[str] = None
    language: Optional[str] = None
    if airdate:
        showtitle = title[: airdate.start()].strip()
        if airdate.end() != titlelen:
            episodetitle = title[airdate.end():].strip()
        return [showtitle, episodetitle, airdate.group()]
    seasonepisode: Optional[Match[str]] = sxxExxMatch(title)
    if seasonepisode:
        print(seasonepisode)
        if (
            seasonepisode.end() - seasonepisode.start() > 6
            or len(seasonepisode.group()) == 5
        ):
            episodetitle = title[seasonepisode.end():].strip()
            seasonnumber: Optional[str] = seasonMatch(title)
            episodenumber: Optional[str] = episodeMatch(title)
            showtitle = title[: seasonepisode.start()]
            languagem: Optional[Match[str]] = languageMatch(showtitle)
            if languagem:
                language = languagem.group().strip("|")
                showtitle = showtitle[languagem.end():]
                language2: Optional[Match[str]] = languageMatch(showtitle)
                if language2:
                    showtitle = showtitle[: language2.start()]
                    season: Optional[Match[str]] = seasonMatch2(showtitle)
                    if season:
                        showtitle = showtitle[: season.start()]
        else:
            seasonnumber: Optional[str] = seasonMatch(title)
            episodenumber: Optional[str] = episodeMatch(title)
            showtitle = stripSxxExx(title)
        return [showtitle, episodetitle, seasonnumber, episodenumber, language]


def check_file_exists(file_path: str) -> bool:
    """
    Check if a file exists at the given path.

    :param file_path: The path to the file.
    :type file_path: str
    :return: True if the file exists, False otherwise.
    """
    return os.path.exists(file_path)
