#include <errno.h>
#include <stdio.h>
#include <unistd.h>

#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

namespace {

constexpr size_t RX_CHUNK_SIZE = 64;
constexpr size_t RX_LINE_SIZE = 128;

constexpr UBaseType_t RECEIVER_TASK_PRIORITY = tskIDLE_PRIORITY + 1;
constexpr uint32_t RECEIVER_TASK_STACK_SIZE = 4096;

// Always yield for at least one RTOS tick when no serial data is available.
constexpr TickType_t RX_IDLE_DELAY_TICKS = 1;

const char *TAG = "rcws_rx";

void receiver_task(void *arg)
{
    (void)arg;

    unsigned char rx_buffer[RX_CHUNK_SIZE];
    char line[RX_LINE_SIZE];

    size_t line_length = 0;
    bool dropping_overflow_line = false;

    while (true) {
        const ssize_t received = read(
            STDIN_FILENO,
            rx_buffer,
            sizeof(rx_buffer)
        );

        // UART VFS stdin is non-blocking by default.
        if (received < 0) {
            if (errno != EAGAIN && errno != EWOULDBLOCK) {
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
            const char ch = static_cast<char>(rx_buffer[i]);

            // Ignore CR so both LF and CRLF terminals work.
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

            printf("RX_RAW:%s\n", line);

            line_length = 0;
            continue;
        }
            // Ignore the rest of an oversized packet until newline.
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
    // Avoid stdio buffering during serial command testing.
    setvbuf(stdin, nullptr, _IONBF, 0);
    setvbuf(stdout, nullptr, _IONBF, 0);

    ESP_LOGI(TAG, "RCWS raw receiver ready");

    const BaseType_t task_created = xTaskCreate(
        receiver_task,
        "rcws_receiver",
        RECEIVER_TASK_STACK_SIZE,
        nullptr,
        RECEIVER_TASK_PRIORITY,
        nullptr
    );

    if (task_created != pdPASS) {
        ESP_LOGE(TAG, "Failed to create receiver task");
    }
}