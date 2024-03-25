import pika
from dependencies import base_logger, rabbit_client
from fastapi import Depends
from pika.channel import Channel
from pika.exceptions import AMQPError


class RabbitRepository:
    def __init__(self, channel: Channel = Depends(rabbit_client.get_channel)):
        self.channel = channel

    def send_message(self, routing_key: str, headers: dict, message: str):
        try:
            properties = pika.BasicProperties(
                headers=headers, content_type="application/json"
            )
            self.channel.basic_publish(
                exchange="",
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
