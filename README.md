# Industrial Protocol Gateway

Шлюз: Modbus TCP / BACnet/IP / OPC UA -> единый JSON -> HTTPS REST.

## Требования
- Python 3.11+
- Linux рекомендуется для промышленной эксплуатации
- Для BACnet контейнеру нужен доступ к UDP/47808 и, при необходимости, host network.

## Запуск локально

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.yaml config.yaml
python main.py --config config.yaml
```

## Docker

```bash
docker compose up --build
```

## Формат конфигурации

`config.example.yaml` содержит примеры всех трёх протоколов.

### Автоопределение
Указать `protocol: auto`. Используются:
- `opc.tcp://...` -> OPC UA
- порт 502 -> Modbus TCP
- порт 47808 -> BACnet/IP

Это не DPI/сниффер. Для произвольного сырого TCP-потока гарантированное определение протокола невозможно.

## Modbus

Поддержаны:
- holding_registers
- input_registers
- coils
- discrete_inputs

Типы регистров:
- uint16
- int16
- uint32
- int32
- float32

Для 32-битных значений используется big-endian порядок байт внутри каждого регистра и порядок регистров `ABCD`. При другом byte/word order добавьте преобразователь в `protocols/modbus.py`.

## BACnet

Конфигурация каждой точки:
`address`, `object_type`, `instance`, `property`, `name`, `unit`.

Пример адреса устройства:
`192.168.1.20:47808`

## OPC UA

Для каждой точки задаётся `node_id`, например:
`ns=2;s=Motor.Speed`

## Надёжность

HTTPS publisher:
- таймаут
- повторные попытки
- exponential backoff
- локальный disk spool при недоступности HTTPS
- повторная отправка spool при восстановлении связи

Spool хранится в JSONL-файлах в `data/spool/`.

## Безопасность

Для прода:
- храните bearer token через переменную окружения
- используйте CA-сертификат вместо `verify_ssl: false`
- не публикуйте порт шлюза наружу без необходимости
- разделяйте OT/IT сети firewall/VLAN
- для OPC UA используйте security policy/certificates, если это требуется сервером
