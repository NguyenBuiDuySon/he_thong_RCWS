#include <cstdint>
#include <errno.h>
#include <stdio.h>
#include <unistd.h>

#include "esp_log.h"
#include "esp_timer.h"

#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"

#include "command_state.hpp"
#include "protocol.hpp"
#include "receiver_guard.hpp"

namespace {

constexpr size_t RX_CHUNK_SIZE = 64;
constexpr size_t RX_LINE_SIZE = 128;

constexpr UBaseType_t RECEIVER_TASK_PRIORITY =
    tskIDLE_PRIORITY + 1;

constexpr uint32_t RECEIVER_TASK_STACK_SIZE = 4096;

constexpr TickType_t RX_IDLE_DELAY_TICKS = 1;

constexpr std::int64_t COMMAND_TIMEOUT_US = 250'000;
constexpr UBaseType_t COMMAND_STATE_QUEUE_LENGTH = 1;
QueueHandle_t command_state_queue = nullptr;

const char *TAG = "rcws_rx";


void publish_command_state(
    const rcws::CommandState &state
)
{
    if (command_state_queue == nullptr) {
        ESP_LOGE(
            TAG,
            "Command state queue unavailable"
        );

        return;
    }

    if (
        xQueueOverwrite(
            command_state_queue,
            &state
        ) != pdPASS
    ) {
        ESP_LOGE(
            TAG,
            "Failed to publish command state"
        );

        return;
    }

    ESP_LOGI(
        TAG,
        "STATE seq=%u active=%d pan=%d tilt=%d reason=%s",
        static_cast<unsigned>(state.sequence),
        state.active ? 1 : 0,
        static_cast<int>(state.pan_milli),
        static_cast<int>(state.tilt_milli),
        rcws::stop_reason_name(state.stop_reason)
    );
}

void process_line(
      char *line,
    rcws::ReceiverGuard &receiver_guard,
    rcws::CommandStateMachine &command_state,
    bool &failsafe_stop
)
{
    rcws::WireCommand command{};
    rcws::ParseError error = rcws::ParseError::None;

    if (!rcws::decode_command(
            line,
            command,
            error
        )) {
        ESP_LOGW(
            TAG,
            "RX rejected: %s",
            rcws::parse_error_name(error)
        );

        return;
    }

    const std::int64_t now_us = esp_timer_get_time();

    const rcws::GuardDecision decision =
        receiver_guard.accept(
            command.sequence,
            command.active,
            now_us
        );

    if (decision != rcws::GuardDecision::accepted) {
        ESP_LOGW(
            TAG,
            "RX rejected: replay_or_stale seq=%u",
            static_cast<unsigned>(command.sequence)
        );

        return;
    }

    const rcws::CommandState &state =
    command_state.apply(
        command,
        now_us
    );

publish_command_state(state);

if (state.active) {
    if (failsafe_stop) {
        ESP_LOGI(
            TAG,
            "CONTROL_ACTIVE"
        );
    }

    failsafe_stop = false;
} else {
    if (!failsafe_stop) {
        ESP_LOGW(
            TAG,
            "CONTROL_STOP reason=inactive_command"
        );
    }

    failsafe_stop = true;
}


    ESP_LOGI(
        TAG,
        "RX_OK seq=%u active=%d pan=%d tilt=%d",
        static_cast<unsigned>(state.sequence),
        state.active ? 1 : 0,
        static_cast<int>(state.pan_milli),
        static_cast<int>(state.tilt_milli)
    );
}

void update_failsafe_state(
    rcws::ReceiverGuard &receiver_guard,
    rcws::CommandStateMachine &command_state,
    bool &failsafe_stop
)
{
    if (failsafe_stop) {
        return;
    }

    const std::int64_t now_us =
        esp_timer_get_time();

    if (!receiver_guard.should_stop(now_us)) {
        return;
    }

    const rcws::CommandState &state =
        command_state.stop(
            rcws::StopReason::timeout,
            now_us
        );

    publish_command_state(state);

    failsafe_stop = true;

    ESP_LOGW(
        TAG,
        "FAILSAFE_STOP reason=timeout"
    );
}


void receiver_task(void *arg)
{
    (void)arg;

    unsigned char rx_buffer[RX_CHUNK_SIZE];
    char line[RX_LINE_SIZE];

    size_t line_length = 0;
    bool dropping_overflow_line = false;

    rcws::ReceiverGuard receiver_guard{
        COMMAND_TIMEOUT_US
    };

    rcws::CommandStateMachine command_state;

    bool failsafe_stop = true;

    publish_command_state(
        command_state.current()
    );

    while (true) {

        update_failsafe_state(
        receiver_guard,
        command_state,
        failsafe_stop
        );

        const ssize_t received = read(
            STDIN_FILENO,
            rx_buffer,
            sizeof(rx_buffer)
        );

        if (received < 0) {
            if (
                errno != EAGAIN &&
                errno != EWOULDBLOCK
            ) {
                ESP_LOGE(
                    TAG,
                    "stdin read failed: errno=%d",
                    errno
                );
            }

            vTaskDelay(RX_IDLE_DELAY_TICKS);
            continue;
        }

        if (received == 0) {
            vTaskDelay(RX_IDLE_DELAY_TICKS);
            continue;
        }

        for (ssize_t i = 0; i < received; ++i) {
            const char ch =
                static_cast<char>(rx_buffer[i]);

            if (ch == '\r' || ch == '\n') {
                if (dropping_overflow_line) {
                    dropping_overflow_line = false;
                    line_length = 0;
                    continue;
                }

                if (line_length == 0) {
                    continue;
                }

                line[line_length] = '\0';

                process_line(
                     line,
                    receiver_guard,
                    command_state,
                    failsafe_stop
                );

                line_length = 0;
                continue;
            }

            if (dropping_overflow_line) {
                continue;
            }

            if (line_length < sizeof(line) - 1) {
                line[line_length++] = ch;
                continue;
            }

            ESP_LOGW(
                TAG,
                "RX line overflow; dropping packet"
            );

            line_length = 0;
            dropping_overflow_line = true;
        }
    }

}

}  // namespace

extern "C" void app_main(void)
{
    setvbuf(stdin, nullptr, _IONBF, 0);
    setvbuf(stdout, nullptr, _IONBF, 0);

    ESP_LOGI(
        TAG,
        "RCWS protocol receiver ready"
    );

    command_state_queue = xQueueCreate(
    COMMAND_STATE_QUEUE_LENGTH,
    sizeof(rcws::CommandState)
    );

    if (command_state_queue == nullptr) {
        ESP_LOGE(
            TAG,
            "Failed to create command state queue"
        );

        return;
    }

    const BaseType_t task_created = xTaskCreate(
        receiver_task,
        "rcws_receiver",
        RECEIVER_TASK_STACK_SIZE,
        nullptr,
        RECEIVER_TASK_PRIORITY,
        nullptr
    );

    if (task_created != pdPASS) {
        ESP_LOGE(
            TAG,
            "Failed to create receiver task"
        );
    }
}