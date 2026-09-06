#pragma once

#include <stdint.h>

namespace rcws {

struct WireCommand {
    uint16_t sequence;
    bool active;
    int16_t pan_milli;
    int16_t tilt_milli;
};

enum class ParseError {
    None,
    InvalidFieldCount,
    UnsupportedProtocol,
    InvalidSequence,
    InvalidActive,
    InvalidPan,
    InvalidTilt,
    InactiveMotion,
};

bool decode_command(
    char *line,
    WireCommand &command,
    ParseError &error
);

const char *parse_error_name(ParseError error);

}  // namespace rcws