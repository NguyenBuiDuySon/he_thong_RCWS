#include "command_state.hpp"

namespace rcws {

const CommandState &CommandStateMachine::current() const noexcept
{
    return state_;
}

const CommandState &CommandStateMachine::apply(
    const WireCommand &command,
    const std::int64_t now_us
) noexcept
{
    state_.sequence = command.sequence;
    state_.updated_us = now_us;

    if (!command.active) {
        return stop(
            StopReason::inactive_command,
            now_us
        );
    }

    state_.active = true;

    state_.pan_milli = command.pan_milli;
    state_.tilt_milli = command.tilt_milli;

    state_.stop_reason = StopReason::none;

    return state_;
}

const CommandState &CommandStateMachine::stop(
    const StopReason reason,
    const std::int64_t now_us
) noexcept
{
    state_.active = false;

    state_.pan_milli = 0;
    state_.tilt_milli = 0;

    state_.updated_us = now_us;
    state_.stop_reason = reason;

    return state_;
}

const char *stop_reason_name(
    const StopReason reason
) noexcept
{
    switch (reason) {
        case StopReason::none:
            return "none";

        case StopReason::startup:
            return "startup";

        case StopReason::inactive_command:
            return "inactive_command";

        case StopReason::timeout:
            return "timeout";
    }

    return "unknown";
}

}  // namespace rcws