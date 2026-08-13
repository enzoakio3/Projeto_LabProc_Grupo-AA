#include <stdio.h>
#include <wiringPi.h>
#include <softTone.h>

#define BUZZER_PIN 4

void stopBuzzer()
{
    softToneWrite(BUZZER_PIN, 0);
}

void successSound()
{
    printf("2000 Hz\n");

    softToneWrite(BUZZER_PIN, 2000);
    delay(1000);

    stopBuzzer();
}

void errorSound()
{
    printf("700 Hz\n");

    softToneWrite(BUZZER_PIN, 700);
    delay(1000);

    stopBuzzer();
}

void alertSound()
{
    printf("1500 Hz\n");

    for (int i = 0; i < 3; i++)
    {
        softToneWrite(BUZZER_PIN, 1500);
        delay(300);

        stopBuzzer();
        delay(150);
    }
}

int main()
{
    printf("Iniciando teste do buzzer...\n");

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

    printf("Som de sucesso...\n");
    successSound();

    delay(1000);

    printf("Som de erro...\n");
    errorSound();

    delay(1000);

    printf("Som de alerta...\n");
    alertSound();

    stopBuzzer();

    printf("Teste concluido.\n");

    return 0;
}