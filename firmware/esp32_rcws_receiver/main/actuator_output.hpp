#pragma once

#include <cstdint>

namespace rcws {

struct ActuatorSetpoint {
    std::int16_t pan_milli = 0;
    std::int16_t tilt_milli = 0;
};

class ActuatorOutput {
public:
    virtual ~ActuatorOutput() = default;

    virtual void apply(
        const ActuatorSetpoint &setpoint
    ) noexcept = 0;

    virtual void stop() noexcept = 0;
};

class NullActuatorOutput final : public ActuatorOutput {
public:
    void apply(
        const ActuatorSetpoint &setpoint
    ) noexcept override;

    void stop() noexcept override;
};

}  // namespace rcws