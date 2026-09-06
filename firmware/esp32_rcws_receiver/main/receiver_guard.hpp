#pragma once

#include <cstdint>

namespace rcws {

enum class GuardDecision : std::uint8_t {
    accepted = 0,
    replay_or_stale,
};

class ReceiverGuard {
public:
    explicit ReceiverGuard(std::int64_t timeout_us) noexcept;

    GuardDecision accept(
        std::uint16_t sequence,
        bool active,
        std::int64_t now_us
    ) noexcept;

    [[nodiscard]] bool should_stop(std::int64_t now_us) const noexcept;

    void reset() noexcept;

private:
    [[nodiscard]] bool session_expired(std::int64_t now_us) const noexcept;

    [[nodiscard]] static bool is_newer_sequence(
        std::uint16_t candidate,
        std::uint16_t previous
    ) noexcept;

    std::int64_t timeout_us_;

    bool has_last_sequence_ = false;
    std::uint16_t last_sequence_ = 0;

    bool has_last_valid_time_ = false;
    std::int64_t last_valid_us_ = 0;

    bool active_ = false;
};

}  // namespace rcws