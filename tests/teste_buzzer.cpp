#include <stdio.h>
#include <wiringPi.h>
#include <softTone.h>

#define BUZZER_PIN 4

int main()
{
    printf("Iniciando buzzer...\n");

    if (wiringPiSetupGpio() == -1)
    {
        printf("Erro ao inicializar wiringPi.\n");
        return 1;
    }

    pinMode(BUZZER_PIN, OUTPUT);

    if (softToneCreate(BUZZER_PIN) != 0)
    {
        printf("Erro ao configurar softTone.\n");
        return 1;
    }

    printf("1000 Hz\n");
    softToneWrite(BUZZER_PIN, 1000);
    delay(500);

    printf("1500 Hz\n");
    softToneWrite(BUZZER_PIN, 1500);
    delay(500);

    printf("2000 Hz\n");
    softToneWrite(BUZZER_PIN, 2000);
    delay(500);

    softToneWrite(BUZZER_PIN, 0);

    printf("Fim.\n");

    return 0;
}