#pragma once

#include <cstdint>

#include "protocol.hpp"

namespace rcws {

enum class StopReason : std::uint8_t {
    none = 0,
    startup,
    inactive_command,
    timeout,
};

struct CommandState {
    std::uint16_t sequence = 0;

    bool active = false;

    std::int16_t pan_milli = 0;
    std::int16_t tilt_milli = 0;

    std::int64_t updated_us = 0;

    StopReason stop_reason = StopReason::startup;
};

class CommandStateMachine {
public:
    [[nodiscard]] const CommandState &current() const noexcept;

    const CommandState &apply(
        const WireCommand &command,
        std::int64_t now_us
    ) noexcept;

    const CommandState &stop(
        StopReason reason,
        std::int64_t now_us
    ) noexcept;

private:
    CommandState state_{};
};

[[nodiscard]] const char *stop_reason_name(
    StopReason reason
) noexcept;

}  // namespace rcws