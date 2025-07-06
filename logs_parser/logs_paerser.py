import time

def follow_log(file_path, flags_to_check):
    """
    Generator that yields new lines appended to the log file.
    """
    with open(file_path, 'r') as f:
        # Go to the end of the file
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)  # wait for new data
                continue
            yield line.rstrip('\n')

def parse_line_for_flags(line, flags):
    """
    Check if any of the flags are in the line and extract their values.
    Assumes format: ... flag=value ...
    Returns a dict {flag: value} for found flags.
    """
    found = {}
    for flag in flags:
        if flag in line:
            # Simple extraction: find flag=VALUE pattern
            # Adjust regex or parsing as per your log format
            import re
            pattern = rf'{flag}\s*=\s*([^\s,]+)'
            match = re.search(pattern, line)
            if match:
                found[flag] = match.group(1)
            else:
                # Flag present but no value found, store None or True
                found[flag] = None
    return found

if __name__ == "__main__":
    log_file_path = 'your_log_file.log'
    flags = ['ERROR_FLAG_X', 'WARN_FLAG_Y']  # flags to monitor

    print(f"Monitoring {log_file_path} for flags: {flags}")

    for new_line in follow_log(log_file_path):
        flags_found = parse_line_for_flags(new_line, flags)
        if flags_found:
            print(f"Flags found in new log line: {flags_found}")
