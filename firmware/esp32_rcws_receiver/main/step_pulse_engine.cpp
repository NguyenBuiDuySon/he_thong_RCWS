#include "step_pulse_engine.hpp"

#include "esp_log.h"

namespace {

constexpr const char *TAG = "step_pulse";

}  // namespace

namespace rcws {

esp_err_t StepPulseEngine::init(
    gpio_num_t step_pin,
    uint32_t pulse_width_us
) noexcept
{
    if (!GPIO_IS_VALID_OUTPUT_GPIO(step_pin)) {
        return ESP_ERR_INVALID_ARG;
    }

    if (pulse_width_us == 0) {
        return ESP_ERR_INVALID_ARG;
    }

    step_pin_ = step_pin;
    pulse_width_us_ = pulse_width_us;

    gpio_config_t io_config{};

    io_config.pin_bit_mask =
        1ULL << static_cast<uint32_t>(step_pin_);

    io_config.mode = GPIO_MODE_OUTPUT;
    io_config.pull_up_en = GPIO_PULLUP_DISABLE;
    io_config.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_config.intr_type = GPIO_INTR_DISABLE;

    esp_err_t result = gpio_config(&io_config);

    if (result != ESP_OK) {
        ESP_LOGE(
            TAG,
            "gpio_config failed: %s",
            esp_err_to_name(result)
        );
        return result;
    }

    result = gpio_set_level(step_pin_, 0);

    if (result != ESP_OK) {
        return result;
    }

    gptimer_config_t timer_config{};
    timer_config.clk_src = GPTIMER_CLK_SRC_DEFAULT;
    timer_config.direction = GPTIMER_COUNT_UP;
    timer_config.resolution_hz = 1'000'000;

    result =
        gptimer_new_timer(&timer_config, &timer_);

    if (result != ESP_OK) {
        ESP_LOGE(
            TAG,
            "gptimer_new_timer failed: %s",
            esp_err_to_name(result)
        );
        return result;
    }

    gptimer_event_callbacks_t callbacks{};
    callbacks.on_alarm = &StepPulseEngine::on_alarm;

    result = gptimer_register_event_callbacks(
        timer_,
        &callbacks,
        this
    );

    if (result != ESP_OK) {
        ESP_LOGE(
            TAG,
            "register callback failed: %s",
            esp_err_to_name(result)
        );
        return result;
    }

    result = gptimer_enable(timer_);

    if (result != ESP_OK) {
        ESP_LOGE(
            TAG,
            "gptimer_enable failed: %s",
            esp_err_to_name(result)
        );
        return result;
    }

    ESP_LOGI(
        TAG,
        "ready GPIO=%d pulse_width=%lu us",
        static_cast<int>(step_pin_),
        static_cast<unsigned long>(pulse_width_us_)
    );

    return ESP_OK;
}

esp_err_t StepPulseEngine::start(
    uint32_t pulse_count,
    uint32_t step_period_us
) noexcept
{
    if (
        timer_ == nullptr ||
        pulse_count == 0 ||
        step_period_us <= pulse_width_us_
    ) {
        return ESP_ERR_INVALID_ARG;
    }

    stop();

    pulses_remaining_ = pulse_count;
    step_period_us_ = step_period_us;
    step_high_ = false;
    running_ = true;

    gpio_set_level(step_pin_, 0);

    gptimer_alarm_config_t alarm_config{};
    alarm_config.reload_count = 0;
    //alarm_config.alarm_count = 1;
    alarm_config.alarm_count = pulse_width_us_;
    alarm_config.flags.auto_reload_on_alarm = false;

    esp_err_t result =
        gptimer_set_raw_count(timer_, 0);

    if (result != ESP_OK) {
        running_ = false;
        return result;
    }

    result =
        gptimer_set_alarm_action(
            timer_,
            &alarm_config
        );

    if (result != ESP_OK) {
        running_ = false;
        return result;
    }

    result = gptimer_start(timer_);

    if (result != ESP_OK) {
        running_ = false;
        return result;
    }

    return ESP_OK;
}

void StepPulseEngine::stop() noexcept
{
    if (timer_ != nullptr && running_) {
        gptimer_stop(timer_);
    }

    running_ = false;
    step_high_ = false;
    pulses_remaining_ = 0;

    if (step_pin_ != GPIO_NUM_NC) {
        gpio_set_level(step_pin_, 0);
    }
}

bool StepPulseEngine::busy() const noexcept
{
    return running_;
}

bool StepPulseEngine::on_alarm(
    gptimer_handle_t timer,
    const gptimer_alarm_event_data_t *event_data,
    void *user_data
)
{
    (void)event_data;

    auto *engine =
        static_cast<StepPulseEngine *>(user_data);

    if (
        engine == nullptr ||
        !engine->running_
    ) {
        return false;
    }

    gptimer_alarm_config_t next_alarm{};
    next_alarm.flags.auto_reload_on_alarm = false;

    if (!engine->step_high_) {
        // Rising edge.
        gpio_set_level(engine->step_pin_, 1);

        engine->step_high_ = true;

        next_alarm.alarm_count =
            event_data->count_value +
            engine->pulse_width_us_;
    } else {
        // Falling edge.
        gpio_set_level(engine->step_pin_, 0);

        engine->step_high_ = false;

        if (engine->pulses_remaining_ > 0) {
            const uint32_t remaining =
            engine->pulses_remaining_;
            engine->pulses_remaining_ =
            remaining - 1U;
        }

        if (engine->pulses_remaining_ == 0) {
            engine->running_ = false;
            gptimer_stop(timer);
            return false;
        }

        const uint32_t low_time_us =
            engine->step_period_us_ -
            engine->pulse_width_us_;

        next_alarm.alarm_count =
            event_data->count_value +
            low_time_us;
    }

    gptimer_set_alarm_action(
        timer,
        &next_alarm
    );

    return false;
}

}  // namespace rcws