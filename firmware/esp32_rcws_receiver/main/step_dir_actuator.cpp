#include "step_dir_actuator.hpp"

#include <cstdint>

#include "esp_log.h"

namespace {

constexpr const char *TAG = "step_dir";
constexpr uint32_t STEP_PULSE_WIDTH_US = 10;
constexpr uint32_t TEST_STEP_COUNT = 10;
constexpr uint32_t TEST_STEP_PERIOD_US = 1000;

bool is_valid_output(gpio_num_t pin)
{
    return GPIO_IS_VALID_OUTPUT_GPIO(pin);
}

uint32_t enable_level(
    bool enabled,
    bool active_low
)
{
    return (enabled != active_low) ? 1U : 0U;
}

}  // namespace

namespace rcws {

esp_err_t StepDirActuatorOutput::init(
    const StepDirPins &pins
) noexcept
{
    if (
        !is_valid_output(pins.pan_step) ||
        !is_valid_output(pins.pan_dir) ||
        !is_valid_output(pins.pan_enable) ||
        !is_valid_output(pins.tilt_step) ||
        !is_valid_output(pins.tilt_dir) ||
        !is_valid_output(pins.tilt_enable)
    ) {
        ESP_LOGE(TAG, "Invalid GPIO configuration");
        return ESP_ERR_INVALID_ARG;
    }

    pins_ = pins;

    const uint64_t output_mask =
    (1ULL << pins.pan_dir) |
    (1ULL << pins.pan_enable) |
    (1ULL << pins.tilt_dir) |
    (1ULL << pins.tilt_enable);

    gpio_config_t config{};
    config.pin_bit_mask = output_mask;
    config.mode = GPIO_MODE_OUTPUT;
    config.pull_up_en = GPIO_PULLUP_DISABLE;
    config.pull_down_en = GPIO_PULLDOWN_DISABLE;
    config.intr_type = GPIO_INTR_DISABLE;

    const esp_err_t result = gpio_config(&config);
    //constexpr uint32_t STEP_PULSE_WIDTH_US = 10;
    if (result != ESP_OK) {
        ESP_LOGE(
            TAG,
            "gpio_config failed: %s",
            esp_err_to_name(result)
        );

        return result;
    }

    // Safe startup state.

    gpio_set_level(pins_.pan_dir, 0);
    gpio_set_level(pins_.tilt_dir, 0);

    gpio_set_level(
        pins_.pan_enable,
        enable_level(false, pins_.enable_active_low)
    );

    gpio_set_level(
        pins_.tilt_enable,
        enable_level(false, pins_.enable_active_low)
    );

    esp_err_t err = pan_step_engine_.init(
    pins_.pan_step,
    STEP_PULSE_WIDTH_US
    );

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "PAN STEP engine init failed: %s",
            esp_err_to_name(err)
        );

        return err;
    }

    err = tilt_step_engine_.init(
        pins_.tilt_step,
        STEP_PULSE_WIDTH_US
    );

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "TILT STEP engine init failed: %s",
            esp_err_to_name(err)
        );

        return err;
    }

    initialized_ = true;

    ESP_LOGI(TAG,  "GPIO backend ready; STEP engines ready; outputs disabled");

    return ESP_OK;
}

void StepDirActuatorOutput::set_enabled(
    bool enabled
) noexcept
{
    if (!initialized_) {
        return;
    }

    const uint32_t level =
        enable_level(enabled, pins_.enable_active_low);

    gpio_set_level(pins_.pan_enable, level);
    gpio_set_level(pins_.tilt_enable, level);
}

void StepDirActuatorOutput::apply(
    const ActuatorSetpoint &setpoint
) noexcept
{
    if (!initialized_) {
        ESP_LOGE(TAG, "apply before init");
        return;
    }

    pan_step_engine_.stop();
    tilt_step_engine_.stop();
    
    if (setpoint.pan_milli != 0) {
        bool direction = setpoint.pan_milli > 0;

        if (pins_.pan_dir_inverted) {
            direction = !direction;
        }

        gpio_set_level(
            pins_.pan_dir,
            direction ? 1 : 0
        );
    }

    if (setpoint.tilt_milli != 0) {
        bool direction = setpoint.tilt_milli > 0;

        if (pins_.tilt_dir_inverted) {
            direction = !direction;
        }

        gpio_set_level(
            pins_.tilt_dir,
            direction ? 1 : 0
        );
    }

    set_enabled(true);

    if (setpoint.pan_milli != 0) {
    const esp_err_t err = pan_step_engine_.start(
        TEST_STEP_COUNT,
        TEST_STEP_PERIOD_US
    );

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "PAN STEP start failed: %s",
            esp_err_to_name(err)
        );

        stop();
        return;
    }
    }

    if (setpoint.tilt_milli != 0) {
        const esp_err_t err = tilt_step_engine_.start(
            TEST_STEP_COUNT,
            TEST_STEP_PERIOD_US
        );

        if (err != ESP_OK) {
            ESP_LOGE(
                TAG,
                "TILT STEP start failed: %s",
                esp_err_to_name(err)
            );

            stop();
            return;
        }
    }


    ESP_LOGI(
        TAG,
        "ARM pan=%d tilt=%d",
        static_cast<int>(setpoint.pan_milli),
        static_cast<int>(setpoint.tilt_milli)
    );
}

void StepDirActuatorOutput::stop() noexcept
{
    if (!initialized_) {
        return;
    }

    // STEP must always return to inactive state.
    // gpio_set_level(pins_.pan_step, 0);
    // gpio_set_level(pins_.tilt_step, 0);
    pan_step_engine_.stop();
    tilt_step_engine_.stop();

    set_enabled(false);

    ESP_LOGI(TAG, "STOP outputs disabled");
}

}  // namespace rcws