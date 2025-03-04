# m3u\_to\_strm

This script converts .m3u playlist files to .strm files, organizing them into a directory structure suitable for media players like Kodi or Plex.

## Features

*   Converts .m3u playlists to .strm files.
*   Supports both local .m3u files and URLs.
*   Automatically creates a directory structure for movies and TV shows:
    *   Movies: `movies/Movie Title - Year/Movie Title - Year - Resolution.strm`
    *   TV Shows: `tvshows/Show Title/Show Title - Season XX/Show Title - SXXEXX - Episode Title - Resolution.strm`
*   Extracts metadata (title, year, resolution, season, episode, etc.) from the .m3u entries.

## Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/evilgenx/m3u_to_strm.git
    cd m3u_to_strm
    ```
2.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The script is configured using the `config.ini` file.

*   **`input_m3u`:**  The path to your .m3u file or a URL pointing to an .m3u playlist.
*   **`output_dir`:** The directory where the .strm files and folder structure will be created.

Example `config.ini`:

```ini
[paths]
input_m3u = YOUR_M3U_URL_OR_PATH
output_dir = streams

[settings]
log_level = INFO
```

## Usage
Run the script using the following command:
```bash
python main.py
```

## Dependencies

*   requests
*   wget

These can be installed using: `pip install requests wget`

## Fork/Credits

This project is forked from: [https://github.com/silence48/m3u2strm](https://github.com/silence48/m3u2strm)

## Example
```
streams/
├── movies/
│   └── Movie Title - Year/
│       └── Movie Title - Year - Resolution.strm
└── tvshows/
    └── Show Title/
        └── Show Title - Season 01/
            └── Show Title - S01E01 - Episode Title - Resolution.strm
```

## License

MIT License

Copyright (c) 2024 BlackGlassSkin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
