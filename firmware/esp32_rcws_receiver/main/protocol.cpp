#include "protocol.hpp"

#include <errno.h>
#include <stdlib.h>
#include <string.h>

namespace rcws {
namespace {

constexpr char PROTOCOL[] = "RCWS1";

constexpr size_t FIELD_COUNT = 5;

constexpr long SEQUENCE_MIN = 0;
constexpr long SEQUENCE_MAX = 65535;

constexpr long COMMAND_MIN = -1000;
constexpr long COMMAND_MAX = 1000;

bool split_fields(
    char *line,
    char *fields[FIELD_COUNT]
)
{
    size_t field_count = 1;
    fields[0] = line;

    for (char *cursor = line; *cursor != '\0'; ++cursor) {
        if (*cursor != ',') {
            continue;
        }

        if (field_count >= FIELD_COUNT) {
            return false;
        }

        *cursor = '\0';
        fields[field_count++] = cursor + 1;
    }

    return field_count == FIELD_COUNT;
}

bool parse_integer(
    const char *text,
    long minimum,
    long maximum,
    long &value
)
{
    if (text == nullptr || *text == '\0') {
        return false;
    }

    errno = 0;

    char *end = nullptr;
    const long parsed = strtol(
        text,
        &end,
        10
    );

    if (errno == ERANGE) {
        return false;
    }

    if (end == text || *end != '\0') {
        return false;
    }

    if (parsed < minimum || parsed > maximum) {
        return false;
    }

    value = parsed;
    return true;
}

}  // namespace

bool decode_command(
    char *line,
    WireCommand &command,
    ParseError &error
)
{
    char *fields[FIELD_COUNT];

    if (!split_fields(line, fields)) {
        error = ParseError::InvalidFieldCount;
        return false;
    }

    if (strcmp(fields[0], PROTOCOL) != 0) {
        error = ParseError::UnsupportedProtocol;
        return false;
    }

    long sequence = 0;
    long active = 0;
    long pan_milli = 0;
    long tilt_milli = 0;

    if (!parse_integer(
            fields[1],
            SEQUENCE_MIN,
            SEQUENCE_MAX,
            sequence
        )) {
        error = ParseError::InvalidSequence;
        return false;
    }

    if (!parse_integer(
            fields[2],
            0,
            1,
            active
        )) {
        error = ParseError::InvalidActive;
        return false;
    }

    if (!parse_integer(
            fields[3],
            COMMAND_MIN,
            COMMAND_MAX,
            pan_milli
        )) {
        error = ParseError::InvalidPan;
        return false;
    }

    if (!parse_integer(
            fields[4],
            COMMAND_MIN,
            COMMAND_MAX,
            tilt_milli
        )) {
        error = ParseError::InvalidTilt;
        return false;
    }

    if (
        active == 0 &&
        (pan_milli != 0 || tilt_milli != 0)
    ) {
        error = ParseError::InactiveMotion;
        return false;
    }

    command.sequence = static_cast<uint16_t>(sequence);
    command.active = active != 0;
    command.pan_milli = static_cast<int16_t>(pan_milli);
    command.tilt_milli = static_cast<int16_t>(tilt_milli);

    error = ParseError::None;
    return true;
}

const char *parse_error_name(ParseError error)
{
    switch (error) {
        case ParseError::None:
            return "none";

        case ParseError::InvalidFieldCount:
            return "invalid_field_count";

        case ParseError::UnsupportedProtocol:
            return "unsupported_protocol";

        case ParseError::InvalidSequence:
            return "invalid_sequence";

        case ParseError::InvalidActive:
            return "invalid_active";

        case ParseError::InvalidPan:
            return "invalid_pan";

        case ParseError::InvalidTilt:
            return "invalid_tilt";

        case ParseError::InactiveMotion:
            return "inactive_motion";
    }

    return "unknown";
}

}  // namespace rcws