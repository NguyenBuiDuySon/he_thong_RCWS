#include "actuator_output.hpp"

namespace rcws {

void NullActuatorOutput::apply(
    const ActuatorSetpoint &setpoint
) noexcept
{
    (void)setpoint;
}

void NullActuatorOutput::stop() noexcept
{
}

}  // namespace rcws