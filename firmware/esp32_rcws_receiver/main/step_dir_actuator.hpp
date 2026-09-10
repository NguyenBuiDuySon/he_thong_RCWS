#pragma once

#include "actuator_output.hpp"

#include "driver/gpio.h"
#include "esp_err.h"
#include "step_pulse_engine.hpp"
#include "step_pulse_engine.hpp"

namespace rcws {

struct StepDirPins {
    gpio_num_t pan_step = GPIO_NUM_NC;
    gpio_num_t pan_dir = GPIO_NUM_NC;
    gpio_num_t pan_enable = GPIO_NUM_NC;

    gpio_num_t tilt_step = GPIO_NUM_NC;
    gpio_num_t tilt_dir = GPIO_NUM_NC;
    gpio_num_t tilt_enable = GPIO_NUM_NC;

    bool enable_active_low = true;
    bool pan_dir_inverted = false;
    bool tilt_dir_inverted = false;
};

class StepDirActuatorOutput final : public ActuatorOutput {
public:
    esp_err_t init(const StepDirPins &pins) noexcept;

    void apply(
        const ActuatorSetpoint &setpoint
    ) noexcept override;

    void stop() noexcept override;

private:
    void set_enabled(bool enabled) noexcept;
    StepDirPins pins_{};
    StepPulseEngine pan_step_engine_;
    StepPulseEngine tilt_step_engine_;
    bool initialized_ = false;
};

}  // namespace rcws