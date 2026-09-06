#include <errno.h>
#include <stdio.h>
#include <unistd.h>

#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define RX_CHUNK_SIZE 64
#define RX_LINE_SIZE 128

static const char *TAG = "rcws_rx";

static void receiver_task(void *arg)
{
    (void)arg;

    unsigned char rx_buffer[RX_CHUNK_SIZE];
    char line[RX_LINE_SIZE];
    size_t line_length = 0;

    while (true) {
        const ssize_t received = read(
            STDIN_FILENO,
            rx_buffer,
            sizeof(rx_buffer)
        );

        if (received < 0) {
            if (errno != EAGAIN && errno != EWOULDBLOCK) {
                ESP_LOGE(
                    TAG,
                    "stdin read failed: errno=%d",
                    errno
                );
            }

            vTaskDelay(pdMS_TO_TICKS(2));
            continue;
        }

        if (received == 0) {
            vTaskDelay(pdMS_TO_TICKS(2));
            continue;
        }

        for (ssize_t i = 0; i < received; ++i) {
            const char ch = (char)rx_buffer[i];

            if (ch == '\r') {
                continue;
            }

            if (ch == '\n') {
                line[line_length] = '\0';

                if (line_length > 0) {
                    printf("RX_RAW:%s\n", line);
                }

                line_length = 0;
                continue;
            }

            if (line_length < RX_LINE_SIZE - 1) {
                line[line_length++] = ch;
            } else {
                ESP_LOGW(TAG, "RX line overflow");
                line_length = 0;
            }
        }
    }
}

extern "C" void app_main(void)
{
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);

    ESP_LOGI(TAG, "RCWS raw receiver ready");

    xTaskCreate(
        receiver_task,
        "rcws_receiver",
        4096,
        NULL,
        5,
        NULL
    );
}