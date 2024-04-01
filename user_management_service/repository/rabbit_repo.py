import pika
from dependencies import RabbitMQClient, base_logger, settings
from fastapi import Depends
from pika.exceptions import AMQPError


class RabbitRepository:
    def __init__(self, client: RabbitMQClient = Depends()):
        self.client = client

    def send_message(self, routing_key: str, message: str):
        try:
            properties = pika.BasicProperties(
                content_type="application/json"
            )
            with self.client.get_connection().channel() as channel:
                channel.basic_publish(
                    exchange=settings.RABBITMQ_EXCHANGE,
                    routing_key=routing_key,
                    properties=properties,
                    body=message,
                )
        except AMQPError as e:
            base_logger.error(f"AMQP error during sending message to rabbitMQ: {e}")
            raise e
        except Exception as e:
            base_logger.error(f"Unknown error during connection to rabbitMQ: {e}")
            raise e
