#include "receiver_guard.hpp"

namespace rcws {

namespace {

constexpr std::uint16_t SEQUENCE_HALF_RANGE = 1U << 15;

}  // namespace

ReceiverGuard::ReceiverGuard(const std::int64_t timeout_us) noexcept
    : timeout_us_(timeout_us > 0 ? timeout_us : 1)
{
}

GuardDecision ReceiverGuard::accept(
    const std::uint16_t sequence,
    const bool active,
    const std::int64_t now_us
) noexcept
{
    if (session_expired(now_us)) {
        reset();
    }

    if (
        has_last_sequence_
        && !is_newer_sequence(sequence, last_sequence_)
    ) {
        return GuardDecision::replay_or_stale;
    }

    last_sequence_ = sequence;
    has_last_sequence_ = true;

    last_valid_us_ = now_us;
    has_last_valid_time_ = true;

    active_ = active;

    return GuardDecision::accepted;
}

bool ReceiverGuard::should_stop(const std::int64_t now_us) const noexcept
{
    if (!has_last_valid_time_) {
        return true;
    }

    if (session_expired(now_us)) {
        return true;
    }

    return !active_;
}

void ReceiverGuard::reset() noexcept
{
    has_last_sequence_ = false;
    last_sequence_ = 0;

    has_last_valid_time_ = false;
    last_valid_us_ = 0;

    active_ = false;
}

bool ReceiverGuard::session_expired(
    const std::int64_t now_us
) const noexcept
{
    if (!has_last_valid_time_) {
        return false;
    }

    // esp_timer_get_time() is monotonic during normal runtime.
    // Treat a backwards timestamp defensively as an expired session.
    if (now_us < last_valid_us_) {
        return true;
    }

    return now_us - last_valid_us_ >= timeout_us_;
}

bool ReceiverGuard::is_newer_sequence(
    const std::uint16_t candidate,
    const std::uint16_t previous
) noexcept
{
    const std::uint16_t delta =
        static_cast<std::uint16_t>(candidate - previous);

    return delta != 0 && delta < SEQUENCE_HALF_RANGE;
}

}  // namespace rcws