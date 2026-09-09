
/**start(100, 1000)
→ tạo 100 pulse
→ mỗi pulse cách nhau 1000 us
→ 1000 pulse/s **/

#pragma once

#include <cstdint>

#include "driver/gpio.h"
#include "driver/gptimer.h"
#include "esp_err.h"

namespace rcws {

class StepPulseEngine {
public:
    esp_err_t init(
        gpio_num_t step_pin,
        uint32_t pulse_width_us = 10
    ) noexcept;

    esp_err_t start(
        uint32_t pulse_count,
        uint32_t step_period_us
    ) noexcept;

    void stop() noexcept;

    bool busy() const noexcept;

private:
    static bool on_alarm(
        gptimer_handle_t timer,
        const gptimer_alarm_event_data_t *event_data,
        void *user_data
    );

    gptimer_handle_t timer_ = nullptr;

    gpio_num_t step_pin_ = GPIO_NUM_NC;

    volatile uint32_t pulses_remaining_ = 0;
    volatile bool step_high_ = false;
    volatile bool running_ = false;

    uint32_t pulse_width_us_ = 10;
    uint32_t step_period_us_ = 1000;
};

}  // namespace rcws


